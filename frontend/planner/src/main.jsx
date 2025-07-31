import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import PlannerApp from './PlannerPage.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <PlannerApp />
  </StrictMode>,
)
