import React from 'react'
import ReactDOM from 'react-dom/client'
import { App } from './App'
import { ThemeProvider } from "@/components/theme-provider"
import { ToastProvider } from "@/components/toast-provider"
import './index.css'
import { AuthProvider } from "react-oidc-context";

const cognitoAuthConfig = {
  authority: import.meta.env.VITE_COGNITO_AUTHORITY,
  client_id: import.meta.env.VITE_COGNITO_CLIENT_ID,
  redirect_uri: import.meta.env.VITE_REDIRECT_SIGN_IN,
  response_type: "code",
  scope: "email openid profile",
};

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider {...cognitoAuthConfig}>
      <ToastProvider>
        <ThemeProvider>
          <App />
        </ThemeProvider>
      </ToastProvider>
    </AuthProvider>
  </React.StrictMode>,
) 