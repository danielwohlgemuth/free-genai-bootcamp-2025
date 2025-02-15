import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Layout } from './components/Layout';

// Pages
import Dashboard from './pages/Dashboard';
import StudyActivitiesIndex from './pages/StudyActivities/Index';
import StudyActivityShow from './pages/StudyActivities/Show';
import StudyActivityLaunch from './pages/StudyActivities/Launch';
import WordsIndex from './pages/Words/Index';
import WordShow from './pages/Words/Show';
import GroupsIndex from './pages/Groups/Index';
import GroupShow from './pages/Groups/Show';
import StudySessionsIndex from './pages/StudySessions/Index';
import StudySessionShow from './pages/StudySessions/Show';
import Settings from './pages/Settings';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/study_activities" element={<StudyActivitiesIndex />} />
            <Route path="/study_activities/:id" element={<StudyActivityShow />} />
            <Route path="/study_activities/:id/launch" element={<StudyActivityLaunch />} />
            <Route path="/words" element={<WordsIndex />} />
            <Route path="/words/:id" element={<WordShow />} />
            <Route path="/groups" element={<GroupsIndex />} />
            <Route path="/groups/:id" element={<GroupShow />} />
            <Route path="/study_sessions" element={<StudySessionsIndex />} />
            <Route path="/study_sessions/:id" element={<StudySessionShow />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App; 