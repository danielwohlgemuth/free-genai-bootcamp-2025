import { createContext, useCallback, useContext, useState } from "react"

type Toast = {
  id: number
  description?: string
  variant?: "success" | "error"
}

type ToastProviderProps = {
  children: React.ReactNode
}


type ToastProviderState = {
  toasts: Toast[]
  toast: (toast: Omit<Toast, "id">) => void
  dismissToast: (id: number) => void
}

const ToastProviderContext = createContext<ToastProviderState | undefined>(undefined)

export function ToastProvider({
  children,
}: ToastProviderProps) {
  const [toasts, setToasts] = useState<Toast[]>([])

  const toast = useCallback(({ description, variant }: Omit<Toast, "id">) => {
    setToasts((current) => [
      ...current,
      { id: Date.now(), description, variant },
    ])
  }, [])
  
  const dismissToast = useCallback((id: number) => {
    setToasts((current) => current.filter((toast) => toast.id !== id))
  }, [])

  return (
    <ToastProviderContext.Provider value={{ toasts, toast, dismissToast }}>
      {children}
    </ToastProviderContext.Provider>
  )
}

export const useToast = () => {
  const context = useContext(ToastProviderContext)
  if (!context) throw new Error("useToast must be used within a ToastProvider")
  return context
} 