import React from 'react'
import ReactDOM from 'react-dom/client'
import { AppContextProvider } from 'contexts'
import { App } from 'App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppContextProvider>
      <App />
    </AppContextProvider>
  </React.StrictMode>,
)
