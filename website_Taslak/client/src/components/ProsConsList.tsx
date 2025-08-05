import { mockAnalysisData } from "../data/mockData";

const ProsConsList = () => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <h2 className="text-xl font-semibold text-gray-800 mb-6">Artılar ve Eksiler</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pros */}
        <div>
          <h3 className="text-lg font-medium text-green-700 mb-4 flex items-center">
            <span className="mr-2">✅</span>
            Artılar
          </h3>
          <div className="space-y-2">
            {mockAnalysisData.top_pros.slice(0, 5).map((pro, index) => (
              <div key={index} className="flex items-start p-2 bg-green-50 rounded-lg">
                <span className="text-green-500 mr-2 mt-0.5">•</span>
                <span className="text-gray-700 text-sm">{pro}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Cons */}
        <div>
          <h3 className="text-lg font-medium text-red-700 mb-4 flex items-center">
            <span className="mr-2">❌</span>
            Eksiler
          </h3>
          <div className="space-y-2">
            {mockAnalysisData.top_cons.slice(0, 5).map((con, index) => (
              <div key={index} className="flex items-start p-2 bg-red-50 rounded-lg">
                <span className="text-red-500 mr-2 mt-0.5">•</span>
                <span className="text-gray-700 text-sm">{con}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProsConsList; 