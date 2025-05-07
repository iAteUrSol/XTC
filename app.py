"""
Main application module for XTC (Crypto Twitter Sentinel)
Connects all components and provides API endpoints
"""
import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our components
from twitter_scraper import TwitterScraper
from sentiment_analyzer import CryptoSentimentAnalyzer
from database import DatabaseManager

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize components
db = DatabaseManager()
analyzer = CryptoSentimentAnalyzer()
scraper = None  # Will be initialized in startup event

# Initialize FastAPI app
app = FastAPI(
    title="XTC - Crypto Twitter Sentinel",
    description="Monitor and analyze crypto-related content from your Twitter feed",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API
class SummaryResponse(BaseModel):
    id: Optional[int] = None
    title: str
    content: str
    sentiment_overview: Dict[str, Any]
    trending_cryptos: List[Dict[str, Any]]
    timestamp: Optional[str] = None

class AlertResponse(BaseModel):
    id: Optional[int] = None
    alert_type: str
    title: str
    description: str
    crypto: str
    importance: int
    timestamp: Optional[str] = None
    is_read: bool = False

class TweetResponse(BaseModel):
    id: Optional[int] = None
    user_name: str
    user_handle: str
    text: str
    sentiment: Dict[str, Any]
    mentioned_cryptos: List[str]
    timestamp: Optional[str] = None
    likes: str
    retweets: str

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

# Background task for scraping and analyzing tweets
async def scrape_and_analyze():
    """
    Background task to scrape Twitter feed, analyze sentiment, and store results
    """
    global scraper
    
    if not scraper:
        logger.error("Scraper not initialized")
        return
        
    try:
        logger.info("Starting tweet scraping")
        
        # Scrape tweets
        tweets = await scraper.scrape_feed(scroll_count=5)
        
        if not tweets:
            logger.warning("No tweets found")
            return
            
        logger.info(f"Scraped {len(tweets)} tweets")
        
        # Analyze sentiment
        analyzed_tweets = analyzer.analyze_tweets(tweets)
        logger.info(f"Analyzed {len(analyzed_tweets)} tweets")
        
        # Store tweets in database
        stored_count = db.store_tweets(analyzed_tweets)
        logger.info(f"Stored {stored_count} new tweets")
        
        # Get trending cryptocurrencies
        trending_cryptos = analyzer.get_trending_cryptos(analyzed_tweets)
        
        # Get sentiment statistics
        bullish_count = sum(1 for t in analyzed_tweets if t.get('sentiment', {}).get('classification') == 'bullish')
        bearish_count = sum(1 for t in analyzed_tweets if t.get('sentiment', {}).get('classification') == 'bearish')
        neutral_count = sum(1 for t in analyzed_tweets if t.get('sentiment', {}).get('classification') == 'neutral')
        
        sentiment_overview = {
            'bullish': bullish_count,
            'bearish': bearish_count,
            'neutral': neutral_count,
            'total': len(analyzed_tweets)
        }
        
        # Create a summary
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"Crypto Twitter Summary {current_date}"
        
        # Generate summary content
        bullish_pct = (bullish_count / len(analyzed_tweets)) * 100 if analyzed_tweets else 0
        bearish_pct = (bearish_count / len(analyzed_tweets)) * 100 if analyzed_tweets else 0
        
        # Determine overall sentiment
        if bullish_pct > bearish_pct + 10:
            overall = "bullish"
        elif bearish_pct > bullish_pct + 10:
            overall = "bearish"
        else:
            overall = "neutral"
            
        # Create content
        content = f"The crypto Twitter sentiment is currently {overall}. "
        content += f"Out of {len(analyzed_tweets)} crypto-related tweets, "
        content += f"{bullish_count} ({bullish_pct:.1f}%) are bullish, "
        content += f"{bearish_count} ({bearish_pct:.1f}%) are bearish, and "
        content += f"{neutral_count} ({100 - bullish_pct - bearish_pct:.1f}%) are neutral.\n\n"
        
        # Add trending cryptos to content
        if trending_cryptos:
            content += "Trending cryptocurrencies:\n"
            for crypto, count, sentiment in trending_cryptos[:5]:
                sentiment_label = "bullish" if sentiment >= 0.05 else "bearish" if sentiment <= -0.05 else "neutral"
                content += f"- {crypto.title()}: {count} mentions, {sentiment_label} sentiment\n"
        
        # Create summary in database
        summary_id = db.create_summary(
            title=title,
            content=content,
            sentiment_overview=sentiment_overview,
            trending_cryptos=trending_cryptos
        )
        
        if summary_id:
            logger.info(f"Created summary with ID {summary_id}")
        
        # Check for notable events that should trigger alerts
        # 1. Sudden shift in sentiment
        if bullish_pct > 70 and len(analyzed_tweets) > 10:
            db.create_alert(
                alert_type="sentiment",
                title="Strong bullish sentiment detected",
                description=f"Crypto Twitter sentiment is highly bullish ({bullish_pct:.1f}% positive) based on {len(analyzed_tweets)} recent tweets.",
                crypto="",
                importance=4
            )
            
        elif bearish_pct > 70 and len(analyzed_tweets) > 10:
            db.create_alert(
                alert_type="sentiment",
                title="Strong bearish sentiment detected",
                description=f"Crypto Twitter sentiment is highly bearish ({bearish_pct:.1f}% negative) based on {len(analyzed_tweets)} recent tweets.",
                crypto="",
                importance=4
            )
            
        # 2. Trending cryptocurrencies
        if trending_cryptos:
            top_crypto, top_count, top_sentiment = trending_cryptos[0]
            
            if top_count > 5:
                sentiment_label = "bullish" if top_sentiment >= 0.05 else "bearish" if top_sentiment <= -0.05 else "neutral"
                
                db.create_alert(
                    alert_type="trend",
                    title=f"{top_crypto.title()} is trending",
                    description=f"{top_crypto.title()} is trending with {top_count} mentions and {sentiment_label} sentiment.",
                    crypto=top_crypto,
                    importance=3
                )
                
        logger.info("Tweet analysis and processing complete")
        
    except Exception as e:
        logger.error(f"Error in background task: {e}")

# API Endpoints
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "message": "XTC - Crypto Twitter Sentinel API",
        "version": "1.0.0",
        "endpoints": [
            "/api/summaries",
            "/api/alerts",
            "/api/tweets",
            "/api/refresh",
            "/api/chat"
        ]
    }

