import { StudySession } from '@/types/api'

interface LastStudySessionProps {
  session: StudySession | null
}

export function LastStudySession({ session }: LastStudySessionProps) {
  if (!session) {
    return (
      <div className="rounded-lg border bg-card p-4 text-card-foreground shadow-sm">
        <h3 className="text-sm font-medium text-muted-foreground">Last Study Session</h3>
        <p className="mt-2 text-sm">No study sessions yet</p>
      </div>
    )
  }

  const date = new Date(session.start_time)
  const formattedDate = new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short'
  }).format(date)

  return (
    <div className="rounded-lg border bg-card p-4 text-card-foreground shadow-sm">
      <h3 className="text-sm font-medium text-muted-foreground">Last Study Session</h3>
      <div className="mt-2 space-y-2">
        <div className="flex justify-between">
          <span className="text-sm font-medium">{session.activity_name}</span>
          <span className="text-sm text-muted-foreground">{formattedDate}</span>
        </div>
        <p className="text-sm text-muted-foreground">
          Group: {session.group_name}
        </p>
        <p className="text-sm text-muted-foreground">
          Words reviewed: {session.review_items_count}
        </p>
      </div>
    </div>
  )
} 