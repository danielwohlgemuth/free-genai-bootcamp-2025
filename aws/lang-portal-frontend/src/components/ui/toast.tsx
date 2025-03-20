import { forwardRef } from "react"
import { cn } from "@/lib/utils"

interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "destructive"
  title?: string
  description?: string
}

export const Toast = forwardRef<HTMLDivElement, ToastProps>(
  ({ className, variant = "default", title, description, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={cn(
          "pointer-events-auto relative rounded-lg border p-4 shadow-lg",
          variant === "default" && "bg-background text-foreground",
          variant === "destructive" && "bg-destructive text-destructive-foreground",
          className
        )}
        {...props}
      >
        {title && <div className="font-semibold">{title}</div>}
        {description && <div className="mt-1 text-sm">{description}</div>}
      </div>
    )
  }
)
Toast.displayName = "Toast" 