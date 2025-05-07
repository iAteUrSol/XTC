# XTC - Crypto Twitter Sentinel

A tool to monitor and analyze crypto-related content from your Twitter feed, providing sentiment analysis, trend detection, and customizable alerts.

## Features

- 🤖 Automatic monitoring of your Twitter feed for crypto-related content
- 📊 Sentiment analysis to classify tweets as bullish, bearish, or neutral
- 🔍 Trend detection to identify emerging topics and coins
- 🚨 Configurable alerts for significant market movements
- 💬 Chat interface to ask questions about the crypto Twitter landscape

## Technology Stack

- **Backend**: Python with FastAPI
- **Scraping**: Playwright (browser automation)
- **Frontend**: React with Tailwind CSS
- **Database**: SQLite
- **Analysis**: VADER Sentiment Analysis

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- A Twitter account with access to crypto content

### Installation

1. Clone this repository:
```bash
git clone https://github.com/iAteUrSol/XTC.git
cd XTC
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
playwright install firefox
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

4. Set up environment variables in a `.env` file:
```
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
```

5. Run the initial setup:
```bash
python setup.py
```

### Running the Application

1. Start the backend server:
```bash
python app.py
```

2. In a new terminal, start the frontend:
```bash
cd frontend
npm start
```

3. Open your browser and navigate to `http://localhost:3000`

## Deployment on Replit

This application is designed to be deployable on Replit:

1. Create a new Replit project and import from GitHub
2. Set up the necessary environment variables in Replit Secrets
3. Install dependencies using the Shell
4. Click Run to start the application

## License

MIT
