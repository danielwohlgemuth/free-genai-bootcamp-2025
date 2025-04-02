import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '@/services/api'
import { ActivityCard } from '@/components/study/ActivityCard'
import { SessionHistory } from '@/components/study/SessionHistory'
import type { StudySession } from '@/types/api'
import { useAuth } from 'react-oidc-context'

interface StudyActivity {
  id: number
  name: string
  thumbnail_url: string
  description: string
  type: string
}

export function StudyActivities() {
  const navigate = useNavigate()
  const [activities, setActivities] = useState<StudyActivity[]>([])
  const [recentSessions, setRecentSessions] = useState<StudySession[]>([])
  const [loading, setLoading] = useState(true)
  const auth = useAuth();

  useEffect(() => {
    async function fetchData() {
      try {
        const token = auth.user?.access_token || '';
        const [activitiesRes, sessionsRes] = await Promise.all([
          api.get<StudyActivity[]>(token, '/study_activities'),
          api.get<{ items: StudySession[] }>(token, '/study_sessions?limit=5')
        ])

        if (activitiesRes.data) setActivities(activitiesRes.data)
        if (sessionsRes.data) setRecentSessions(sessionsRes.data.items)
      } catch (error) {
        console.error('Error fetching study activities:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const handleStartActivity = async (activityId: number, groupId: number) => {
    try {
      const token = auth.user?.access_token || '';
      const response = await api.post<{ id: number }>(token, '/study_activities', {
        group_id: groupId,
        study_activity_id: activityId
      })

      if (response.data) {
        navigate(`/study/${response.data.id}`)
      }
    } catch (error) {
      console.error('Error starting activity:', error)
    }
  }

  if (loading) {
    return <div className="py-8 text-center">Loading...</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Study Activities</h1>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Available Activities</h2>
          <div className="grid gap-4">
            {activities.map((activity) => (
              <ActivityCard
                key={activity.id}
                id={activity.id}
                name={activity.name}
                thumbnailUrl={activity.thumbnail_url}
                description={activity.description}
                type={activity.type}
                onStart={handleStartActivity}
              />
            ))}
          </div>
        </div>

        <div>
          <SessionHistory sessions={recentSessions} />
        </div>
      </div>
    </div>
  )
} 