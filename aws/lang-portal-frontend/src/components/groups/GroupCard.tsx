import { Group } from '@/types/api'
import { Link } from 'react-router-dom'

interface GroupCardProps {
  group: Group
}

export function GroupCard({ group }: GroupCardProps) {
  return (
    <Link 
      to={`/groups/${group.id}`}
      className="block rounded-lg border bg-card p-4 hover:border-primary transition-colors"
    >
      <div className="space-y-2">
        <h3 className="text-lg font-medium">{group.name}</h3>
        <p className="text-sm text-muted-foreground">
          {group.word_count} words
        </p>
      </div>
    </Link>
  )
} 