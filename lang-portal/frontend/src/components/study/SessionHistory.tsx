import { StudySession } from '@/types/api'

interface SessionHistoryProps {
  sessions: StudySession[]
}

export function SessionHistory({ sessions }: SessionHistoryProps) {
  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold mb-4">Recent Sessions</h2>
      
      {sessions.length === 0 ? (
        <div className="rounded-lg border bg-card p-4">
          <p className="text-sm text-muted-foreground">No study sessions yet</p>
        </div>
      ) : (
        sessions.map((session) => (
          <div 
            key={session.id}
            className="rounded-lg border bg-card p-4 space-y-2"
          >
            <div className="flex justify-between items-start">
              <div>
                <h3 className="font-medium">{session.activity_name}</h3>
                <p className="text-sm text-muted-foreground">{session.group_name}</p>
              </div>
              <span className="text-sm text-muted-foreground">
                {new Date(session.start_time).toLocaleDateString()}
              </span>
            </div>
            <div className="text-sm text-muted-foreground">
              Words reviewed: {session.review_items_count}
            </div>
          </div>
        ))
      )}
    </div>
  )
} 