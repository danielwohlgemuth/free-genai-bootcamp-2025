import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { fetchJson } from '../../api/client';

interface Group {
  id: number;
  name: string;
}

interface LaunchResponse {
  id: number;
  group_id: number;
}

export default function StudyActivityLaunch() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [selectedGroupId, setSelectedGroupId] = useState<number>();

  const { data: activity } = useQuery({
    queryKey: ['studyActivity', id],
    queryFn: () => fetchJson(`/study_activities/${id}`),
  });

  const { data: groups } = useQuery<Group[]>({
    queryKey: ['groups'],
    queryFn: () => fetchJson('/groups'),
  });

  const launchMutation = useMutation({
    mutationFn: () => 
      fetchJson<LaunchResponse>('/study_activities', {
        method: 'POST',
        body: JSON.stringify({
          group_id: selectedGroupId,
          study_activity_id: id,
        }),
      }),
    onSuccess: (data) => {
      navigate(`/study_sessions/${data.id}`);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedGroupId) {
      launchMutation.mutate();
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Launch Study Activity</h1>
      
      <div className="bg-white rounded-lg shadow p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Group
            </label>
            <select
              className="w-full border rounded-lg p-2"
              value={selectedGroupId}
              onChange={(e) => setSelectedGroupId(Number(e.target.value))}
              required
            >
              <option value="">Select a group...</option>
              {groups?.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>

          <button
            type="submit"
            disabled={!selectedGroupId || launchMutation.isPending}
            className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {launchMutation.isPending ? 'Launching...' : 'Launch Now'}
          </button>
        </form>
      </div>
    </div>
  );
} 