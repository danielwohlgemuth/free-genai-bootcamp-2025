import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { useState } from 'react';
import { fetchJson } from '../../api/client';
import { Pagination } from '../../components/shared/Pagination';

interface GroupDetails {
  id: number;
  name: string;
  stats: {
    total_word_count: number;
  };
}

interface Word {
  id: number;
  japanese: string;
  romaji: string;
  english: string;
  correct_count: number;
  wrong_count: number;
}

interface StudySession {
  id: number;
  activity_name: string;
  group_name: string;
  start_time: string;
  end_time: string;
  review_items_count: number;
}

interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_items: number;
    items_per_page: number;
  };
}

export default function GroupShow() {
  const { id } = useParams<{ id: string }>();
  const [wordsPage, setWordsPage] = useState(1);
  const [sessionsPage, setSessionsPage] = useState(1);

  const { data: group } = useQuery<GroupDetails>({
    queryKey: ['group', id],
    queryFn: () => fetchJson(`/groups/${id}`),
  });

  const { data: wordsData } = useQuery<PaginatedResponse<Word>>({
    queryKey: ['groupWords', id, wordsPage],
    queryFn: () => fetchJson(`/groups/${id}/words?page=${wordsPage}`),
  });

  const { data: sessionsData } = useQuery<PaginatedResponse<StudySession>>({
    queryKey: ['groupSessions', id, sessionsPage],
    queryFn: () => fetchJson(`/groups/${id}/study_sessions?page=${sessionsPage}`),
  });

  return (
    <div>
      <h1 className="text-3xl font-bold mb-8">{group?.name}</h1>

      {/* Group Statistics */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">Group Statistics</h2>
        <div className="text-lg">
          Total Words: <span className="font-semibold">{group?.stats.total_word_count}</span>
        </div>
      </div>

      {/* Words in Group */}
      <div className="bg-white rounded-lg shadow overflow-hidden mb-8">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Words in Group</h2>
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
              onPageChange={setWordsPage}
            />
          </div>
        )}
      </div>

      {/* Study Sessions */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="p-6 border-b">
          <h2 className="text-xl font-semibold">Study Sessions</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="text-left py-3 px-4">ID</th>
                <th className="text-left py-3 px-4">Activity</th>
                <th className="text-left py-3 px-4">Start Time</th>
                <th className="text-left py-3 px-4">End Time</th>
                <th className="text-left py-3 px-4">Items</th>
              </tr>
            </thead>
            <tbody>
              {sessionsData?.items.map((session) => (
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
                  <td className="py-3 px-4">{new Date(session.start_time).toLocaleString()}</td>
                  <td className="py-3 px-4">{new Date(session.end_time).toLocaleString()}</td>
                  <td className="py-3 px-4">{session.review_items_count}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {sessionsData?.pagination && (
          <div className="p-4 border-t">
            <Pagination
              currentPage={sessionsData.pagination.current_page}
              totalPages={sessionsData.pagination.total_pages}
              onPageChange={setSessionsPage}
            />
          </div>
        )}
      </div>
    </div>
  );
} 