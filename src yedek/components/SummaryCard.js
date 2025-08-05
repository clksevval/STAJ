import React from 'react';
function SummaryCard({ icon, title, value, color }) {
  return (
    <div className={`summary-card card-color-${color}`}>
      <span className="summary-icon">{icon}</span>
      <div className="summary-text">
        <div className="summary-value">{value}</div>
        <div className="summary-title">{title}</div>
      </div>
    </div>
  );
}
export default SummaryCard;