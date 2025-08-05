import React from 'react';
import { NavLink } from 'react-router-dom'; // NavLink'i import ediyoruz

function Sidebar() {
  return (
    <aside className="sidebar">
      <h1 className="sidebar-title">Decathlon Paneli</h1>
      <nav className="sidebar-nav">
        <ul>
          {/*
            NavLink, 'to' ile gideceği adresi alır.
            Tıklanınca sayfa yenilenmez, sadece içerik değişir.
            className içinde, link aktif ise 'active' sınıfını otomatik ekler.
          */}
          <li><NavLink to="/" className={({ isActive }) => (isActive ? 'active' : '')}>Gösterge Paneli</NavLink></li>
          <li><NavLink to="/urun-analizleri" className={({ isActive }) => (isActive ? 'active' : '')}>Ürün Analizleri</NavLink></li>
          <li><NavLink to="/sikayetler" className={({ isActive }) => (isActive ? 'active' : '')}>Şikayetler</NavLink></li>
          <li><NavLink to="/tavsiyeler" className={({ isActive }) => (isActive ? 'active' : '')}>Tavsiyeler</NavLink></li>
          <li><NavLink to="/raporlar" className={({ isActive }) => (isActive ? 'active' : '')}>Raporlar</NavLink></li>
        </ul>
      </nav>
      <div className="sidebar-footer">
        Son güncelleme <br /> 15 Ağustos 2025
      </div>
    </aside>
  );
}

export default Sidebar;