import { forwardRef } from "react"
import { mergeClasses } from "@/lib/utils"

interface ToastProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "success" | "error"
  description?: string
  onDismiss?: () => void
}

export const Toast = forwardRef<HTMLDivElement, ToastProps>(
  ({ variant = "success", description, onDismiss }, ref) => {
    return (
      <div ref={ref} className={mergeClasses(
        "flex items-center p-4 mb-4 w-fit max-w-[400px] ml-auto",
        variant === "error" && "text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400",
        variant === "success" && "text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400"
      )} role="alert">
        <div className="text-sm font-medium flex-grow">
          {description}
        </div>
        <button type="button" className={mergeClasses(
          "ms-auto -mx-1.5 -my-1.5 items-center justify-center h-8 w-8 inline-flex",
          variant === "error" && "bg-red-50 text-red-500 rounded-lg focus:ring-2 focus:ring-red-400 p-1.5 hover:bg-red-200 dark:bg-gray-800 dark:text-red-400 dark:hover:bg-gray-700",
          variant === "success" && "bg-green-50 text-green-500 rounded-lg focus:ring-2 focus:ring-green-400 p-1.5 hover:bg-green-200 dark:bg-gray-800 dark:text-green-400 dark:hover:bg-gray-700"
        )} onClick={onDismiss} aria-label="Close">
          <span className="sr-only">Close</span>
          <svg className="w-3 h-3" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 14 14">
            <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="m1 1 6 6m0 0 6 6M7 7l6-6M7 7l-6 6" />
          </svg>
        </button>
      </div>
    )
  }
)
Toast.displayName = "Toast" 