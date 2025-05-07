// DOM Elements
const refreshBtn = document.getElementById('refresh-btn');
const liveSummary = document.getElementById('live-summary');
const tweetsContainer = document.getElementById('tweets-container');
const alertsContainer = document.getElementById('alerts-container');
const loadMoreBtn = document.getElementById('load-more-btn');
const chatInput = document.getElementById('chat-message-input');
const sendMessageBtn = document.getElementById('send-message-btn');
const chatMessages = document.getElementById('chat-messages');
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');
const filterBtns = document.querySelectorAll('.filter-btn');

// State
let currentPage = 1;
let currentLimit = 10;
let currentSentimentFilter = 'all';
let isLoading = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Fetch initial data
    fetchSummaries();
    fetchTweets();
    fetchAlerts();
    
    // Set up event listeners
    setupEventListeners();
});

// Set up event listeners
function setupEventListeners() {
    // Refresh button
    refreshBtn.addEventListener('click', handleRefresh);
    
    // Load more button
    loadMoreBtn.addEventListener('click', handleLoadMore);
    
    // Chat input
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            handleSendMessage();
        }
    });
    
    // Send message button
    sendMessageBtn.addEventListener('click', handleSendMessage);
    
    // Tab buttons
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabName = btn.getAttribute('data-tab');
            switchTab(tabName);
        });
    });
    
    // Filter buttons
    filterBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const sentiment = btn.getAttribute('data-sentiment');
            applySentimentFilter(sentiment);
        });
    });
}

// Handle refresh
async function handleRefresh() {
    refreshBtn.disabled = true;
    refreshBtn.textContent = 'Refreshing...';
    
    try {
        const response = await fetch('/api/refresh', {
            method: 'POST'
        });
        
        if (response.ok) {
            // Wait a moment for the backend to process
            setTimeout(() => {
                fetchSummaries();
                fetchTweets(true);
                fetchAlerts();
                
                refreshBtn.textContent = 'Feed Refreshed!';
                setTimeout(() => {
                    refreshBtn.textContent = 'Refresh Feed';
                    refreshBtn.disabled = false;
                }, 2000);
            }, 3000);
        } else {
            throw new Error('Failed to refresh feed');
        }
    } catch (error) {
        console.error('Error refreshing feed:', error);
        refreshBtn.textContent = 'Refresh Failed';
        setTimeout(() => {
            refreshBtn.textContent = 'Refresh Feed';
            refreshBtn.disabled = false;
        }, 2000);
    }
}

// Handle load more
function handleLoadMore() {
    currentPage++;
    fetchTweets(false, currentPage, currentLimit);
}

// Handle send message
async function handleSendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) return;
    
    // Add user message to chat
    addChatMessage(message, 'user');
    
    // Clear input
    chatInput.value = '';
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        if (response.ok) {
            const data = await response.json();
            addChatMessage(data.response, 'bot');
        } else {
            throw new Error('Failed to get response');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        addChatMessage('Sorry, I encountered an error processing your request. Please try again.', 'bot');
    }
}

// Add chat message
function addChatMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);
    
    const paragraph = document.createElement('p');
    // Split by new lines and create paragraphs
    text.split('\n\n').forEach((part, i) => {
        if (i > 0) {
            paragraph.appendChild(document.createElement('br'));
            paragraph.appendChild(document.createElement('br'));
        }
        paragraph.appendChild(document.createTextNode(part));
    });
    
    messageDiv.appendChild(paragraph);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Switch tab
