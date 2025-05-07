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
  const [error, setError] = useState(null);
  const [refreshing, setRefreshing] = useState(false);

  // Function to fetch data from the API
  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch summaries
      const summariesResponse = await axios.get('/api/summaries');
      setSummaries(summariesResponse.data);
      
      // Fetch alerts
      const alertsResponse = await axios.get('/api/alerts');
      setAlerts(alertsResponse.data);
      
      // Fetch tweets
      const tweetsResponse = await axios.get('/api/tweets');
      setTweets(tweetsResponse.data);
      
      setLoading(false);
    } catch (err) {
      setError('Failed to fetch data. Please try again later.');
      setLoading(false);
    }
  };
  
  // Function to manually refresh data
  const handleRefresh = async () => {
    try {
      setRefreshing(true);
      
      // Trigger backend refresh
      await axios.post('/api/refresh');
      
      // Wait a moment for the backend to process
      setTimeout(() => {
        fetchData().then(() => {
          setRefreshing(false);
        });
      }, 3000);
    } catch (err) {
      setError('Failed to refresh data. Please try again later.');
      setRefreshing(false);
    }
  };
  
  // Mark an alert as read
  const markAlertRead = async (alertId) => {
    try {
      await axios.post(`/api/alerts/${alertId}/read`);
      // Update alerts list
      setAlerts(alerts.map(alert => 
        alert.id === alertId ? { ...alert, is_read: true } : alert
      ));
    } catch (err) {
      setError('Failed to mark alert as read.');
    }
  };
  
  // Fetch data on component mount
  useEffect(() => {
    fetchData();
    
    // Set up an interval to refresh data every 5 minutes
    const interval = setInterval(() => {
      fetchData();
    }, 5 * 60 * 1000);
    
    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="min-h-screen bg-crypto-dark text-white">
      <Header onRefresh={handleRefresh} refreshing={refreshing} />
      
      <main className="container mx-auto px-4 py-6">
        {loading && !refreshing ? (
          <div className="flex justify-center items-center h-64">
            <p className="text-xl">Loading Crypto Twitter data...</p>
          </div>
        ) : error ? (
          <div className="bg-red-900 text-white p-4 rounded-lg mb-6">
            <p>{error}</p>
          </div>
        ) : (
          <>
            {/* Summary Section */}
            <Summary 
              summary={summaries.length > 0 ? summaries[0] : null} 
              refreshing={refreshing} 
            />
            
            {/* Main Content Section */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
              {/* Feed Container */}
              <div className="lg:col-span-2">
                <FeedContainer 
                  alerts={alerts}
                  tweets={tweets}
                  markAlertRead={markAlertRead}
                  refreshing={refreshing}
                />
              </div>
              
              {/* Chat Panel */}
              <div className="lg:col-span-1">
                <ChatPanel />
              </div>
            </div>
          </>
        )}
      </main>
      
      <footer className="container mx-auto px-4 py-6 text-center text-gray-500 text-sm">
        <p>XTC - Crypto Twitter Sentinel &copy; {new Date().getFullYear()}</p>
      </footer>
    </div>
  );
}

export default App;
