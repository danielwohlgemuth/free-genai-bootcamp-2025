import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
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

interface Word {
  id: number;
  japanese: string;
  romaji: string;
  english: string;
  correct_count: number;
  wrong_count: number;
}

interface PaginatedResponse {
  items: Word[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_items: number;
    items_per_page: number;
  };
}

export default function StudySessionShow() {
  const { id } = useParams<{ id: string }>();
  const [page, setPage] = useState(1);

  const { data: session } = useQuery<StudySession>({
    queryKey: ['studySession', id],
    queryFn: () => fetchJson(`/study_sessions/${id}`),
  });

  const { data: wordsData } = useQuery<PaginatedResponse>({
    queryKey: ['studySessionWords', id, page],
    queryFn: () => fetchJson(`/study_sessions/${id}/words?page=${page}`),
  });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">Study Session Details</h1>

      {/* Session Details */}
      {session && (
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Activity</h3>
              <p className="mt-1 text-lg font-medium">{session.activity_name}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Group</h3>
              <p className="mt-1 text-lg font-medium">{session.group_name}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Review Items</h3>
              <p className="mt-1 text-lg font-medium">{session.review_items_count}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Start Time</h3>
              <p className="mt-1 text-lg font-medium">
                {format(new Date(session.start_time), 'PPp')}
              </p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">End Time</h3>
              <p className="mt-1 text-lg font-medium">
                {format(new Date(session.end_time), 'PPp')}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Words Review Items */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Reviewed Words</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="text-left py-3 px-4">Japanese</th>
                <th className="text-left py-3 px-4">Romaji</th>
                <th className="text-left py-3 px-4">English</th>
                <th className="text-left py-3 px-4">Correct</th>
                <th className="text-left py-3 px-4">Wrong</th>
              </tr>
            </thead>
            <tbody>
              {wordsData?.items.map((word) => (
                <tr key={word.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <Link 
                      to={`/words/${word.id}`}
                      className="text-blue-600 hover:underline"
                    >
                      {word.japanese}
                    </Link>
                  </td>
                  <td className="py-3 px-4">{word.romaji}</td>
                  <td className="py-3 px-4">{word.english}</td>
                  <td className="py-3 px-4 text-green-600">{word.correct_count}</td>
                  <td className="py-3 px-4 text-red-600">{word.wrong_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {wordsData?.pagination && (
          <div className="p-4 border-t">
            <Pagination
              currentPage={wordsData.pagination.current_page}
              totalPages={wordsData.pagination.total_pages}
              onPageChange={setPage}
            />
          </div>
        )}
      </div>
    </div>
  );
} 