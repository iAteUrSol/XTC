"""
Setup script for XTC - Crypto Twitter Sentinel
Initializes Twitter credentials, installs Playwright browsers, and creates directories
"""
import os
import sys
import asyncio
import logging
from getpass import getpass
from pathlib import Path
from twitter_scraper import TwitterScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """
    Main setup function
    """
    print("=" * 60)
    print(" XTC - Crypto Twitter Sentinel Setup")
    print("=" * 60)
    print("\nThis script will help you set up the XTC application.")
    print("It will guide you through setting Twitter credentials and initializing components.")
    
    # Check if .env file exists
    env_file = Path(".env")
    if env_file.exists():
        print("\n.env file already exists. Do you want to recreate it? (y/n)")
        choice = input("> ").strip().lower()
        
        if choice != 'y':
            print("Keeping existing .env file.")
        else:
            await create_env_file()
    else:
        await create_env_file()
        
    # Install browsers for Playwright
    print("\nInstalling browsers for Playwright...")
    try:
        import playwright
        os.system("playwright install firefox")
        print("Firefox browser installed successfully.")
    except Exception as e:
        print(f"Error installing browsers: {e}")
        print("Please install Playwright browsers manually with: playwright install firefox")
        
    # Create data directories
    print("\nCreating data directories...")
    os.makedirs("data", exist_ok=True)
    
    print("\nSetup complete! You can now run the application with:")
    print("python app.py")
    
    print("\nTo test Twitter login, would you like to try it now? (y/n)")
    choice = input("> ").strip().lower()
    
    if choice == 'y':
        await test_twitter_login()
    else:
        print("Skipping Twitter login test.")
        
    print("\nSetup process complete.")

async def create_env_file():
    """
    Create .env file with Twitter credentials
    """
    print("\nPlease enter your Twitter credentials:")
    
    # Get username/email
    print("\nEnter your Twitter username, email, or phone number:")
    username = input("> ").strip()
    
    # Get password
    print("Enter your Twitter password:")
    password = getpass("> ")
    
    # Create .env file
    with open(".env", "w") as f:
        f.write(f"TWITTER_USERNAME={username}\n")
        f.write(f"TWITTER_PASSWORD={password}\n")
        
    print("\n.env file created successfully.")

async def test_twitter_login():
    """
    Test Twitter login with provided credentials
    """
    print("\nTesting Twitter login...")
    
    try:
        # Initialize Twitter scraper
        scraper = TwitterScraper()
        await scraper.initialize()
        
        # Try to login
        success = await scraper.login()
        
        if success:
            print("Twitter login successful!")
            # Save cookies
            print("Cookies saved for future sessions.")
        else:
            print("Twitter login failed. Please check your credentials.")
            
        # Close browser
        await scraper.close()
        
    except Exception as e:
        print(f"Error testing Twitter login: {e}")
        print("Please check your credentials and try again.")

if __name__ == "__main__":
    asyncio.run(main())
