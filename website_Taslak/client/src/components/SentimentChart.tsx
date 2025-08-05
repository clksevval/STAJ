import { mockAnalysisData } from "../data/mockData";

const SentimentChart = () => {
  const { positive, negative, neutral } = mockAnalysisData.sentiment_distribution;
  
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Duygu Dağılımı</h3>
      <div className="space-y-4">
        {/* Positive */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-2xl mr-3">😊</span>
            <span className="text-sm font-medium text-gray-700">Pozitif</span>
          </div>
          <div className="flex items-center">
            <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
              <div 
                className="bg-green-500 h-2 rounded-full" 
                style={{ width: `${positive}%` }}
              ></div>
            </div>
            <span className="text-sm font-semibold text-green-600">{positive}%</span>
          </div>
        </div>

        {/* Negative */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-2xl mr-3">😞</span>
            <span className="text-sm font-medium text-gray-700">Negatif</span>
          </div>
          <div className="flex items-center">
            <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
              <div 
                className="bg-red-500 h-2 rounded-full" 
                style={{ width: `${negative}%` }}
              ></div>
            </div>
            <span className="text-sm font-semibold text-red-600">{negative}%</span>
          </div>
        </div>

        {/* Neutral */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="text-2xl mr-3">😐</span>
            <span className="text-sm font-medium text-gray-700">Nötr</span>
          </div>
          <div className="flex items-center">
            <div className="w-32 bg-gray-200 rounded-full h-2 mr-3">
              <div 
                className="bg-gray-500 h-2 rounded-full" 
                style={{ width: `${neutral}%` }}
              ></div>
            </div>
            <span className="text-sm font-semibold text-gray-600">{neutral}%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SentimentChart;
  