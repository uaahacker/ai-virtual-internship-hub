import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import App from './App';
import { AuthProvider } from './contexts/AuthContext';
import './index.css';

console.log('🚀 main.jsx - Starting React app...');

try {
  const root = document.getElementById('root');
  if (!root) {
    throw new Error('Root element not found! Check index.html');
  }
  
  console.log('✅ Root element found:', root);
  
  ReactDOM.createRoot(root).render(
    <React.StrictMode>
      <BrowserRouter>
        <AuthProvider>
          <App />
          <ToastContainer position="top-right" autoClose={3000} />
        </AuthProvider>
      </BrowserRouter>
    </React.StrictMode>
  );
  
  console.log('✅ React app mounted successfully');
} catch (err) {
  console.error('❌ Fatal error mounting React:', err);
  document.body.innerHTML = `<div style="color: red; padding: 20px;">Fatal Error: ${err.message}</div>`;
}
