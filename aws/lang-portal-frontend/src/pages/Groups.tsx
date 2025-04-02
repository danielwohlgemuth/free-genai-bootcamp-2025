import { useEffect, useState } from 'react'
import { api } from '@/services/api'
import { GroupCard } from '@/components/groups/GroupCard'
import type { Group, PaginatedResponse } from '@/types/api'
import { useAuth } from 'react-oidc-context'

export function Groups() {
  const [groups, setGroups] = useState<Group[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const auth = useAuth();

  useEffect(() => {
    async function fetchGroups() {
      try {
        const token = auth.user?.access_token || '';
        const response = await api.get<PaginatedResponse<Group>>(
          token,
          `/groups?page=${currentPage}`
        )
        
        if (response.data) {
          setGroups(response.data.items)
          setTotalPages(response.data.pagination.total_pages)
        }
      } catch (error) {
        console.error('Error fetching groups:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchGroups()
  }, [currentPage])

  if (loading) {
    return <div className="py-8 text-center">Loading...</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Word Groups</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {groups.map((group) => (
          <GroupCard key={group.id} group={group} />
        ))}
      </div>

      {totalPages > 1 && (
        <div className="flex justify-center gap-2 mt-8">
          <button
            onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
            disabled={currentPage === 1}
            className="px-4 py-2 rounded-md bg-primary text-primary-foreground disabled:opacity-50"
          >
            Previous
          </button>
          <span className="px-4 py-2">
            Page {currentPage} of {totalPages}
          </span>
          <button
            onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
            disabled={currentPage === totalPages}
            className="px-4 py-2 rounded-md bg-primary text-primary-foreground disabled:opacity-50"
          >
            Next
          </button>
        </div>
      )}
    </div>
  )
} 