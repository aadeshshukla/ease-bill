import React from 'react'
import { createRoot } from 'react-dom/client'

function App() {
  const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
  const docsUrl = `${apiBaseUrl.replace(/\/$/, '')}/docs`
  const healthUrl = `${apiBaseUrl.replace(/\/$/, '')}/health`

  return (
    <main>
      <h1>Ease Bill</h1>
      <p>API Base URL: {apiBaseUrl}</p>
      <p>
        API Docs: <a href={docsUrl}>{docsUrl}</a>
      </p>
      <p>
        Health Check: <a href={healthUrl}>{healthUrl}</a>
      </p>
    </main>
  )
}

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
