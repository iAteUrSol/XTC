"""
Sentiment Analysis Module for Crypto Tweets
Uses VADER sentiment analysis to classify tweet sentiment
"""
import re
import logging
from typing import Dict, Any, List, Tuple
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CryptoSentimentAnalyzer:
    """
    Analyzes sentiment of crypto-related tweets
    """
    
    def __init__(self):
        """
        Initialize the sentiment analyzer with VADER
        """
        self.analyzer = SentimentIntensityAnalyzer()
        
        # Crypto-specific sentiment words to augment VADER lexicon
        self.crypto_lexicon = {
            # Bullish terms (positive)
            "hodl": 2.0,
            "mooning": 3.0,
            "to the moon": 3.0,
            "bullish": 2.5,
            "diamond hands": 2.0,
            "buy the dip": 1.5,
            "fomo": 1.0,
            "rocket": 2.0,
            "🚀": 2.5,
            "🌕": 2.0,
            "💎": 1.5,
            "🙌": 1.0,
            "accumulate": 1.0,
            "support": 0.5,
            "breakout": 1.8,
            "adoption": 1.5,
            "bullrun": 2.0,
            "all time high": 2.0,
            "ath": 2.0,
            "beat the market": 1.5,
            
            # Bearish terms (negative)
            "bearish": -2.5,
            "rugpull": -3.0,
            "dumping": -2.0,
            "crash": -2.5,
            "paper hands": -1.5,
            "fud": -2.0,
            "ponzi": -3.0,
            "scam": -3.0,
            "shitcoin": -2.5,
            "rekt": -2.5,
            "liquidated": -2.0,
            "sell off": -1.5,
            "bearmarket": -2.0,
            "bubble": -1.5,
            "correction": -1.0,
            "dead cat bounce": -1.5,
            "📉": -2.0,
            "🧸": -2.0,
            "💩": -2.0
        }
        
        # Update VADER lexicon with crypto terms
        for word, score in self.crypto_lexicon.items():
            self.analyzer.lexicon[word] = score
            
    def analyze_tweet(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze sentiment of a tweet and classify as bullish, bearish, or neutral
        
        Args:
            tweet: Dictionary containing tweet data
            
        Returns:
            Updated tweet dictionary with sentiment data
        """
        text = tweet.get('text', '')
        if not text:
            logger.warning("Empty tweet text for sentiment analysis")
            return self._add_default_sentiment(tweet)
            
        # Preprocess text
        processed_text = self._preprocess_text(text)
        
        # Get sentiment scores
        sentiment = self.analyzer.polarity_scores(processed_text)
        
        # Add sentiment data to tweet
        tweet['sentiment'] = {
            'compound': sentiment['compound'],
            'positive': sentiment['pos'],
            'negative': sentiment['neg'],
            'neutral': sentiment['neu']
        }
        
        # Classify sentiment
        if sentiment['compound'] >= 0.05:
            tweet['sentiment']['classification'] = 'bullish'
        elif sentiment['compound'] <= -0.05:
            tweet['sentiment']['classification'] = 'bearish'
        else:
            tweet['sentiment']['classification'] = 'neutral'
            
        # Extract mentioned cryptocurrencies
        tweet['mentioned_cryptos'] = self._extract_crypto_mentions(text)
        
        return tweet
        
    def analyze_tweets(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze sentiment of multiple tweets
        
        Args:
            tweets: List of tweet dictionaries
            
        Returns:
            Updated list of tweets with sentiment data
        """
        analyzed_tweets = []
        
        for tweet in tweets:
            analyzed_tweet = self.analyze_tweet(tweet)
            analyzed_tweets.append(analyzed_tweet)
            
        # Get sentiment statistics
        stats = self._get_sentiment_stats(analyzed_tweets)
        logger.info(f"Sentiment stats: {stats['bullish']} bullish, {stats['bearish']} bearish, {stats['neutral']} neutral")
        
        return analyzed_tweets
        
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess tweet text for sentiment analysis
        
        Args:
            text: Raw tweet text
            
        Returns:
            Preprocessed text
        """
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'https?://\S+|www\.\S+', '', text)
        
        # Remove user mentions
        text = re.sub(r'@\w+', '', text)
        
        # Replace hashtags with plain text
        text = re.sub(r'#(\w+)', r'\1', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
        
    def _extract_crypto_mentions(self, text: str) -> List[str]:
        """
        Extract mentioned cryptocurrencies from tweet text
        
        Args:
            text: Tweet text
            
        Returns:
            List of mentioned cryptocurrencies
        """
        # Common cryptocurrencies to check for
        cryptos = {
            'bitcoin': ['bitcoin', 'btc', '₿', 'xbt'],
            'ethereum': ['ethereum', 'eth', 'ether'],
            'solana': ['solana', 'sol'],
            'cardano': ['cardano', 'ada'],
            'binance': ['binance', 'bnb', 'bsc'],
            'ripple': ['ripple', 'xrp'],
            'dogecoin': ['dogecoin', 'doge'],
            'polkadot': ['polkadot', 'dot'],
            'avalanche': ['avalanche', 'avax'],
            'shiba inu': ['shiba', 'shib'],
            'litecoin': ['litecoin', 'ltc'],
            'chainlink': ['chainlink', 'link'],
            'polygon': ['polygon', 'matic'],
            'tron': ['tron', 'trx'],
            'uniswap': ['uniswap', 'uni'],
            'cosmos': ['cosmos', 'atom']
        }
        
        # Check for crypto mentions in text
        mentioned = []
        text_lower = text.lower()
        
        for crypto, keywords in cryptos.items():
            if any(keyword in text_lower for keyword in keywords):
                mentioned.append(crypto)
                
        # Look for cashtags like $BTC, $ETH
        cashtags = re.findall(r'\$([A-Za-z0-9]+)', text)
        for tag in cashtags:
            tag_lower = tag.lower()
            
            # Map common ticker symbols to crypto names
            if tag_lower == 'btc' and 'bitcoin' not in mentioned:
                mentioned.append('bitcoin')
            elif tag_lower == 'eth' and 'ethereum' not in mentioned:
                mentioned.append('ethereum')
            elif tag_lower == 'sol' and 'solana' not in mentioned:
                mentioned.append('solana')
            elif tag_lower == 'ada' and 'cardano' not in mentioned:
                mentioned.append('cardano')
            # Add the tag itself if not mapped
            elif tag_lower not in [item for sublist in cryptos.values() for item in sublist]:
                mentioned.append(tag.lower())
                
        return mentioned
        
    def _get_sentiment_stats(self, tweets: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Get statistics on sentiment classifications
        
        Args:
            tweets: List of analyzed tweets
            
        Returns:
            Dictionary with counts of bullish, bearish, and neutral tweets
        """
        stats = {
            'bullish': 0,
            'bearish': 0,
            'neutral': 0
        }
        
        for tweet in tweets:
            classification = tweet.get('sentiment', {}).get('classification', 'neutral')
            stats[classification] += 1
            
        return stats
        
    def _add_default_sentiment(self, tweet: Dict[str, Any]) -> Dict[str, Any]:
        """
        Add default neutral sentiment to a tweet
        
        Args:
            tweet: Tweet dictionary
            
        Returns:
            Tweet with default sentiment data
        """
        tweet['sentiment'] = {
            'compound': 0.0,
            'positive': 0.0,
            'negative': 0.0,
            'neutral': 1.0,
            'classification': 'neutral'
        }
        tweet['mentioned_cryptos'] = []
        
        return tweet
        
    def get_trending_cryptos(self, tweets: List[Dict[str, Any]]) -> List[Tuple[str, int, float]]:
        """
        Get trending cryptocurrencies from analyzed tweets
        
        Args:
            tweets: List of analyzed tweets
            
        Returns:
            List of tuples containing (crypto_name, mention_count, avg_sentiment)
        """
        # Count mentions and sum sentiment
        crypto_data = {}
        
        for tweet in tweets:
            for crypto in tweet.get('mentioned_cryptos', []):
                if crypto not in crypto_data:
                    crypto_data[crypto] = {
                        'count': 0,
                        'sentiment_sum': 0.0
                    }
                    
                crypto_data[crypto]['count'] += 1
                crypto_data[crypto]['sentiment_sum'] += tweet.get('sentiment', {}).get('compound', 0.0)
                
        # Calculate average sentiment and create trending list
        trending = []
        
        for crypto, data in crypto_data.items():
            avg_sentiment = data['sentiment_sum'] / data['count'] if data['count'] > 0 else 0.0
            trending.append((crypto, data['count'], avg_sentiment))
            
        # Sort by mention count (descending)
        trending.sort(key=lambda x: x[1], reverse=True)
        
        return trending

# Example usage
if __name__ == "__main__":
    # Example tweet data
    example_tweets = [
        {"text": "Bitcoin is going to the moon! #BTC 🚀"},
        {"text": "Bearish on ETH right now, might crash soon. #crypto #ethereum"},
        {"text": "Just bought more $SOL. Solana ecosystem looking strong!"},
        {"text": "The market is down today. #crypto #bitcoin #eth"},
        {"text": "This #NFT project is a complete scam. Avoid at all costs."}
    ]
    
    # Analyze sentiment
    analyzer = CryptoSentimentAnalyzer()
    analyzed_tweets = analyzer.analyze_tweets(example_tweets)
    
    # Print results
    for i, tweet in enumerate(analyzed_tweets, 1):
        print(f"\n--- Tweet {i} ---")
        print(f"Text: {tweet['text']}")
        print(f"Sentiment: {tweet['sentiment']['classification']} (Score: {tweet['sentiment']['compound']:.2f})")
        print(f"Mentioned cryptos: {tweet['mentioned_cryptos']}")
        
    # Get trending cryptos
    trending = analyzer.get_trending_cryptos(analyzed_tweets)
    print("\n--- Trending Cryptos ---")
    for crypto, count, sentiment in trending:
        sentiment_label = "bullish" if sentiment >= 0.05 else "bearish" if sentiment <= -0.05 else "neutral"
        print(f"{crypto}: {count} mentions, {sentiment_label} sentiment ({sentiment:.2f})")
