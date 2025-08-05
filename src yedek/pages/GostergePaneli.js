import React, { useState, useEffect } from 'react';
import ProductAnalysis from '../components/ProductAnalysis';

const API_BASE_URL = 'http://localhost:8000';

// Artık 'selectedProductId' prop olarak geliyor
function GostergePaneli({ selectedProductId }) {
  const [analysisData, setAnalysisData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Eğer seçili ürün yoksa veya değişiyorsa, veriyi çek
    if (!selectedProductId) return;

    const fetchAnalysisData = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`${API_BASE_URL}/analysis/${selectedProductId}`);
        if (!response.ok) throw new Error(`Ürün analizi alınamadı.`);
        const data = await response.json();
        setAnalysisData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalysisData();
  }, [selectedProductId]); // Bu effect, prop'tan gelen ID değiştiğinde çalışır

  if (loading) return <div className="loading">Analiz verisi yükleniyor...</div>;
  if (error) return <div className="loading error">HATA: {error}</div>;
  if (analysisData) return <ProductAnalysis data={analysisData} />;

  return <div className="loading">Lütfen bir ürün seçin.</div>;
}

export default GostergePaneli;