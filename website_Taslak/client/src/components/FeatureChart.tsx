import { mockAnalysisData } from "../data/mockData";

const FeatureChart = () => {
  const featureCategories = Object.entries(mockAnalysisData.feature_categories);
  
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h3 className="text-lg font-semibold text-gray-800 mb-4">Özellik Kategorileri</h3>
      <div className="space-y-3">
        {featureCategories.map(([category, score], index) => (
          <div key={index} className="flex items-center justify-between">
            <span className="text-sm font-medium text-gray-700 w-32 truncate">
              {category}
            </span>
            <div className="flex items-center flex-1 mx-3">
              <div className="flex-1 bg-gray-200 rounded-full h-2 mr-3">
                <div 
                  className="bg-blue-500 h-2 rounded-full transition-all duration-300" 
                  style={{ width: `${score}%` }}
                ></div>
              </div>
              <span className="text-sm font-semibold text-blue-600 w-8 text-right">
                {score}%
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default FeatureChart;
  