function switchTab(tabName) {
    // Update active tab button
    tabBtns.forEach(btn => {
        if (btn.getAttribute('data-tab') === tabName) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update active tab content
    tabContents.forEach(content => {
        if (content.id === tabName) {
            content.classList.add('active');
        } else {
            content.classList.remove('active');
        }
    });
}

// Apply sentiment filter
function applySentimentFilter(sentiment) {
    currentSentimentFilter = sentiment;
    
    // Update active filter button
    filterBtns.forEach(btn => {
        if (btn.getAttribute('data-sentiment') === sentiment) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Reset pagination
    currentPage = 1;
    
    // Fetch tweets with filter
    fetchTweets(true);
}

// Fetch summaries
async function fetchSummaries() {
    try {
        const response = await fetch('/api/summaries?limit=1');
        
        if (response.ok) {
            const data = await response.json();
            
            if (data && data.length > 0) {
                const summary = data[0];
                renderSummary(summary);
            } else {
                liveSummary.innerHTML = `<p>No summaries available yet. Try refreshing the feed.</p>`;
            }
        } else {
            throw new Error('Failed to fetch summaries');
        }
    } catch (error) {
        console.error('Error fetching summaries:', error);
        liveSummary.innerHTML = `<p>Error loading summary. Please try again.</p>`;
    }
}

// Fetch tweets
async function fetchTweets(reset = false, page = 1, limit = 10) {
    if (isLoading) return;
    
    isLoading = true;
    
    if (reset) {
        tweetsContainer.innerHTML = `<p class="loading">Loading tweets...</p>`;
        currentPage = 1;
    }
    
    try {
        let url = `/api/tweets?limit=${limit}&page=${page}`;
        
        if (currentSentimentFilter !== 'all') {
            url += `&sentiment=${currentSentimentFilter}`;
        }
        
        const response = await fetch(url);
        
        if (response.ok) {
            const data = await response.json();
            
            if (reset) {
                tweetsContainer.innerHTML = '';
            }
            
            if (data && data.length > 0) {
                renderTweets(data);
                loadMoreBtn.style.display = 'block';
            } else {
                if (reset) {
                    tweetsContainer.innerHTML = `<p>No tweets available for the selected filter.</p>`;
                }
                loadMoreBtn.style.display = 'none';
            }
        } else {
            throw new Error('Failed to fetch tweets');
        }
    } catch (error) {
        console.error('Error fetching tweets:', error);
        
        if (reset) {
            tweetsContainer.innerHTML = `<p>Error loading tweets. Please try again.</p>`;
        }
    } finally {
        isLoading = false;
    }
}

// Fetch alerts
async function fetchAlerts() {
    try {
        const response = await fetch('/api/alerts');
        
        if (response.ok) {
            const data = await response.json();
            
            alertsContainer.innerHTML = '';
            
            if (data && data.length > 0) {
                renderAlerts(data);
            } else {
                alertsContainer.innerHTML = `<p>No alerts available yet.</p>`;
            }
        } else {
            throw new Error('Failed to fetch alerts');
        }
    } catch (error) {
        console.error('Error fetching alerts:', error);
        alertsContainer.innerHTML = `<p>Error loading alerts. Please try again.</p>`;
    }
}

// Render summary
function renderSummary(summary) {
    liveSummary.innerHTML = `
        <h3>${summary.title}</h3>
        <p>${formatContent(summary.content)}</p>
        <div class="summary-footer">
            <small>Last updated: ${formatDate(summary.timestamp)}</small>
        </div>
    `;
}

// Render tweets
function renderTweets(tweets) {
    tweets.forEach(tweet => {
        const tweetElement = document.createElement('div');
        tweetElement.classList.add('tweet-card');
        tweetElement.classList.add(tweet.sentiment.classification);
        
        tweetElement.innerHTML = `
            <div class="tweet-header">
                <div>
                    <span class="tweet-user">${tweet.user_name}</span>
                    <span class="tweet-handle">@${tweet.user_handle}</span>
                </div>
                <span class="tweet-timestamp">${formatDate(tweet.timestamp)}</span>
            </div>
            <div class="tweet-text">${formatContent(tweet.text)}</div>
            <div class="tweet-footer">
                <div class="tweet-sentiment">
                    <span class="sentiment-badge ${tweet.sentiment.classification}">${tweet.sentiment.classification}</span>
                    ${tweet.mentioned_cryptos.length > 0 ? `<span>${tweet.mentioned_cryptos.join(', ')}</span>` : ''}
                </div>
                <div class="tweet-metrics">
                    <span>❤️ ${tweet.likes}</span>
                    <span>🔁 ${tweet.retweets}</span>
                </div>
            </div>
        `;
        
        tweetsContainer.appendChild(tweetElement);
    });
}

// Render alerts
function renderAlerts(alerts) {
    alerts.forEach(alert => {
        const alertElement = document.createElement('div');
        alertElement.classList.add('alert-card');
        
        // Generate importance dots
        let importanceDots = '';
        for (let i = 1; i <= 5; i++) {
            importanceDots += `<div class="importance-dot${i <= alert.importance ? ' active' : ''}"></div>`;
        }
        
        alertElement.innerHTML = `
            <div class="alert-header">
                <div class="alert-title">${alert.title}</div>
                <div class="alert-type">${alert.alert_type}</div>
            </div>
            <div class="alert-description">${formatContent(alert.description)}</div>
            <div class="alert-footer">
                <div class="alert-importance">
                    ${importanceDots}
                </div>
                <span>${formatDate(alert.timestamp)}</span>
            </div>
        `;
        
        alertsContainer.appendChild(alertElement);
    });
}

// Format content
function formatContent(content) {
    if (!content) return '';
    
    // Convert new lines to HTML line breaks
    return content.replace(/\n/g, '<br>');
}

// Format date
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    
    // Check if the date is valid
    if (isNaN(date.getTime())) {
        return dateString;
    }
    
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    // Format relative time
    if (diffSec < 60) {
        return 'just now';
    } else if (diffMin < 60) {
        return `${diffMin}m ago`;
    } else if (diffHour < 24) {
        return `${diffHour}h ago`;
    } else if (diffDay < 7) {
        return `${diffDay}d ago`;
    } else {
        // Format as date
        return date.toLocaleDateString();
    }
}
