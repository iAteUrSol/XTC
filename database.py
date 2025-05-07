"""
Database module for storing and retrieving tweet data
Uses SQLite with SQLAlchemy ORM
"""
import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create SQLAlchemy base class
Base = declarative_base()

class Tweet(Base):
    """
    SQLAlchemy model for storing tweet data
    """
    __tablename__ = 'tweets'
    
    id = Column(Integer, primary_key=True)
    user_name = Column(String(255))
    user_handle = Column(String(255))
    text = Column(Text)
    comment_count = Column(String(50))
    retweet_count = Column(String(50))
    like_count = Column(String(50))
    timestamp = Column(String(50))
    scrape_time = Column(DateTime)
    has_media = Column(Boolean, default=False)
    
    # Sentiment data
    sentiment_compound = Column(Float)
    sentiment_positive = Column(Float)
    sentiment_negative = Column(Float)
    sentiment_neutral = Column(Float)
    sentiment_classification = Column(String(20))
    
    # Crypto-specific data
    is_crypto = Column(Boolean, default=True)
    mentioned_cryptos = Column(Text)  # Stored as JSON string
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Tweet model to dictionary
        
        Returns:
            Dictionary representation of the tweet
        """
        return {
            'id': self.id,
            'user_name': self.user_name,
            'user_handle': self.user_handle,
            'text': self.text,
            'comment_count': self.comment_count,
            'retweet_count': self.retweet_count,
            'like_count': self.like_count,
            'timestamp': self.timestamp,
            'scrape_time': self.scrape_time.isoformat() if self.scrape_time else None,
            'has_media': self.has_media,
            'sentiment': {
                'compound': self.sentiment_compound,
                'positive': self.sentiment_positive,
                'negative': self.sentiment_negative,
                'neutral': self.sentiment_neutral,
                'classification': self.sentiment_classification
            },
            'is_crypto': self.is_crypto,
            'mentioned_cryptos': json.loads(self.mentioned_cryptos) if self.mentioned_cryptos else []
        }

class Alert(Base):
    """
    SQLAlchemy model for storing crypto alerts
    """
    __tablename__ = 'alerts'
    
    id = Column(Integer, primary_key=True)
    alert_type = Column(String(50))  # 'trend', 'sentiment', 'volume', etc.
    title = Column(String(255))
    description = Column(Text)
    crypto = Column(String(50))  # Which crypto is this alert about
    importance = Column(Integer)  # 1 (low) to 5 (high)
    timestamp = Column(DateTime)
    is_read = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Alert model to dictionary
        
        Returns:
            Dictionary representation of the alert
        """
        return {
            'id': self.id,
            'alert_type': self.alert_type,
            'title': self.title,
            'description': self.description,
            'crypto': self.crypto,
            'importance': self.importance,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'is_read': self.is_read
        }

