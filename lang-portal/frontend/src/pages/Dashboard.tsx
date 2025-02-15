import { useQuery } from '@tanstack/react-query';
import { fetchJson } from '../api/client';
import { Card } from '../components/shared/Card';
import { Button } from '../components/shared/Button';
import { PageHeader } from '../components/shared/PageHeader';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import { Play } from 'lucide-react';

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
    <Card title="Last Study Session">
      <div className="space-y-4">
        <div className="flex flex-col items-center text-center">
          <p className="text-sm text-gray-600 mb-2">Group</p>
          <Link 
            to={`/groups/${session.group_id}`}
            className="text-xl font-medium text-primary-600 hover:text-primary-700"
          >
            {session.group_name}
          </Link>
          <p className="text-sm text-gray-600 mt-4">
            {format(new Date(session.created_at), 'PPp')}
          </p>
        </div>
      </div>
    </Card>
  );
}

function StudyProgressCard({ progress }: { progress: StudyProgress | undefined }) {
  if (!progress) return null;

  const percentage = Math.round((progress.total_words_studied / progress.total_available_words) * 100);

  return (
    <Card title="Study Progress">
      <div className="text-center">
        <div className="mb-4">
          <p className="text-3xl font-bold text-primary-600">{percentage}%</p>
          <p className="text-sm text-gray-600">Overall Progress</p>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2.5 mb-4">
          <div 
            className="bg-primary-600 h-2.5 rounded-full transition-all duration-500" 
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-600">
          {progress.total_words_studied} / {progress.total_available_words} words studied
        </p>
      </div>
    </Card>
  );
}

function QuickStatsCard({ stats }: { stats: QuickStats | undefined }) {
  if (!stats) return null;

  const statItems = [
    { label: 'Success Rate', value: `${stats.success_rate}%` },
    { label: 'Study Sessions', value: stats.total_study_sessions },
    { label: 'Active Groups', value: stats.total_active_groups },
    { label: 'Study Streak', value: `${stats.study_streak_days} days` },
  ];

  return (
    <Card title="Quick Stats">
      <div className="grid grid-cols-2 gap-6">
        {statItems.map((item) => (
          <div key={item.label} className="text-center">
            <p className="text-3xl font-bold text-gray-800">{item.value}</p>
            <p className="text-sm text-gray-600">{item.label}</p>
          </div>
        ))}
      </div>
    </Card>
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
    <div>
      <PageHeader 
        title="Dashboard" 
        showBack={false}
        action={{
          label: 'Start Studying',
          onClick: () => navigate('/study_activities')
        }}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="space-y-6">
          <LastStudySessionCard session={lastSession} />
          <StudyProgressCard progress={progress} />
        </div>
        <QuickStatsCard stats={stats} />
      </div>
    </div>
  );
}

export default Dashboard; 