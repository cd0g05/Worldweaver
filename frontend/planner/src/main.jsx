import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import PlannerApp from './PlannerPage.jsx'
import { StageProvider } from "./StageContext.jsx";

createRoot(document.getElementById('root')).render(
  <StrictMode>
      <StageProvider>
          <PlannerApp />
      </StageProvider>
  </StrictMode>,
)