class Summary(Base):
    """
    SQLAlchemy model for storing feed summaries
    """
    __tablename__ = 'summaries'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    content = Column(Text)
    sentiment_overview = Column(Text)  # JSON string of sentiment statistics
    trending_cryptos = Column(Text)  # JSON string of trending cryptos
    timestamp = Column(DateTime)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Summary model to dictionary
        
        Returns:
            Dictionary representation of the summary
        """
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'sentiment_overview': json.loads(self.sentiment_overview) if self.sentiment_overview else {},
            'trending_cryptos': json.loads(self.trending_cryptos) if self.trending_cryptos else [],
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

class DatabaseManager:
    """
    Manager for database operations
    """
    
    def __init__(self, db_path: str = 'crypto_twitter.db'):
        """
        Initialize database connection
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.Session = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(self.engine)
        logger.info(f"Database initialized at {db_path}")
        
    def store_tweets(self, tweets: List[Dict[str, Any]]) -> int:
        """
        Store tweets in database
        
        Args:
            tweets: List of tweet dictionaries
            
        Returns:
            Number of tweets stored
        """
        session = self.Session()
        try:
            count = 0
            for tweet_data in tweets:
                # Check if tweet already exists
                text = tweet_data.get('text', '')
                user_handle = tweet_data.get('userHandle', '')
                
                existing = session.query(Tweet).filter(
                    Tweet.text == text,
                    Tweet.user_handle == user_handle
                ).first()
                
                if existing:
                    logger.debug(f"Tweet already exists: {text[:30]}...")
                    continue
                
                # Create new tweet
                tweet = Tweet(
                    user_name=tweet_data.get('userName', ''),
                    user_handle=tweet_data.get('userHandle', ''),
                    text=tweet_data.get('text', ''),
                    comment_count=tweet_data.get('commentCount', '0'),
                    retweet_count=tweet_data.get('retweetCount', '0'),
                    like_count=tweet_data.get('likeCount', '0'),
                    timestamp=tweet_data.get('timestamp', ''),
                    scrape_time=datetime.fromisoformat(tweet_data.get('scrape_time', datetime.now().isoformat())),
                    has_media=tweet_data.get('hasMedia', False),
                    sentiment_compound=tweet_data.get('sentiment', {}).get('compound', 0.0),
                    sentiment_positive=tweet_data.get('sentiment', {}).get('positive', 0.0),
                    sentiment_negative=tweet_data.get('sentiment', {}).get('negative', 0.0),
                    sentiment_neutral=tweet_data.get('sentiment', {}).get('neutral', 0.0),
                    sentiment_classification=tweet_data.get('sentiment', {}).get('classification', 'neutral'),
                    is_crypto=tweet_data.get('is_crypto', True),
                    mentioned_cryptos=json.dumps(tweet_data.get('mentioned_cryptos', []))
                )
                
                session.add(tweet)
                count += 1
                
            session.commit()
            logger.info(f"Stored {count} new tweets in database")
            return count
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error storing tweets: {e}")
            return 0
            
        finally:
            session.close()
            
    def get_tweets(self, 
                   limit: int = 100, 
                   only_crypto: bool = True,
                   sentiment: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get tweets from database
        
        Args:
            limit: Maximum number of tweets to return
            only_crypto: Only return crypto-related tweets
            sentiment: Filter by sentiment classification
            
        Returns:
            List of tweet dictionaries
        """
        session = self.Session()
        try:
            query = session.query(Tweet)
            
            if only_crypto:
                query = query.filter(Tweet.is_crypto == True)
                
            if sentiment:
                query = query.filter(Tweet.sentiment_classification == sentiment)
                
            tweets = query.order_by(Tweet.scrape_time.desc()).limit(limit).all()
            
            return [tweet.to_dict() for tweet in tweets]
            
        except Exception as e:
            logger.error(f"Error getting tweets: {e}")
            return []
            
        finally:
            session.close()
            
    def create_alert(self, 
                     alert_type: str,
                     title: str,
                     description: str,
                     crypto: str = '',
                     importance: int = 3) -> Optional[int]:
        """
        Create a new alert
        
        Args:
            alert_type: Type of alert
            title: Alert title
            description: Alert description
            crypto: Cryptocurrency involved
            importance: Alert importance (1-5)
            
        Returns:
            ID of created alert, or None if failed
        """
        session = self.Session()
        try:
            alert = Alert(
                alert_type=alert_type,
                title=title,
                description=description,
                crypto=crypto,
                importance=importance,
                timestamp=datetime.now(),
                is_read=False
            )
            
            session.add(alert)
            session.commit()
            
            logger.info(f"Created alert: {title}")
            return alert.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating alert: {e}")
            return None
            
        finally:
            session.close()
            
    def get_alerts(self, limit: int = 20, include_read: bool = False) -> List[Dict[str, Any]]:
        """
        Get alerts from database
        
        Args:
            limit: Maximum number of alerts to return
            include_read: Include already read alerts
            
        Returns:
            List of alert dictionaries
        """
        session = self.Session()
        try:
            query = session.query(Alert)
            
            if not include_read:
                query = query.filter(Alert.is_read == False)
                
            alerts = query.order_by(Alert.timestamp.desc()).limit(limit).all()
            
            return [alert.to_dict() for alert in alerts]
            
        except Exception as e:
            logger.error(f"Error getting alerts: {e}")
            return []
            
        finally:
            session.close()
            
    def mark_alert_read(self, alert_id: int) -> bool:
        """
        Mark an alert as read
        
        Args:
            alert_id: ID of the alert to mark
            
        Returns:
            True if successful, False otherwise
        """
        session = self.Session()
        try:
            alert = session.query(Alert).filter(Alert.id == alert_id).first()
            
            if not alert:
                logger.warning(f"Alert with ID {alert_id} not found")
                return False
                
            alert.is_read = True
            session.commit()
            
            logger.info(f"Marked alert {alert_id} as read")
            return True
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error marking alert as read: {e}")
            return False
            
        finally:
            session.close()
            
    def create_summary(self, 
                       title: str,
                       content: str,
                       sentiment_overview: Dict[str, Any],
                       trending_cryptos: List[Tuple[str, int, float]]) -> Optional[int]:
        """
        Create a new summary
        
        Args:
            title: Summary title
            content: Summary content
            sentiment_overview: Dictionary of sentiment statistics
            trending_cryptos: List of trending cryptocurrencies
            
        Returns:
            ID of created summary, or None if failed
        """
        session = self.Session()
        try:
            # Convert trending_cryptos to JSON-friendly format
            trending_cryptos_json = [
                {
                    'name': crypto,
                    'mentions': count,
                    'sentiment': sentiment
                }
                for crypto, count, sentiment in trending_cryptos
            ]
            
            summary = Summary(
                title=title,
                content=content,
                sentiment_overview=json.dumps(sentiment_overview),
                trending_cryptos=json.dumps(trending_cryptos_json),
                timestamp=datetime.now()
            )
            
            session.add(summary)
            session.commit()
            
            logger.info(f"Created summary: {title}")
            return summary.id
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating summary: {e}")
            return None
            
        finally:
            session.close()
            
    def get_summaries(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get summaries from database
        
        Args:
            limit: Maximum number of summaries to return
            
        Returns:
            List of summary dictionaries
        """
        session = self.Session()
        try:
            summaries = session.query(Summary).order_by(Summary.timestamp.desc()).limit(limit).all()
            
            return [summary.to_dict() for summary in summaries]
            
        except Exception as e:
            logger.error(f"Error getting summaries: {e}")
            return []
            
        finally:
            session.close()
            
    def get_trending_cryptos(self) -> List[Dict[str, Any]]:
        """
        Get trending cryptocurrencies from the latest summary
        
        Returns:
            List of trending cryptocurrencies
        """
        session = self.Session()
        try:
            latest_summary = session.query(Summary).order_by(Summary.timestamp.desc()).first()
            
            if not latest_summary or not latest_summary.trending_cryptos:
                return []
                
            trending_cryptos = json.loads(latest_summary.trending_cryptos)
            
            return trending_cryptos
            
        except Exception as e:
            logger.error(f"Error getting trending cryptos: {e}")
            return []
            
        finally:
            session.close()


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = DatabaseManager()
    
    # Example tweet data
    example_tweets = [
        {
            "userName": "CryptoUser1",
            "userHandle": "cryptouser1",
            "text": "Bitcoin is going to the moon! #BTC 🚀",
            "commentCount": "5",
            "retweetCount": "10",
            "likeCount": "25",
            "timestamp": "2025-05-01T12:34:56Z",
            "scrape_time": datetime.now().isoformat(),
            "hasMedia": False,
            "sentiment": {
                "compound": 0.8,
                "positive": 0.9,
                "negative": 0.0,
                "neutral": 0.1,
                "classification": "bullish"
            },
            "is_crypto": True,
            "mentioned_cryptos": ["bitcoin"]
        }
    ]
    
    # Store tweets
    db.store_tweets(example_tweets)
    
    # Create an alert
    db.create_alert(
        alert_type="trend",
        title="Bitcoin trending upwards",
        description="Bitcoin mentions are increasing with positive sentiment",
        crypto="bitcoin",
        importance=4
    )
    
    # Create a summary
    db.create_summary(
        title="Morning Crypto Report",
        content="Bitcoin and Ethereum are trending with positive sentiment today.",
        sentiment_overview={"bullish": 10, "bearish": 2, "neutral": 5},
        trending_cryptos=[
            ("bitcoin", 15, 0.8),
            ("ethereum", 8, 0.6),
            ("solana", 4, 0.2)
        ]
    )
    
    # Retrieve data
    tweets = db.get_tweets(limit=5)
    alerts = db.get_alerts()
    summaries = db.get_summaries()
    
    print(f"Retrieved {len(tweets)} tweets, {len(alerts)} alerts, {len(summaries)} summaries")
