import { mockAnalysisData } from "../data/mockData";

const ExpectationsList = () => {
  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-800">Üreticiden Beklentiler</h2>
        <span className="text-sm text-gray-500">Top 10</span>
      </div>
      <div className="space-y-3">
        {mockAnalysisData.expectations_from_producer.map((expectation, index) => (
          <div key={index} className="flex items-start p-3 bg-blue-50 rounded-lg border border-blue-100">
            <span className="flex-shrink-0 w-6 h-6 bg-blue-500 text-white text-xs rounded-full flex items-center justify-center mr-3 mt-0.5">
              {index + 1}
            </span>
            <span className="text-gray-700 text-sm">{expectation}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ExpectationsList; 