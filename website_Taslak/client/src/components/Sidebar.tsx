import React from 'react';

const Sidebar = () => {
  return (
    <aside className="w-64 bg-gray-900 text-white p-6 shadow-lg">
      <div className="mb-8">
        <h2 className="text-xl font-bold text-blue-300 mb-2">Decathlon Paneli</h2>
        <p className="text-gray-400 text-sm">Ürün Analiz Sistemi</p>
      </div>
      
      <nav className="space-y-2">
        <a href="#" className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors bg-gray-800 text-white">
          <span className="mr-3">📊</span>
          Gösterge Paneli
        </a>
        <a href="#" className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
          <span className="mr-3">📈</span>
          Ürün Analizleri
        </a>
        <a href="#" className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
          <span className="mr-3">⚠️</span>
          Şikayetler
        </a>
        <a href="#" className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
          <span className="mr-3">💡</span>
          Tavsiyeler
        </a>
        <a href="#" className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
          <span className="mr-3">📋</span>
          Raporlar
        </a>
        <a href="#" className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white rounded-lg transition-colors">
          <span className="mr-3">⚙️</span>
          Ayarlar
        </a>
      </nav>

      <div className="mt-auto pt-8 border-t border-gray-700">
        <div className="text-center">
          <p className="text-gray-400 text-xs">Son güncelleme</p>
          <p className="text-gray-300 text-sm">15 Ocak 2024</p>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
