import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router';
import HaikuOverview from './components/HaikuList';
import HaikuGenerator from './components/HaikuGenerator';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" exact component={HaikuOverview} />
        <Route path="/haiku/:haiku_id" component={HaikuGenerator} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;