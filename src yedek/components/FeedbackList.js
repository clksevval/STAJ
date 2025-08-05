import React from 'react';
function FeedbackList({ title, items, icon, color }) {
  return (
    <div className="feedback-list-card">
      <h3 className={`feedback-title ${color ? `title-color-${color}` : ''}`}>
        {icon && <span className="feedback-icon">{icon}</span>}
        {title}
      </h3>
      <ol className="feedback-list">
        {items.map((item, index) => (
          <li key={index}>{item.text}</li>
        ))}
      </ol>
    </div>
  );
}
export default FeedbackList;