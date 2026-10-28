import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  // removing StricMode to stop double calls, but it must be there when deploying (it catches real bugs)
  <StrictMode>
    <App />
  </StrictMode>,
)