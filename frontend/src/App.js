import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Header from './components/Header';
import Summary from './components/Summary';
import FeedContainer from './components/FeedContainer';
import ChatPanel from './components/ChatPanel';

function App() {
  const [summaries, setSummaries] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [tweets, setTweets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState(null);

  // API base URL - change this to your deployment URL when deployed
  const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // Fetch data from the API
  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Fetch summaries
      const summariesResponse = await axios.get(`${API_BASE_URL}/api/summaries?limit=1`);
      setSummaries(summariesResponse.data);
      
      // Fetch alerts
      const alertsResponse = await axios.get(`${API_BASE_URL}/api/alerts?limit=10`);
      setAlerts(alertsResponse.data);
      
      // Fetch tweets
      const tweetsResponse = await axios.get(`${API_BASE_URL}/api/tweets?limit=20`);
      setTweets(tweetsResponse.data);
      
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("Failed to fetch data. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  // Trigger a feed refresh
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      
      // Call the refresh endpoint
      await axios.post(`${API_BASE_URL}/api/refresh`);
      
      // Wait a moment for the backend to process
      setTimeout(() => {
        fetchData();
        setRefreshing(false);
      }, 5000); // Wait 5 seconds for processing
      
    } catch (err) {
      console.error("Error refreshing feed:", err);
      setError("Failed to refresh feed. Please try again later.");
      setRefreshing(false);
    }
  };

  // Mark an alert as read
  const markAlertRead = async (alertId) => {
    try {
      await axios.post(`${API_BASE_URL}/api/alerts/${alertId}/read`);
      
      // Update local state by marking the alert as read
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? { ...alert, is_read: true } : alert
      ));
      
    } catch (err) {
      console.error("Error marking alert as read:", err);
    }
  };

  // Chat with the AI
  const sendChatMessage = async (message) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/api/chat`, { message });
      return response.data.response;
    } catch (err) {
      console.error("Error sending chat message:", err);
      return "Sorry, I couldn't process your message. Please try again.";
    }
  };

  // Fetch data on component mount
  useEffect(() => {
    fetchData();
    
    // Set up a timer to refresh data every 5 minutes
    const interval = setInterval(() => {
      fetchData();
    }, 300000); // 5 minutes
    
    // Clean up interval on unmount
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      <Header onRefresh={handleRefresh} refreshing={refreshing} />
      
      <main className="container mx-auto px-4 py-8">
        {error && (
          <div className="bg-red-500 text-white p-4 rounded-lg mb-6">
            {error}
          </div>
        )}
        
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2">
              {/* Latest Summary */}
              {summaries.length > 0 && (
                <Summary summary={summaries[0]} />
              )}
              
              {/* Feed */}
              <FeedContainer 
                alerts={alerts.filter(a => !a.is_read)} 
                tweets={tweets}
                onMarkAlertRead={markAlertRead}
              />
            </div>
            
            {/* Chat Panel */}
            <div className="lg:col-span-1">
              <ChatPanel sendMessage={sendChatMessage} />
            </div>
          </div>
        )}
      </main>
      
      <footer className="bg-slate-800 py-4 mt-12">
        <div className="container mx-auto px-4 text-center text-slate-400">
          <p>XTC - Crypto Twitter Sentinel &copy; {new Date().getFullYear()}</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
