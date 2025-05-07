"""
Twitter Feed Scraper for Crypto Analysis
Uses Playwright to scrape the user's feed and extract crypto-related content
"""
import os
import json
import asyncio
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from playwright.async_api import async_playwright, Page, Browser, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TwitterScraper:
    """
    A class to scrape Twitter feed and extract crypto-related content
    using Playwright browser automation
    """
    
    def __init__(self, 
                 username: Optional[str] = None, 
                 password: Optional[str] = None,
                 cookies_path: str = "twitter_cookies.json",
                 crypto_keywords: Optional[List[str]] = None):
        """
        Initialize the Twitter scraper
        
        Args:
            username: Twitter username/email/phone
            password: Twitter password
            cookies_path: Path to save/load Twitter session cookies
            crypto_keywords: List of crypto-related keywords to filter tweets
        """
        self.username = username or os.getenv("TWITTER_USERNAME")
        self.password = password or os.getenv("TWITTER_PASSWORD")
        self.cookies_path = cookies_path
        
        # Default crypto keywords if none provided
        self.crypto_keywords = crypto_keywords or [
            "bitcoin", "btc", "ethereum", "eth", "solana", "sol", 
            "crypto", "blockchain", "nft", "defi", "web3", "altcoin",
            "token", "binance", "coinbase", "$", "bull", "bear"
        ]
        
        # Playwright objects
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        
    async def initialize(self) -> None:
        """
        Initialize the Playwright browser and load cookies if available
        """
        logger.info("Initializing Playwright browser")
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.firefox.launch(headless=True)
        self.context = await self.browser.new_context()
        
        # Load cookies if available
        if os.path.exists(self.cookies_path):
            logger.info(f"Loading cookies from {self.cookies_path}")
            try:
                with open(self.cookies_path, "r") as f:
                    cookies = json.load(f)
                await self.context.add_cookies(cookies)
            except Exception as e:
                logger.error(f"Error loading cookies: {e}")
        
        self.page = await self.context.new_page()
        
    async def login(self) -> bool:
        """
        Log in to Twitter and save cookies
        
        Returns:
            bool: True if login was successful, False otherwise
        """
        if not self.username or not self.password:
            logger.error("Twitter credentials not provided")
            return False
            
        logger.info("Logging in to Twitter")
        try:
            # Navigate to login page
            await self.page.goto("https://twitter.com/login")
            await self.page.wait_for_load_state("networkidle")
            
            # Check if we're already logged in
            if await self._is_logged_in():
                logger.info("Already logged in")
                return True
                
            # Enter username
            logger.info("Entering username")
            await self.page.fill('input[autocomplete="username"]', self.username)
            await self.page.click('div[role="button"]:has-text("Next")')
            await self.page.wait_for_timeout(2000)  # Wait for transition
            
            # Handle phone verification if required
            if await self.page.is_visible('input[data-testid="ocfEnterPhoneNumberForm-phone-number-input"]'):
                logger.warning("Phone verification required. Consider using cookies instead.")
                return False
                
            # Enter password
            logger.info("Entering password")
            await self.page.fill('input[name="password"]', self.password)
            await self.page.click('div[data-testid="LoginForm_Login_Button"]')
            
            # Wait for login to complete
            await self.page.wait_for_timeout(5000)  # Wait for login to process
            
            # Check if login was successful
            if await self._is_logged_in():
                logger.info("Login successful")
                # Save cookies for future sessions
                cookies = await self.context.cookies()
                with open(self.cookies_path, "w") as f:
                    json.dump(cookies, f)
                logger.info(f"Cookies saved to {self.cookies_path}")
                return True
            else:
                logger.error("Login failed")
                return False
                
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False
            
    async def _is_logged_in(self) -> bool:
        """
        Check if the user is logged in
        
        Returns:
            bool: True if logged in, False otherwise
        """
        try:
            # Check for typical elements only visible when logged in
            logged_in = await self.page.is_visible('a[aria-label="Profile"]')
            return logged_in
        except Exception:
            return False
            
    async def scrape_feed(self, scroll_count: int = 5) -> List[Dict[str, Any]]:
        """
        Scrape tweets from the home timeline
        
        Args:
            scroll_count: Number of times to scroll down to load more tweets
            
        Returns:
            List of dictionaries containing tweet data
        """
        logger.info("Scraping Twitter feed")
        
        # Navigate to home timeline
        await self.page.goto("https://twitter.com/home")
        await self.page.wait_for_selector('article[data-testid="tweet"]', timeout=30000)
        
        # Scroll down to load more tweets
        for i in range(scroll_count):
            logger.info(f"Scrolling feed ({i+1}/{scroll_count})")
            await self.page.evaluate("window.scrollBy(0, 1000)")
            await asyncio.sleep(2)  # Wait for new tweets to load
        
        # Extract all tweets
        logger.info("Extracting tweets")
        raw_tweets = await self._extract_tweets()
        
        # Filter tweets for crypto-related content
        crypto_tweets = self._filter_crypto_tweets(raw_tweets)
        logger.info(f"Found {len(crypto_tweets)} crypto-related tweets out of {len(raw_tweets)} total tweets")
        
        return crypto_tweets
        
    async def _extract_tweets(self) -> List[Dict[str, Any]]:
        """
        Extract tweets from the page
        
        Returns:
            List of dictionaries containing tweet data
        """
        # Using JavaScript to extract tweet data
        tweets = await self.page.evaluate("""
            () => {
                const tweetElements = document.querySelectorAll('article[data-testid="tweet"]');
                return Array.from(tweetElements).map(tweet => {
                    // Extract username and display name
                    const userElement = tweet.querySelector('div[data-testid="User-Name"]');
                    const userName = userElement ? userElement.querySelector('a[role="link"] span')?.textContent : 'Unknown';
                    const userHandle = userElement ? userElement.querySelector('a[role="link"] div[dir="ltr"] span')?.textContent : 'Unknown';
                    
                    // Extract tweet text
                    const textElement = tweet.querySelector('div[data-testid="tweetText"]');
                    const text = textElement ? textElement.innerText : '';
                    
                    // Extract engagement metrics
                    const commentCount = tweet.querySelector('div[data-testid="reply"] span[data-testid="app-text-transition-container"]')?.textContent || '0';
                    const retweetCount = tweet.querySelector('div[data-testid="retweet"] span[data-testid="app-text-transition-container"]')?.textContent || '0';
                    const likeCount = tweet.querySelector('div[data-testid="like"] span[data-testid="app-text-transition-container"]')?.textContent || '0';
                    
                    // Extract timestamp
                    const timeElement = tweet.querySelector('time');
                    const timestamp = timeElement ? timeElement.getAttribute('datetime') : null;
                    
                    // Extract URLs from the tweet
                    const links = Array.from(tweet.querySelectorAll('a[role="link"]'))
                        .filter(link => link.href && link.href.startsWith('https://t.co/'))
                        .map(link => link.href);
                    
                    // Extract any media
                    const hasMedia = !!tweet.querySelector('div[data-testid="tweetPhoto"], div[data-testid="videoPlayer"]');
                    
                    return { 
                        userName,
                        userHandle,
                        text,
                        commentCount,
                        retweetCount,
                        likeCount,
                        timestamp,
                        links,
                        hasMedia
                    };
                });
            }
        """)
        
        # Add timestamp for when we scraped this
        now = datetime.now().isoformat()
        for tweet in tweets:
            tweet['scrape_time'] = now
            
        return tweets
        
    def _filter_crypto_tweets(self, tweets: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter tweets for crypto-related content
        
        Args:
            tweets: List of tweets to filter
            
        Returns:
            List of crypto-related tweets
        """
        crypto_tweets = []
        
        for tweet in tweets:
            text = tweet.get('text', '').lower()
            
            # Check if any crypto keyword is in the tweet
            if any(keyword.lower() in text for keyword in self.crypto_keywords):
                # Add a flag indicating this is crypto-related
                tweet['is_crypto'] = True
                crypto_tweets.append(tweet)
                
        return crypto_tweets
        
    async def close(self) -> None:
        """
        Close browser and playwright
        """
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# Example usage
async def main():
    scraper = TwitterScraper()
    await scraper.initialize()
    
    # Try to use cookies, or login if needed
    if not await scraper._is_logged_in():
        success = await scraper.login()
        if not success:
            print("Login failed")
            await scraper.close()
            return
    
    # Scrape crypto tweets
    tweets = await scraper.scrape_feed(scroll_count=3)
    
    # Print results
    print(f"Found {len(tweets)} crypto-related tweets")
    for i, tweet in enumerate(tweets, 1):
        print(f"\n--- Tweet {i} ---")
        print(f"User: {tweet['userName']} (@{tweet['userHandle']})")
        print(f"Text: {tweet['text']}")
        print(f"Likes: {tweet['likeCount']}, Retweets: {tweet['retweetCount']}")
        print(f"Timestamp: {tweet['timestamp']}")
    
    await scraper.close()

if __name__ == "__main__":
    asyncio.run(main())
