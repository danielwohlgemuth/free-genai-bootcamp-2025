import { Word } from '@/types/api'

interface WordCardProps {
  word: Word
}

export function WordCard({ word }: WordCardProps) {
  const successRate = word.correct_count + word.wrong_count > 0
    ? Math.round((word.correct_count / (word.correct_count + word.wrong_count)) * 100)
    : 0

  return (
    <div className="rounded-lg border bg-card p-4">
      <div className="space-y-2">
        <div className="text-xl font-medium">{word.japanese}</div>
        <div className="text-sm text-muted-foreground">{word.romaji}</div>
        <div className="text-sm">{word.english}</div>
        <div className="flex justify-between text-sm text-muted-foreground pt-2 border-t">
          <span>Success rate: {successRate}%</span>
          <span>Reviews: {word.correct_count + word.wrong_count}</span>
        </div>
      </div>
    </div>
  )
} 