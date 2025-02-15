import { useQuery } from '@tanstack/react-query';
import { fetchJson } from '../api/client';

interface LastStudySession {
  id: number;
  group_id: number;
  created_at: string;
  study_activity_id: number;
  group_name: string;
}

interface StudyProgress {
  total_words_studied: number;
  total_available_words: number;
}

interface QuickStats {
  success_rate: number;
  total_study_sessions: number;
  total_active_groups: number;
  study_streak_days: number;
}

function Dashboard() {
  const { data: lastSession } = useQuery<LastStudySession>({
    queryKey: ['lastStudySession'],
    queryFn: () => fetchJson('/dashboard/last_study_session'),
  });

  const { data: progress } = useQuery<StudyProgress>({
    queryKey: ['studyProgress'],
    queryFn: () => fetchJson('/dashboard/study_progress'),
  });

  const { data: stats } = useQuery<QuickStats>({
    queryKey: ['quickStats'],
    queryFn: () => fetchJson('/dashboard/quick_stats'),
  });

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Dashboard</h1>
      
      {/* We'll add the dashboard components here */}
    </div>
  );
}

export default Dashboard; 