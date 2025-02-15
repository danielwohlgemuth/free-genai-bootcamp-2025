import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@/services/api'
import type { Word } from '@/types/api'

interface StudySessionDetails {
  id: number
  activity_name: string
  group_name: string
}

export function StudySession() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState<StudySessionDetails | null>(null)
  const [words, setWords] = useState<Word[]>([])
  const [currentWordIndex, setCurrentWordIndex] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function fetchSessionData() {
      try {
        const [sessionRes, wordsRes] = await Promise.all([
          api.get<StudySessionDetails>(`/study_sessions/${sessionId}`),
          api.get<{ items: Word[] }>(`/study_sessions/${sessionId}/words`)
        ])

        if (sessionRes.data) setSession(sessionRes.data)
        if (wordsRes.data) setWords(wordsRes.data.items)
      } catch (error) {
        console.error('Error fetching session data:', error)
      } finally {
        setLoading(false)
      }
    }

    if (sessionId) {
      fetchSessionData()
    }
  }, [sessionId])

  const handleAnswer = async (correct: boolean) => {
    if (!session || !words[currentWordIndex]) return

    try {
      await api.post(`/study_sessions/${session.id}/words/${words[currentWordIndex].id}/review`, {
        correct
      })

      if (currentWordIndex < words.length - 1) {
        setCurrentWordIndex(prev => prev + 1)
      } else {
        navigate('/study/complete')
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
    }
  }

  if (loading) {
    return <div className="container mx-auto px-4 py-8">Loading...</div>
  }

  const currentWord = words[currentWordIndex]

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <header className="mb-8">
          <h1 className="text-2xl font-bold">{session?.activity_name}</h1>
          <p className="text-muted-foreground">{session?.group_name}</p>
        </header>

        <div className="text-center space-y-8">
          <div className="p-8 rounded-lg border bg-card">
            <div className="text-3xl mb-4">{currentWord.japanese}</div>
            <div className="text-xl text-muted-foreground mb-4">{currentWord.romaji}</div>
          </div>

          <div className="flex gap-4 justify-center">
            <button
              onClick={() => handleAnswer(false)}
              className="px-6 py-3 rounded-md bg-destructive text-destructive-foreground hover:bg-destructive/90"
            >
              Incorrect
            </button>
            <button
              onClick={() => handleAnswer(true)}
              className="px-6 py-3 rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Correct
            </button>
          </div>

          <div className="text-sm text-muted-foreground">
            Word {currentWordIndex + 1} of {words.length}
          </div>
        </div>
      </div>
    </div>
  )
} 