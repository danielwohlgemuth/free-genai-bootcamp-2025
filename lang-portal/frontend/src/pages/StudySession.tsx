import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@/services/api'
import type { Word } from '@/types/api'

interface StudySessionDetails {
  id: number
  activity_name: string
  activity_type: string
  group_name: string
}

interface WordsResponse {
  items: Word[]
}

export function StudySession() {
  const { sessionId } = useParams()
  const navigate = useNavigate()
  const [session, setSession] = useState<StudySessionDetails | null>(null)
  const [words, setWords] = useState<Word[]>([])
  const [currentWordIndex, setCurrentWordIndex] = useState(0)
  const [loading, setLoading] = useState(true)
  const [userAnswer, setUserAnswer] = useState('')

  useEffect(() => {
    let mounted = true

    async function fetchSessionData() {
      try {
        const [sessionRes, wordsRes] = await Promise.all([
          api.get<StudySessionDetails>(`/study_sessions/${sessionId}`),
          api.get<WordsResponse>(`/study_sessions/${sessionId}/next_words`),
        ])

        console.log('sessionRes', sessionRes)
        console.log('wordsRes', wordsRes)

        if (mounted) {
          setSession(sessionRes.data || null)
          setWords(wordsRes.data?.items || [] )
          setLoading(false)
        }
      } catch (error) {
        console.error('Error fetching session data:', error)
        if (mounted) {
          setLoading(false)
        }
      }
    }

    fetchSessionData()
    return () => { mounted = false }
  }, [sessionId])

  const checkAnswer = async () => {
    if (!session) return

    const currentWord = words[currentWordIndex]
    const isCorrect = session.activity_type === 'ja_to_en' 
      ? userAnswer.toLowerCase().trim() === currentWord.english.toLowerCase()
      : userAnswer.toLowerCase().trim() === currentWord.japanese.toLowerCase()

    try {
      await api.post(`/study_sessions/${sessionId}/words/${currentWord.id}/review`, {
        correct: isCorrect
      })

      setUserAnswer('')
      if (currentWordIndex < words.length - 1) {
        setCurrentWordIndex(prev => prev + 1)
      } else {
        navigate('/study')
      }
    } catch (error) {
      console.error('Error submitting answer:', error)
    }
  }

  if (loading) {
    return <div className="py-8 text-center">Loading...</div>
  }

  if (!session) {
    return (
      <div className="py-8 text-center">
        <div>Session not found</div>
        <button
          onClick={() => navigate('/study')}
          className="mt-4 px-6 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Back to Study Activities
        </button>
      </div>
    )
  }

  if (!words.length) {
    return (
      <div className="py-8 text-center">
        <div>All words have been studied</div>
        <button
          onClick={() => navigate('/study')}
          className="mt-4 px-6 py-2 rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
        >
          Back to Study Activities
        </button>
      </div>
    )
  }
  
  if (!['ja_to_en', 'en_to_ja'].includes(session.activity_type)) {
    return <div className="py-8 text-center">Unsupported activity type: {session.activity_type}</div>
  }

  const currentWord = words[currentWordIndex]
  const isJapaneseToEnglish = session.activity_type === 'ja_to_en'
  const questionText = isJapaneseToEnglish ? currentWord.japanese : currentWord.english
  const placeholderText = isJapaneseToEnglish ? 'Enter English translation' : 'Enter Japanese word'

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-2xl mx-auto">
        <div className="mb-8">
          <h1 className="text-2xl font-bold mb-2">{session.activity_name}</h1>
          <p className="text-muted-foreground">{session.group_name}</p>
        </div>

        <div className="rounded-lg border bg-card p-6 space-y-6">
          <div className="text-center">
            <p className="text-xl mb-2">{questionText}</p>
            {isJapaneseToEnglish && (
              <p className="text-sm text-muted-foreground">{currentWord.romaji}</p>
            )}
          </div>

          <div className="flex gap-4">
            <input
              type="text"
              value={userAnswer}
              onChange={(e) => setUserAnswer(e.target.value)}
              placeholder={placeholderText}
              className="px-4 py-2 rounded-md border w-full max-w-md bg-background text-foreground"
              onKeyDown={(e) => e.key === 'Enter' && checkAnswer()}
            />
            <button
              onClick={checkAnswer}
              className="px-6 py-3 rounded-md bg-primary text-primary-foreground hover:bg-primary/90"
            >
              Check
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