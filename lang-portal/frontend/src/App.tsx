import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

import Dashboard from './pages/Dashboard';
// We'll add more routes as we build them

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <div className="min-h-screen bg-background">
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            {/* We'll add more routes here */}
          </Routes>
        </div>
      </Router>
    </QueryClientProvider>
  );
}

export default App; 