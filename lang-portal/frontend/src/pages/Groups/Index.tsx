import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { useState } from 'react';
import { fetchJson } from '../../api/client';
import { Pagination } from '../../components/shared/Pagination';

interface Group {
  id: number;
  name: string;
  word_count: number;
}

interface PaginatedResponse {
  items: Group[];
  pagination: {
    current_page: number;
    total_pages: number;
    total_items: number;
    items_per_page: number;
  };
}

export default function GroupsIndex() {
  const [page, setPage] = useState(1);

  const { data, isLoading } = useQuery<PaginatedResponse>({
    queryKey: ['groups', page],
    queryFn: () => fetchJson(`/groups?page=${page}`),
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
      <h1 className="text-3xl font-bold mb-8">Word Groups</h1>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="bg-gray-50 border-b">
                <th className="text-left py-3 px-4">Group Name</th>
                <th className="text-left py-3 px-4">Word Count</th>
              </tr>
            </thead>
            <tbody>
              {data?.items.map((group) => (
                <tr key={group.id} className="border-b hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <Link 
                      to={`/groups/${group.id}`}
                      className="text-blue-600 hover:underline"
                    >
                      {group.name}
                    </Link>
                  </td>
                  <td className="py-3 px-4">{group.word_count}</td>
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