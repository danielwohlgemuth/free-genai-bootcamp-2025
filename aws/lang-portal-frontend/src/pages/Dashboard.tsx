import { useEffect, useState } from 'react'
import { api } from '@/services/api'
import { StatsCard } from '@/components/dashboard/StatsCard'
import { StudyProgress } from '@/components/dashboard/StudyProgress'
import { LastStudySession } from '@/components/dashboard/LastStudySession'
import type { DashboardStats, StudySession } from '@/types/api'

interface StudyProgressData {
  total_words_studied: number
  total_available_words: number
}

export function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [progress, setProgress] = useState<StudyProgressData | null>(null)
  const [lastSession, setLastSession] = useState<StudySession | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    let mounted = true

    const fetchDashboardData = async () => {
      try {
        const [statsRes, progressRes, sessionRes] = await Promise.all([
          api.get<DashboardStats>('/dashboard/quick-stats'),
          api.get<StudyProgressData>('/dashboard/study_progress'),
          api.get<StudySession>('/dashboard/last_study_session'),
        ])

        if (mounted) {
          if (statsRes.data) setStats(statsRes.data)
          if (progressRes.data) setProgress(progressRes.data)
          if (sessionRes.data) setLastSession(sessionRes.data)
          setLoading(false)
        }
      } catch (error) {
        if (mounted) {
          console.error('Error fetching dashboard data:', error)
          setLoading(false)
        }
      }
    }

    fetchDashboardData()

    return () => {
      mounted = false
    }
  }, [])

  if (loading) {
    return <div className="container mx-auto px-4 py-8">Loading...</div>
  }

  if (!stats) {
    return <div className="container mx-auto px-4 py-8">Error loading dashboard</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid gap-4 md:grid-cols-4 mb-6">
        <StatsCard 
          title="Success Rate"
          value={`${stats?.success_rate ?? 0}%`}
        />
        <StatsCard 
          title="Study Sessions"
          value={stats?.total_study_sessions ?? 0}
        />
        <StatsCard 
          title="Active Groups"
          value={stats?.total_active_groups ?? 0}
        />
        <StatsCard 
          title="Study Streak"
          value={stats?.study_streak_days ?? 0}
          description="days"
        />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {progress && (
        <StudyProgress 
            totalWordsStudied={progress.total_words_studied}
            totalAvailableWords={progress.total_available_words}
        />
        )}
        <LastStudySession session={lastSession} />
      </div>
    </div>
  )
} 