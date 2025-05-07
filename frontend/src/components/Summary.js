import React from 'react';

function Summary({ summary }) {
  if (!summary) return null;
  
  // Format timestamp to readable format
  const formatDate = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleString();
  };
  
  // Generate sentiment chart data for visualization
  const generateSentimentData = () => {
    const sentimentData = summary.sentiment_overview || {};
    const bullish = sentimentData.bullish || 0;
    const bearish = sentimentData.bearish || 0;
    const neutral = sentimentData.neutral || 0;
    const total = bullish + bearish + neutral;
    
    if (total === 0) return null;
    
    // Calculate percentages
    const bullishPercent = Math.round((bullish / total) * 100);
    const bearishPercent = Math.round((bearish / total) * 100);
    const neutralPercent = Math.round((neutral / total) * 100);
    
    return { bullishPercent, bearishPercent, neutralPercent, total };
  };
  
  const sentimentData = generateSentimentData();
  
  return (
    <div className="bg-slate-800 shadow-lg rounded-lg p-6 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold text-blue-400">Live Summary</h2>
        <span className="text-sm text-slate-400">
          {formatDate(summary.timestamp)}
        </span>
      </div>
      
      <div className="prose prose-invert max-w-none mb-6">
        <p className="text-lg leading-relaxed">{summary.content}</p>
      </div>
      
      {sentimentData && (
        <div className="mb-4">
          <h3 className="text-lg font-semibold mb-2">Sentiment Overview</h3>
          <div className="flex h-6 w-full rounded-full overflow-hidden">
            <div 
              className="bg-green-500 h-full"
              style={{ width: `${sentimentData.bullishPercent}%` }}
              title={`Bullish: ${sentimentData.bullishPercent}%`}
            ></div>
            <div 
              className="bg-gray-500 h-full" 
              style={{ width: `${sentimentData.neutralPercent}%` }}
              title={`Neutral: ${sentimentData.neutralPercent}%`}
            ></div>
            <div 
              className="bg-red-500 h-full"
              style={{ width: `${sentimentData.bearishPercent}%` }}
              title={`Bearish: ${sentimentData.bearishPercent}%`}
            ></div>
          </div>
          <div className="flex justify-between text-xs mt-1">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-1"></div>
              <span>Bullish {sentimentData.bullishPercent}%</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-gray-500 rounded-full mr-1"></div>
              <span>Neutral {sentimentData.neutralPercent}%</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-1"></div>
              <span>Bearish {sentimentData.bearishPercent}%</span>
            </div>
          </div>
        </div>
      )}
      
      {summary.trending_cryptos && summary.trending_cryptos.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-2">Trending Cryptocurrencies</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {summary.trending_cryptos.slice(0, 6).map((crypto, index) => (
              <div 
                key={index} 
                className="bg-slate-700 rounded-lg p-3 flex items-center justify-between"
              >
                <div>
                  <div className="font-medium capitalize">{crypto.name}</div>
                  <div className="text-sm text-slate-400">{crypto.mentions} mentions</div>
                </div>
                <div className={`text-sm font-medium ${
                  crypto.sentiment >= 0.05 ? 'text-green-400' : 
                  crypto.sentiment <= -0.05 ? 'text-red-400' : 'text-gray-400'
                }`}>
                  {crypto.sentiment >= 0.05 ? 'Bullish' : 
                   crypto.sentiment <= -0.05 ? 'Bearish' : 'Neutral'}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      <div className="mt-6 flex justify-end">
        <button className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md text-sm font-medium transition-colors">
          Refresh Data
        </button>
      </div>
    </div>
  );
}

export default Summary;
