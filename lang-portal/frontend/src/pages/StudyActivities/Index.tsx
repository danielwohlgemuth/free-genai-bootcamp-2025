import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { fetchJson } from '../../api/client';

interface StudyActivity {
  id: number;
  name: string;
  thumbnail_url: string;
  description: string;
}

function StudyActivityCard({ activity }: { activity: StudyActivity }) {
  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <img 
        src={activity.thumbnail_url} 
        alt={activity.name}
        className="w-full h-48 object-cover"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2">{activity.name}</h3>
        <div className="flex gap-2">
          <Link
            to={`/study_activities/${activity.id}/launch`}
            className="flex-1 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-center"
          >
            Launch
          </Link>
          <Link
            to={`/study_activities/${activity.id}`}
            className="flex-1 bg-gray-100 text-gray-700 px-4 py-2 rounded hover:bg-gray-200 text-center"
          >
            View Details
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function StudyActivitiesIndex() {
  const { data: activities, isLoading } = useQuery<StudyActivity[]>({
    queryKey: ['studyActivities'],
    queryFn: () => fetchJson('/study_activities'),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Study Activities</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {activities?.map((activity) => (
          <StudyActivityCard key={activity.id} activity={activity} />
        ))}
      </div>
    </div>
  );
} 