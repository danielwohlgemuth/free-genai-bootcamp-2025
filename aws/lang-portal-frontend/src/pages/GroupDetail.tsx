import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { api } from '@/services/api'
import { WordCard } from '@/components/words/WordCard'
import { SessionHistory } from '@/components/study/SessionHistory'
import type { Word, StudySession } from '@/types/api'
import { useAuth } from 'react-oidc-context'

interface GroupDetails {
  id: number
  name: string
  stats: {
    total_word_count: number
  }
}

export function GroupDetail() {
  const { groupId } = useParams()
  const [group, setGroup] = useState<GroupDetails | null>(null)
  const [words, setWords] = useState<Word[]>([])
  const [sessions, setSessions] = useState<StudySession[]>([])
  const [loading, setLoading] = useState(true)
  const auth = useAuth();

  useEffect(() => {
    async function fetchGroupData() {
      try {
        const token = auth.user?.access_token || '';
        const [groupRes, wordsRes, sessionsRes] = await Promise.all([
          api.get<GroupDetails>(token, `/groups/${groupId}`),
          api.get<{ items: Word[] }>(token, `/groups/${groupId}/words`),
          api.get<{ items: StudySession[] }>(token, `/groups/${groupId}/study_sessions`)
        ])

        if (groupRes.data) setGroup(groupRes.data)
        if (wordsRes.data) setWords(wordsRes.data.items)
        if (sessionsRes.data) setSessions(sessionsRes.data.items)
      } catch (error) {
        console.error('Error fetching group data:', error)
      } finally {
        setLoading(false)
      }
    }

    if (groupId) {
      fetchGroupData()
    }
  }, [groupId])

  if (loading) {
    return <div className="py-8 text-center">Loading...</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <header className="mb-8">
        <h1 className="text-2xl font-bold">{group?.name}</h1>
        <p className="text-muted-foreground">
          {group?.stats.total_word_count} words in this group
        </p>
      </header>

      <div className="grid md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold mb-4">Words</h2>
          <div className="grid gap-4">
            {words.map((word) => (
              <WordCard key={word.japanese} word={word} />
            ))}
          </div>
        </div>

        <div>
          <SessionHistory sessions={sessions} />
        </div>
      </div>
    </div>
  )
} 