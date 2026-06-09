import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import './styles/globals.css'

// Aplicar tema salvo antes do render
const tema = localStorage.getItem('tema-aparencia') || 'dark'
document.documentElement.classList.add(tema)

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
