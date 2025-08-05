import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import './App.css';

import Sidebar from './components/Sidebar';
import ProductSelector from './components/ProductSelector';
import GostergePaneli from './pages/GostergePaneli';
import UrunAnalizleri from './pages/UrunAnalizleri';
import Sikayetler from './pages/Sikayetler';
import Tavsiyeler from './pages/Tavsiyeler';
import Raporlar from './pages/Raporlar';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [products, setProducts] = useState([]);
  const [selectedProductId, setSelectedProductId] = useState('');
  const [isLoadingProducts, setIsLoadingProducts] = useState(true);

  // Ürün listesini en üst bileşende SADECE BİR KEZ çekiyoruz
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/products`);
        if (!response.ok) throw new Error('Sunucudan ürünler alınamadı.');
        const data = await response.json();
        const productList = data.map(p => ({
          id: p.product_id,
          name: p.product_name || `Ürün #${p.product_id}`
        }));
        setProducts(productList);
        if (productList.length > 0) {
          setSelectedProductId(productList[0].id);
        }
      } catch (error) {
        console.error("Ürünler çekilirken hata:", error);
      } finally {
        setIsLoadingProducts(false);
      }
    };
    fetchProducts();
  }, []);

  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        <header className="main-header">
          {/* Dropdown artık tüm sayfalar için burada görünecek */}
          <h2>Decathlon Ürün Analizi</h2>
          {!isLoadingProducts && products.length > 0 ? (
            <ProductSelector
                products={products}
                selectedId={selectedProductId}
                onChange={e => setSelectedProductId(e.target.value)}
            />
          ) : (
            <p>Ürünler yükleniyor veya bulunamadı...</p>
          )}
        </header>
        <div className="content-area">
          <Routes>
            {/* Seçili ürün ID'sini sayfalara prop olarak iletiyoruz */}
            <Route path="/" element={<GostergePaneli selectedProductId={selectedProductId} />} />
            <Route path="/urun-analizleri" element={<UrunAnalizleri selectedProductId={selectedProductId} />} />
            <Route path="/sikayetler" element={<Sikayetler selectedProductId={selectedProductId} />} />
            <Route path="/tavsiyeler" element={<Tavsiyeler selectedProductId={selectedProductId} />} />
            <Route path="/raporlar" element={<Raporlar selectedProductId={selectedProductId} />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}

export default App;