import { useState, useEffect } from 'react'
import { api } from '@/services/api'

interface ActivityCardProps {
  id: number
  name: string
  thumbnailUrl: string
  description: string
  type: string
  onStart: (activityId: number, groupId: number) => void
}

interface Group {
  id: number
  name: string
}

interface GroupsResponse {
  items: Group[]
}

export function ActivityCard({ id, name, thumbnailUrl, description, type, onStart }: ActivityCardProps) {
  const [groups, setGroups] = useState<Group[]>([])
  const [selectedGroupId, setSelectedGroupId] = useState<number>(0)

  useEffect(() => {
    let mounted = true

    // Fetch groups only for translation activities
    if (type === 'ja_to_en' || type === 'en_to_ja') {
      const fetchGroups = async () => {
        try {
          const response = await api.get<GroupsResponse>('/groups')
          if (mounted) {  // Only update state if component is still mounted
            setGroups(response.data?.items || [])
            if (response.data?.items && response.data.items.length > 0) {
              setSelectedGroupId(response.data.items[0].id)
            }
          }
        } catch (error) {
          if (mounted) {
            console.error('Error fetching groups:', error)
            setGroups([])
          }
        }
      }
      fetchGroups()
    }

    // Cleanup function
    return () => {
      mounted = false
    }
  }, [type])

  const needsGroupSelection = type === 'ja_to_en' || type === 'en_to_ja'

  return (
    <div className="rounded-lg border bg-card shadow-sm">
      <img 
        src={thumbnailUrl} 
        alt={name}
        className="w-full h-48 object-cover rounded-t-lg"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2">{name}</h3>
        <p className="text-sm text-muted-foreground mb-4">{description}</p>
        
        {needsGroupSelection && groups && groups.length > 0 && (
          <div className="mb-4">
            <select
              value={selectedGroupId}
              onChange={(e) => setSelectedGroupId(Number(e.target.value))}
              className="w-full p-2 border rounded-md mb-2 bg-background text-foreground"
            >
              <option value={0} disabled>Select a word group</option>
              {groups.map((group) => (
                <option key={group.id} value={group.id}>
                  {group.name}
                </option>
              ))}
            </select>
          </div>
        )}

        <button
          onClick={() => onStart(id, selectedGroupId)}
          disabled={needsGroupSelection && !selectedGroupId}
          className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Start Activity
        </button>
      </div>
    </div>
  )
} 