import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom';
import HaikuOverview from './components/HaikuList';
import HaikuGenerator from './components/HaikuGenerator';

function App() {
  return (
    <Router>
      <Switch>
        <Route path="/" exact component={HaikuOverview} />
        <Route path="/haiku/:haiku_id" component={HaikuGenerator} />
      </Switch>
    </Router>
  );
}

export default App;