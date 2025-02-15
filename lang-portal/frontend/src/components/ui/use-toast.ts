import { useState, useCallback } from "react"

interface Toast {
  id: number
  title?: string
  description?: string
  variant?: "default" | "destructive"
}

export function useToast() {
  const [toasts, setToasts] = useState<Toast[]>([])

  const toast = useCallback(({ title, description, variant }: Omit<Toast, "id">) => {
    setToasts((current) => [
      ...current,
      { id: Date.now(), title, description, variant },
    ])
  }, [])

  return { toast, toasts }
} 