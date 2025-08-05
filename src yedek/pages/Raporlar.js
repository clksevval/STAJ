import React, { useState, useEffect } from 'react';
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE_URL = 'http://localhost:8000';

// Veriyi Recharts formatına dönüştüren yardımcı fonksiyon
const formatDataForChart = (dataObject) => {
  if (!dataObject) return [];
  return Object.entries(dataObject).map(([name, value]) => ({ name, value }));
};

// Her dilim için farklı renkler
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#AF19FF'];

function Raporlar({ selectedProductId }) {
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!selectedProductId) return;

    const fetchChartData = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`${API_BASE_URL}/analysis/${selectedProductId}`);
        if (!response.ok) throw new Error('Grafik verileri alınamadı.');
        const data = await response.json();
        setChartData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchChartData();
  }, [selectedProductId]);

  if (loading) return <div className="loading">Raporlar yükleniyor...</div>;
  if (error) return <div className="loading error">HATA: {error}</div>;
  if (!chartData) return <p>Grafik için veri bulunamadı.</p>;

  const prosData = formatDataForChart(chartData.top_pros);
  const consData = formatDataForChart(chartData.top_cons);

  return (
    <div className="reports-grid">
      <div className="chart-container">
        <h3>En Beğenilen Özellikler Dağılımı (Pie Chart)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={prosData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} fill="#8884d8" label>
              {prosData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-container">
        <h3>En Beğenilmeyen Özellikler Dağılımı (Donut Chart)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <PieChart>
            <Pie data={consData} dataKey="value" nameKey="name" cx="50%" cy="50%" innerRadius={60} outerRadius={80} fill="#82ca9d" paddingAngle={5} label>
               {consData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Raporlar;