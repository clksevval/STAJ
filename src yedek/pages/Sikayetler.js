import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function Sikayetler({ selectedProductId }) {
  const [complaints, setComplaints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!selectedProductId) return;

    const fetchComplaints = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`${API_BASE_URL}/reviews/fields/${selectedProductId}`);
        if (!response.ok) throw new Error('Şikayet verileri alınamadı.');
        const data = await response.json();
        setComplaints(data.complaints || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchComplaints();
  }, [selectedProductId]);

  if (loading) return <div className="loading">Şikayetler yükleniyor...</div>;
  if (error) return <div className="loading error">HATA: {error}</div>;

  return (
    <div>
      <h2>Ürüne Ait Tüm Şikayetler</h2>
      {complaints.length > 0 ? (
        <ul className="feedback-list">
          {complaints.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>Bu ürün için kayıtlı bir şikayet bulunamadı.</p>
      )}
    </div>
  );
}

export default Sikayetler;