import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { fetchJson } from '../../api/client';
import { Pagination } from '../../components/shared/Pagination';
import { format } from 'date-fns';

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

export default function StudySessionsIndex() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['studySessions', page],
    queryFn: () => fetchJson(`/study_sessions?page=${page}`),
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
      <h1 className="text-3xl font-bold mb-8">Study Sessions</h1>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="text-left py-3 px-4">ID</th>
                <th className="text-left py-3 px-4">Activity</th>
                <th className="text-left py-3 px-4">Group</th>
                <th className="text-left py-3 px-4">Start Time</th>
                <th className="text-left py-3 px-4">End Time</th>
                <th className="text-left py-3 px-4">Items</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((session) => (
                <tr key={session.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <Link 
                      to={`/study_sessions/${session.id}`}
                      className="text-blue-600 hover:underline"
                    >
                      {session.id}
                    </Link>
                  </td>
                  <td className="py-3 px-4">{session.activity_name}</td>
                  <td className="py-3 px-4">{session.group_name}</td>
                  <td className="py-3 px-4">{format(new Date(session.start_time), 'PPp')}</td>
                  <td className="py-3 px-4">{format(new Date(session.end_time), 'PPp')}</td>
                  <td className="py-3 px-4">{session.review_items_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {data?.pagination && (
          <div className="p-4 border-t">
            <Pagination
              currentPage={data.pagination.current_page}
              totalPages={data.pagination.total_pages}
              onPageChange={setPage}
            />
          </div>
        )}
      </div>
    </div>
  );
} 