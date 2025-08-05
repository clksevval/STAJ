import React from 'react';
import SummaryCard from './SummaryCard';
import CategoryBar from './CategoryBar';
import FeedbackList from './FeedbackList';

// Bu fonksiyonda geçen sefer yaptığımız düzeltme vardı, aynen kalıyor.
const convertObjectToArray = (obj) => {
    if (!obj) {
        return [];
    }
    return Object.entries(obj)
                 .sort(([, countA], [, countB]) => countB - countA)
                 .map(([text, count]) => ({ text, count }));
}

function ProductAnalysis({ data }) {
  if (!data) return null;

  // Bu kısım da aynı kalıyor
  const topProsArray = convertObjectToArray(data.top_pros);
  const topConsArray = convertObjectToArray(data.top_cons);
  const topComplaintsArray = convertObjectToArray(data.top_complaints);
  const topSuggestionsArray = convertObjectToArray(data.top_suggestions);
  const producerExpectationsArray = convertObjectToArray(data.producer_expectations);

  return (
    <div className="analysis-grid">
      {/* Üst Kısım: Özet Kartları */}
      <div className="grid-section section-summary-cards">
        <SummaryCard 
            icon="😊" 
            title="Pozitif" 
            // DÜZELTME: data.sentiment'in var olup olmadığını kontrol et, yoksa 0 kullan
            value={`${data.sentiment?.positive || 0}%`} 
            color="positive" 
        />
        <SummaryCard 
            icon="☹️" 
            title="Negatif" 
            // DÜZELTME: data.sentiment'in var olup olmadığını kontrol et, yoksa 0 kullan
            value={`${data.sentiment?.negative || 0}%`} 
            color="negative" 
        />
        <SummaryCard 
            icon="😐" 
            title="Nötr" 
            // DÜZELTME: data.sentiment'in var olup olmadığını kontrol et, yoksa 0 kullan
            value={`${data.sentiment?.neutral || 0}%`} 
            color="neutral" 
        />
        <SummaryCard 
            icon="📊" 
            title="Toplam" 
            value={data.total_reviews.toLocaleString()} 
            color="total" 
        />
      </div>

      {/* Orta Kısım: Duygu Dağılımı ve Özellikler */}
      <div className="grid-section section-details">
        <div className="detail-card">
            <h3>Duygu Dağılımı</h3>
            <div className="sentiment-distribution">
                <span>Pozitif</span>
                <div className="sentiment-bar-container">
                    {/* DÜZELTME: data.sentiment'in var olup olmadığını kontrol et, yoksa 0 kullan */}
                    <div className="sentiment-bar positive" style={{width: `${data.sentiment?.positive || 0}%`}}></div>
                </div>
                <span>{data.sentiment?.positive || 0}%</span>
            </div>
            <div className="sentiment-distribution">
                <span>Negatif</span>
                <div className="sentiment-bar-container">
                    {/* DÜZELTME: data.sentiment'in var olup olmadığını kontrol et, yoksa 0 kullan */}
                    <div className="sentiment-bar negative" style={{width: `${data.sentiment?.negative || 0}%`}}></div>
                </div>
                <span>{data.sentiment?.negative || 0}%</span>
            </div>
             <div className="sentiment-distribution">
                <span>Nötr</span>
                <div className="sentiment-bar-container">
                    {/* DÜZELTME: data.sentiment'in var olup olmadığını kontrol et, yoksa 0 kullan */}
                    <div className="sentiment-bar neutral" style={{width: `${data.sentiment?.neutral || 0}%`}}></div>
                </div>
                <span>{data.sentiment?.neutral || 0}%</span>
            </div>
        </div>
        <div className="detail-card">
            <h3>Özellik Kategorileri</h3>
            {/* DÜZELTME: feature_categories'in de boş olabileceğini varsayarak kontrol ekleyelim */}
            {(data.feature_categories || []).map(cat => (
                <CategoryBar key={cat.name} label={cat.name} value={cat.value} />
            ))}
        </div>
      </div>
      
      {/* Alt Kısım: Geri Bildirim Listeleri (Bu kısım zaten düzgündü) */}
      <div className="grid-section section-feedback">
         <FeedbackList title="Artılar" items={topProsArray} icon="✔" color="positive" />
         <FeedbackList title="Eksiler" items={topConsArray} icon="✖" color="negative" />
      </div>
      <div className="grid-section section-feedback">
         <FeedbackList title="En Çok Şikayetler" items={topComplaintsArray} />
         <FeedbackList title="Kullanıcı Tavsiyeleri" items={topSuggestionsArray} />
      </div>
      <div className="grid-section section-feedback single-column">
         <FeedbackList title="Üreticiden Beklentiler" items={producerExpectationsArray} />
      </div>
    </div>
  );
}

export default ProductAnalysis;