interface ActivityCardProps {
  id: number
  name: string
  thumbnailUrl: string
  description: string
  onStart: (activityId: number) => void
}

export function ActivityCard({ id, name, thumbnailUrl, description, onStart }: ActivityCardProps) {
  return (
    <div className="rounded-lg border bg-card shadow-sm">
      <img 
        src={thumbnailUrl} 
        alt={name}
        className="w-full h-48 object-cover rounded-t-lg"
      />
      <div className="p-4">
        <h3 className="text-lg font-semibold mb-2">{name}</h3>
        <p className="text-sm text-muted-foreground mb-4">{description}</p>
        <button
          onClick={() => onStart(id)}
          className="w-full px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
        >
          Start Activity
        </button>
      </div>
    </div>
  )
} 