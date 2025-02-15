import { useQuery } from '@tanstack/react-query';
import { fetchJson } from '../api/client';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';

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

function LastStudySessionCard({ session }: { session: LastStudySession | undefined }) {
  if (!session) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Last Study Session</h2>
      <div className="space-y-2">
        <p>Group: <Link to={`/groups/${session.group_id}`} className="text-blue-600 hover:underline">{session.group_name}</Link></p>
        <p>Date: {format(new Date(session.created_at), 'PPp')}</p>
      </div>
    </div>
  );
}

function StudyProgressCard({ progress }: { progress: StudyProgress | undefined }) {
  if (!progress) return null;

  const percentage = Math.round((progress.total_words_studied / progress.total_available_words) * 100);

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Study Progress</h2>
      <div className="space-y-2">
        <p>Words Studied: {progress.total_words_studied} / {progress.total_available_words}</p>
        <div className="w-full bg-gray-200 rounded-full h-2.5">
          <div 
            className="bg-blue-600 h-2.5 rounded-full" 
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
      </div>
    </div>
  );
}

function QuickStatsCard({ stats }: { stats: QuickStats | undefined }) {
  if (!stats) return null;

  return (
    <div className="bg-white rounded-lg shadow p-6 mb-6">
      <h2 className="text-xl font-semibold mb-4">Quick Stats</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-gray-600">Success Rate</p>
          <p className="text-2xl font-bold">{stats.success_rate}%</p>
        </div>
        <div>
          <p className="text-gray-600">Study Sessions</p>
          <p className="text-2xl font-bold">{stats.total_study_sessions}</p>
        </div>
        <div>
          <p className="text-gray-600">Active Groups</p>
          <p className="text-2xl font-bold">{stats.total_active_groups}</p>
        </div>
        <div>
          <p className="text-gray-600">Study Streak</p>
          <p className="text-2xl font-bold">{stats.study_streak_days} days</p>
        </div>
      </div>
    </div>
  );
}

function StartStudyingButton() {
  return (
    <Link 
      to="/study_activities"
      className="block w-full bg-blue-600 text-white text-center py-3 rounded-lg hover:bg-blue-700 transition-colors"
    >
      Start Studying
    </Link>
  );
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
      
      <div className="max-w-4xl mx-auto">
        <LastStudySessionCard session={lastSession} />
        <StudyProgressCard progress={progress} />
        <QuickStatsCard stats={stats} />
        <StartStudyingButton />
      </div>
    </div>
  );
}

export default Dashboard; 