import React, { useState, useEffect } from 'react';

const API_BASE_URL = 'http://localhost:8000';

function Tavsiyeler({ selectedProductId }) {
  const [suggestions, setSuggestions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!selectedProductId) return;

    const fetchSuggestions = async () => {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(`${API_BASE_URL}/reviews/fields/${selectedProductId}`);
        if (!response.ok) throw new Error('Tavsiye verileri alınamadı.');
        const data = await response.json();
        setSuggestions(data.suggestions || []);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchSuggestions();
  }, [selectedProductId]);

  if (loading) return <div className="loading">Tavsiyeler yükleniyor...</div>;
  if (error) return <div className="loading error">HATA: {error}</div>;

  return (
    <div>
      <h2>Ürüne Ait Tüm Tavsiyeler</h2>
      {suggestions.length > 0 ? (
        <ul className="feedback-list">
          {suggestions.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>Bu ürün için kayıtlı bir tavsiye bulunamadı.</p>
      )}
    </div>
  );
}

export default Tavsiyeler;