import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom'; // Import et
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    {/* App bileşenini BrowserRouter ile sarmala */}
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);