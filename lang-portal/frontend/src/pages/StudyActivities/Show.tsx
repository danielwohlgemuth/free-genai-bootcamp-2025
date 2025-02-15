import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { fetchJson } from '../../api/client';
import { Pagination } from '../../components/shared/Pagination';
import { useState } from 'react';
import { format } from 'date-fns';

interface StudyActivity {
  id: number;
  name: string;
  thumbnail_url: string;
  description: string;
}

interface StudySession {
  id: number;
  activity_name: string;
  group_name: string;
  start_time: string;
  end_time: string;
  review_items_count: number;
}

interface PaginatedResponse {
  items: StudySession[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_items: number;
    items_per_page: number;
  };
}

export default function StudyActivityShow() {
  const { id } = useParams<{ id: string }>();
  const [page, setPage] = useState(1);

  const { data: activity } = useQuery<StudyActivity>({
    queryKey: ['studyActivity', id],
    queryFn: () => fetchJson(`/study_activities/${id}`),
  });

  const { data: sessionsData } = useQuery<PaginatedResponse>({
    queryKey: ['studyActivitySessions', id, page],
    queryFn: () => fetchJson(`/study_activities/${id}/study_sessions?page=${page}`),
  });

  return (
    <div className="max-w-4xl mx-auto">
      {activity && (
        <div className="mb-8">
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <img 
              src={activity.thumbnail_url} 
              alt={activity.name}
              className="w-full h-64 object-cover"
            />
            <div className="p-6">
              <h1 className="text-3xl font-bold mb-4">{activity.name}</h1>
              <p className="text-gray-600 mb-6">{activity.description}</p>
              <Link
                to={`/study_activities/${id}/launch`}
                className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 inline-block"
              >
                Launch Activity
              </Link>
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg shadow">
        <div className="p-6">
          <h2 className="text-xl font-semibold mb-4">Study Sessions</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-3">ID</th>
                  <th className="text-left py-3">Group</th>
                  <th className="text-left py-3">Start Time</th>
                  <th className="text-left py-3">End Time</th>
                  <th className="text-left py-3">Items</th>
                </tr>
              </thead>
              <tbody>
                {sessionsData?.items.map((session) => (
                  <tr key={session.id} className="border-b hover:bg-gray-50">
                    <td className="py-3">
                      <Link 
                        to={`/study_sessions/${session.id}`}
                        className="text-blue-600 hover:underline"
                      >
                        {session.id}
                      </Link>
                    </td>
                    <td className="py-3">{session.group_name}</td>
                    <td className="py-3">{format(new Date(session.start_time), 'PPp')}</td>
                    <td className="py-3">{format(new Date(session.end_time), 'PPp')}</td>
                    <td className="py-3">{session.review_items_count}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {sessionsData?.pagination && (
            <Pagination
              currentPage={sessionsData.pagination.current_page}
              totalPages={sessionsData.pagination.total_pages}
              onPageChange={setPage}
            />
          )}
        </div>
      </div>
    </div>
  );
} 