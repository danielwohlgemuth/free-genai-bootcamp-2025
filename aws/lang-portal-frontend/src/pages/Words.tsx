import { useEffect, useState } from 'react'
import { api } from '@/services/api'
import { WordCard } from '@/components/words/WordCard'
import type { Word, PaginatedResponse } from '@/types/api'
import { useAuth } from 'react-oidc-context'
import { Link } from 'react-router-dom'

export function Words() {
  const [words, setWords] = useState<Word[]>([])
  const [loading, setLoading] = useState(true)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const auth = useAuth();

  useEffect(() => {
    async function fetchWords() {
      try {
        const token = auth.user?.access_token || '';
        const response = await api.get<PaginatedResponse<Word>>(
          token,
          `/words?page=${currentPage}`
        )
        
        if (response.data) {
          setWords(response.data.items)
          setTotalPages(response.data.pagination.total_pages)
        }
      } catch (error) {
        console.error('Error fetching words:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchWords()
  }, [currentPage])

  if (loading) {
    return <div className="container mx-auto px-4 py-8">Loading...</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Vocabulary Words</h1>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {words.length === 0 ? (
          <div className="rounded-lg border bg-card p-4">
            <p className="text-sm text-muted-foreground">No words found. Import initial data from <Link to="/settings" className="text-primary">Settings</Link>.</p>
          </div>
        ) : (
          words.map((word) => (
            <WordCard key={word.id} word={word} />
          ))
        )}
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