import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Summary from './components/Summary';
import TaskList from './components/TaskList';
import Footer from './components/Footer';

function App() {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Fetch data from your backend when the component mounts
    const fetchData = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/data');
        
        if (!response.ok) {
          throw new Error(`API error: ${response.status}`);
        }
        
        const result = await response.json();
        setData(result);
        setError(null);
      } catch (err) {
        console.error('Error fetching data:', err);
        setError('Failed to load data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Calculate summary data from the fetched data
  const summaryData = data ? {
    totalItems: data.tasks?.length || 0,
    completedItems: data.tasks?.filter(task => task.completed).length || 0,
    pendingItems: data.tasks?.filter(task => !task.completed).length || 0,
    progress: data.tasks?.length ? 
      Math.round((data.tasks.filter(task => task.completed).length / data.tasks.length) * 100) : 0
  } : null;

  return (
    <div className="min-h-screen flex flex-col bg-gray-50">
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-8">
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : error ? (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            <p>{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="md:col-span-1">
              <Summary summary={summaryData} />
            </div>
            <div className="md:col-span-3">
              <TaskList tasks={data?.tasks || []} />
            </div>
          </div>
        )}
      </main>
      
      <Footer />
    </div>
  );
}

export default App;
