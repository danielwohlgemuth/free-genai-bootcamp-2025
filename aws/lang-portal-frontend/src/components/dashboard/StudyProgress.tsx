interface StudyProgressProps {
  totalWordsStudied: number
  totalAvailableWords: number
}

export function StudyProgress({ totalWordsStudied, totalAvailableWords }: StudyProgressProps) {
  const percentage = Math.round((totalWordsStudied / totalAvailableWords) * 100)

  return (
    <div className="rounded-lg border bg-card p-4 text-card-foreground shadow-sm">
      <h3 className="text-sm font-medium text-muted-foreground mb-2">Study Progress</h3>
      <div className="space-y-2">
        <div className="h-2 w-full bg-gray-200 rounded-full">
          <div
            className="h-2 bg-primary rounded-full transition-all duration-300"
            style={{ width: `${percentage}%` }}
          />
        </div>
        <div className="flex justify-between text-sm text-muted-foreground">
          <span>{totalWordsStudied} words studied</span>
          <span>{totalAvailableWords} total words</span>
        </div>
      </div>
    </div>
  )
} 