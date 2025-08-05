import Sidebar from "../components/Sidebar";
import SentimentChart from "../components/SentimentChart";
import FeatureChart from "../components/FeatureChart";
import TipsList from "../components/TipsList";
import ComplaintsList from "../components/ComplaintsList";
import ProsConsList from "../components/ProsConsList";
import ExpectationsList from "../components/ExpectationsList";
import { mockAnalysisData } from "../data/mockData";

const Dashboard = () => {
  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-auto">
        <div className="p-6">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Decathlon Ürün Analizi
            </h1>
            <p className="text-gray-600">
              Ürün ID: {mockAnalysisData.product_id} • 
              Toplam {mockAnalysisData.total_reviews.toLocaleString()} değerlendirme
            </p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-2 bg-green-100 rounded-lg">
                  <span className="text-2xl">😊</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Pozitif</p>
                  <p className="text-2xl font-bold text-green-600">
                    {mockAnalysisData.sentiment_distribution.positive}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-2 bg-red-100 rounded-lg">
                  <span className="text-2xl">😞</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Negatif</p>
                  <p className="text-2xl font-bold text-red-600">
                    {mockAnalysisData.sentiment_distribution.negative}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-2 bg-gray-100 rounded-lg">
                  <span className="text-2xl">😐</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Nötr</p>
                  <p className="text-2xl font-bold text-gray-600">
                    {mockAnalysisData.sentiment_distribution.neutral}%
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200">
              <div className="flex items-center">
                <div className="p-2 bg-blue-100 rounded-lg">
                  <span className="text-2xl">📊</span>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Toplam</p>
                  <p className="text-2xl font-bold text-blue-600">
                    {mockAnalysisData.total_reviews.toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Charts Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <SentimentChart />
            <FeatureChart />
          </div>

          {/* Lists Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <ComplaintsList />
            <TipsList />
          </div>

          {/* Pros/Cons Section */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <ProsConsList />
            <ExpectationsList />
          </div>
        </div>
      </main>
    </div>
  );
};

export default Dashboard;
