import React from 'react';
function CategoryBar({ label, value }) {
  return (
    <div className="category-bar-wrapper">
      <span className="category-label">{label}</span>
      <div className="category-bar-container">
        <div className="category-bar-fill" style={{ width: `${value}%` }}></div>
      </div>
      <span className="category-value">{value}%</span>
    </div>
  );
}
export default CategoryBar;