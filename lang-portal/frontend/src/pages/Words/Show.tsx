import { useQuery } from '@tanstack/react-query';
import { useParams, Link } from 'react-router-dom';
import { fetchJson } from '../../api/client';

interface WordDetails {
  japanese: string;
  romaji: string;
  english: string;
  stats: {
    correct_count: number;
    wrong_count: number;
  };
  groups: {
    id: number;
    name: string;
  }[];
}

export default function WordShow() {
  const { id } = useParams<{ id: string }>();

  const { data: word, isLoading } = useQuery<WordDetails>({
    queryKey: ['word', id],
    queryFn: () => fetchJson(`/words/${id}`),
  });

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  if (!word) {
    return (
      <div className="text-center py-8">
        <h2 className="text-2xl font-bold text-gray-800">Word not found</h2>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Word Details</h1>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        {/* Word Information */}
        <div className="p-6 border-b">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-sm font-medium text-gray-500">Japanese</h3>
              <p className="mt-1 text-2xl">{word.japanese}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">Romaji</h3>
              <p className="mt-1 text-2xl">{word.romaji}</p>
            </div>
            <div>
              <h3 className="text-sm font-medium text-gray-500">English</h3>
              <p className="mt-1 text-2xl">{word.english}</p>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="p-6 border-b bg-gray-50">
          <h2 className="text-lg font-semibold mb-4">Study Statistics</h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-sm text-gray-500">Correct Answers</span>
              <p className="text-2xl font-semibold text-green-600">
                {word.stats.correct_count}
              </p>
            </div>
            <div>
              <span className="text-sm text-gray-500">Wrong Answers</span>
              <p className="text-2xl font-semibold text-red-600">
                {word.stats.wrong_count}
              </p>
            </div>
          </div>
        </div>

        {/* Word Groups */}
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Word Groups</h2>
          <div className="flex flex-wrap gap-2">
            {word.groups.map((group) => (
              <Link
                key={group.id}
                to={`/groups/${group.id}`}
                className="inline-flex items-center px-3 py-1 rounded-full bg-blue-100 text-blue-700 hover:bg-blue-200 transition-colors"
              >
                {group.name}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
} 