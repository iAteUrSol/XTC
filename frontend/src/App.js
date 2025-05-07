import React, { useState, useEffect } from 'react';
import './App.css';

// Import components
import Header from './components/Header';
import LiveSummary from './components/LiveSummary';
import FeedContainer from './components/FeedContainer';
import ChatBox from './components/ChatBox';

// Import API service
import { 
  getSummaries, 
  getAlerts, 
  getTweets, 
  refreshFeed, 
  sendChatMessage 
} from './services/api';

function App() {
  // State for data
  const [summaries, setSummaries] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [tweets, setTweets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Load initial data
  useEffect(() => {
    fetchData();
  }, []);

  // Function to fetch all data
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const [summariesData, alertsData, tweetsData] = await Promise.all([
        getSummaries(),
        getAlerts(),
        getTweets()
      ]);
      
      setSummaries(summariesData);
      setAlerts(alertsData);
      setTweets(tweetsData);
    } catch (err) {
      console.error('Error fetching data:', err);
      setError('Failed to load data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  // Function to refresh feed data
  const handleRefresh = async () => {
    setRefreshing(true);
    
    try {
      await refreshFeed();
      // Give the backend some time to process
      setTimeout(fetchData, 5000);
    } catch (err) {
      console.error('Error refreshing feed:', err);
      setError('Failed to refresh feed. Please try again later.');
    } finally {
      setRefreshing(false);
    }
  };

  // Function to handle chat messages
  const handleChatMessage = async (message) => {
    try {
      const response = await sendChatMessage(message);
      return response;
    } catch (err) {
      console.error('Error sending chat message:', err);
      return { response: 'Sorry, there was an error processing your request.' };
    }
  };

  return (
    <div className="min-h-screen bg-background text-text-primary">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : error ? (
          <div className="bg-red-500 text-white p-4 rounded">
            {error}
          </div>
        ) : (
          <>
            <LiveSummary 
              summary={summaries[0]} 
              onRefresh={handleRefresh} 
              refreshing={refreshing} 
            />
            
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mt-8">
              <div className="lg:col-span-2">
                <FeedContainer 
                  summaries={summaries} 
                  alerts={alerts} 
                  tweets={tweets} 
                />
              </div>
              
              <div className="lg:col-span-1">
                <ChatBox onSendMessage={handleChatMessage} />
              </div>
            </div>
          </>
        )}
      </main>
      
      <footer className="bg-card py-4 text-center text-text-secondary">
        <p>XTC - Crypto Twitter Sentinel &copy; 2025</p>
      </footer>
    </div>
  );
}

export default App;
