import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HaikuOverview from './components/HaikuList';
import HaikuGenerator from './components/HaikuGenerator';
import AuthCallback from './components/AuthCallback';
import { useAuth } from 'react-oidc-context';

function App() {
  const auth = useAuth();

  if (auth.isLoading) {
    return <div>Loading...</div>;
  }

  if (auth.error) {
    return (
      <div>
        Authentication error: {auth.error.message}.
        <button onClick={() => window.location.reload()} className="text-primary">
          Reload page
        </button>
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HaikuOverview />} />
        <Route path="/haiku/:haiku_id" element={<HaikuGenerator />} />
        <Route path="/auth/callback" element={<AuthCallback />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;