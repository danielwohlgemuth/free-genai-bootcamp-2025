import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { fetchJson } from '../../api/client';
import { Pagination } from '../../components/shared/Pagination';

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

export default function WordsIndex() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['words', page],
    queryFn: () => fetchJson(`/words?page=${page}`),
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
      <h1 className="text-3xl font-bold mb-8">Words</h1>

      <div className="bg-white rounded-lg shadow overflow-hidden">
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
              {data?.items.map((word) => (
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