@app.get("/api/summaries", response_model=List[SummaryResponse])
async def get_summaries(limit: int = Query(10, ge=1, le=50)):
    """
    Get feed summaries
    """
    summaries = db.get_summaries(limit=limit)
    return summaries

@app.get("/api/alerts", response_model=List[AlertResponse])
async def get_alerts(limit: int = Query(20, ge=1, le=100), include_read: bool = False):
    """
    Get alerts
    """
    alerts = db.get_alerts(limit=limit, include_read=include_read)
    return alerts

@app.post("/api/alerts/{alert_id}/read")
async def mark_alert_read(alert_id: int):
    """
    Mark an alert as read
    """
    success = db.mark_alert_read(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
        
    return {"message": "Alert marked as read"}

@app.get("/api/tweets", response_model=List[TweetResponse])
async def get_tweets(
    limit: int = Query(50, ge=1, le=200),
    only_crypto: bool = True,
    sentiment: Optional[str] = None
):
    """
    Get tweets
    """
    tweets = db.get_tweets(limit=limit, only_crypto=only_crypto, sentiment=sentiment)
    
    # Convert to response model format
    response_tweets = []
    for tweet in tweets:
        response_tweets.append({
            "id": tweet.get("id"),
            "user_name": tweet.get("user_name", ""),
            "user_handle": tweet.get("user_handle", ""),
            "text": tweet.get("text", ""),
            "sentiment": tweet.get("sentiment", {}),
            "mentioned_cryptos": tweet.get("mentioned_cryptos", []),
            "timestamp": tweet.get("timestamp"),
            "likes": tweet.get("like_count", "0"),
            "retweets": tweet.get("retweet_count", "0")
        })
    
    return response_tweets

@app.post("/api/refresh")
async def refresh_feed(background_tasks: BackgroundTasks):
    """
    Manually trigger a feed refresh
    """
    background_tasks.add_task(scrape_and_analyze)
    return {"message": "Feed refresh started"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI about crypto Twitter trends
    """
    message = request.message.strip()
    
    if not message:
        return {"response": "Please provide a message to chat about crypto Twitter trends."}
        
    # Get the latest summary and alerts
    summaries = db.get_summaries(limit=1)
    alerts = db.get_alerts(limit=5)
    
    # Get some recent tweets
    bullish_tweets = db.get_tweets(limit=10, only_crypto=True, sentiment="bullish")
    bearish_tweets = db.get_tweets(limit=10, only_crypto=True, sentiment="bearish")
    
    # Get trending cryptos
    trending_cryptos = db.get_trending_cryptos()
    
    # Simple rule-based chat responses
    response = ""
    
    # Check for specific queries
    if any(keyword in message.lower() for keyword in ["trend", "trending", "popular"]):
        if trending_cryptos:
            response = "Currently trending cryptocurrencies:\n\n"
            for crypto in trending_cryptos[:5]:
                sentiment_label = "bullish" if crypto.get("sentiment", 0) >= 0.05 else "bearish" if crypto.get("sentiment", 0) <= -0.05 else "neutral"
                response += f"- {crypto.get('name', '').title()}: {crypto.get('mentions', 0)} mentions, {sentiment_label} sentiment\n"
        else:
            response = "No trending cryptocurrencies detected in recent tweets."
            
    elif any(keyword in message.lower() for keyword in ["sentiment", "mood", "feeling"]):
        if summaries:
            summary = summaries[0]
            sentiment_overview = summary.get("sentiment_overview", {})
            bullish = sentiment_overview.get("bullish", 0)
            bearish = sentiment_overview.get("bearish", 0)
            neutral = sentiment_overview.get("neutral", 0)
            total = bullish + bearish + neutral
            
            if total > 0:
                bullish_pct = (bullish / total) * 100
                bearish_pct = (bearish / total) * 100
                
                if bullish_pct > bearish_pct + 10:
                    overall = "bullish"
                elif bearish_pct > bullish_pct + 10:
                    overall = "bearish"
                else:
                    overall = "neutral"
                    
                response = f"The overall sentiment on crypto Twitter is currently {overall}. "
                response += f"Out of {total} analyzed tweets, {bullish_pct:.1f}% are bullish, "
                response += f"{bearish_pct:.1f}% are bearish, and {100-bullish_pct-bearish_pct:.1f}% are neutral."
            else:
                response = "Not enough data to determine the current sentiment on crypto Twitter."
        else:
            response = "No recent sentiment analysis available."
            
    elif any(keyword in message.lower() for keyword in ["bull", "bullish", "positive"]):
        if bullish_tweets:
            response = "Recent bullish tweets:\n\n"
            for tweet in bullish_tweets[:3]:
                response += f"@{tweet.get('user_handle', '')}: {tweet.get('text', '')[:100]}...\n\n"
        else:
            response = "No recent bullish tweets found."
            
    elif any(keyword in message.lower() for keyword in ["bear", "bearish", "negative"]):
        if bearish_tweets:
            response = "Recent bearish tweets:\n\n"
            for tweet in bearish_tweets[:3]:
                response += f"@{tweet.get('user_handle', '')}: {tweet.get('text', '')[:100]}...\n\n"
        else:
            response = "No recent bearish tweets found."
            
    elif any(crypto in message.lower() for crypto in ["bitcoin", "btc"]):
        # Get Bitcoin-specific insights
        bitcoin_tweets = [t for t in db.get_tweets(limit=20) if "bitcoin" in t.get("mentioned_cryptos", [])]
        
        if bitcoin_tweets:
            bullish_count = sum(1 for t in bitcoin_tweets if t.get("sentiment", {}).get("classification") == "bullish")
            bearish_count = sum(1 for t in bitcoin_tweets if t.get("sentiment", {}).get("classification") == "bearish")
            
            if bullish_count > bearish_count:
                sentiment = "bullish"
            elif bearish_count > bullish_count:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
                
            response = f"Bitcoin sentiment is currently {sentiment} with {len(bitcoin_tweets)} recent mentions. "
            
            if bitcoin_tweets:
                response += f"Here's a sample tweet: @{bitcoin_tweets[0].get('user_handle', '')}: {bitcoin_tweets[0].get('text', '')[:100]}..."
        else:
            response = "No recent Bitcoin-related tweets found."
            
    elif any(crypto in message.lower() for crypto in ["ethereum", "eth"]):
        # Get Ethereum-specific insights
        eth_tweets = [t for t in db.get_tweets(limit=20) if "ethereum" in t.get("mentioned_cryptos", [])]
        
        if eth_tweets:
            bullish_count = sum(1 for t in eth_tweets if t.get("sentiment", {}).get("classification") == "bullish")
            bearish_count = sum(1 for t in eth_tweets if t.get("sentiment", {}).get("classification") == "bearish")
            
            if bullish_count > bearish_count:
                sentiment = "bullish"
            elif bearish_count > bullish_count:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
                
            response = f"Ethereum sentiment is currently {sentiment} with {len(eth_tweets)} recent mentions. "
            
            if eth_tweets:
                response += f"Here's a sample tweet: @{eth_tweets[0].get('user_handle', '')}: {eth_tweets[0].get('text', '')[:100]}..."
        else:
            response = "No recent Ethereum-related tweets found."
            
    elif any(alert_word in message.lower() for alert_word in ["alert", "notification", "important"]):
        if alerts:
            response = "Recent alerts:\n\n"
            for alert in alerts[:3]:
                response += f"- {alert.get('title', '')}: {alert.get('description', '')}\n\n"
        else:
            response = "No recent alerts found."
            
    elif "help" in message.lower():
        response = (
            "I can help you analyze crypto Twitter trends. Try asking me about:\n\n"
            "- Current sentiment\n"
            "- Trending cryptocurrencies\n"
            "- Recent bullish or bearish tweets\n"
            "- Specific cryptocurrencies like Bitcoin or Ethereum\n"
            "- Recent alerts or notifications\n\n"
            "You can also use the refresh button to update the feed data."
        )
        
    else:
        if summaries:
            response = summaries[0].get("content", "")
        else:
            response = "No recent data available. Try refreshing the feed."
    
    return {"response": response}

@app.on_event("startup")
async def startup_event():
    """
    Initialize components on startup
    """
    global scraper
    
    try:
        # Initialize Twitter scraper
        scraper = TwitterScraper()
        await scraper.initialize()
        
        # Check if we need to log in
        if not await scraper._is_logged_in():
            success = await scraper.login()
            if not success:
                logger.error("Twitter login failed")
                
        # Run initial scraping
        asyncio.create_task(scrape_and_analyze())
        
        logger.info("Application startup complete")
        
    except Exception as e:
        logger.error(f"Error during startup: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Clean up resources on shutdown
    """
    global scraper
    
    if scraper:
        await scraper.close()
        
    logger.info("Application shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
