import { Toast } from "../ui/toast";
import { useAuth } from "react-oidc-context";
import { useToast } from "@/components/toast-provider";
import { useEffect } from 'react'
import { Link, Outlet, useLocation } from 'react-router-dom'

export function MainLayout() {
  const location = useLocation()
  const auth = useAuth();
  const { toasts, dismissToast } = useToast();

  if (auth.isLoading) {
    return <div>Loading...</div>;
  }

  if (auth.error) {
    return <div>Authentication error: {auth.error.message}. <button onClick={() => window.location.reload()} className="text-primary">Reload page</button>.</div>;
  }

  if (!auth.isAuthenticated) {
    useEffect(() => {
      auth.signinRedirect();
    }, []);
    return null;
  }

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/study', label: 'Study' },
    { path: '/words', label: 'Words' },
    { path: '/groups', label: 'Groups' },
    { path: '/settings', label: 'Settings' },
  ]

  return (
    <div className="min-h-screen bg-background">
      <nav className="border-b bg-card">
        <div className="container mx-auto px-4">
          <div className="flex h-16 items-center justify-between">
            <div className="font-bold text-xl">
              <Link to="/">Language Portal</Link>
            </div>
            <div className="flex gap-6">
              {navItems.map(({ path, label }) => (
                <Link
                  key={path}
                  to={path}
                  className={`text-sm font-medium transition-colors hover:text-primary ${
                    location.pathname === path ? 'text-primary' : 'text-muted-foreground'
                    }`}
                >
                  {label}
                </Link>
              ))}
            </div>
          </div>
        </div>
      </nav>

      <main>
        <div className="relative">
          <div className="absolute top-4 right-4 z-50">
            {toasts.map((toast) => (
              <Toast
                key={toast.id}
                variant={toast.variant}
                description={toast.description}
                onDismiss={() => dismissToast(toast.id)}
                className="m-2"
              />
            ))}
          </div>
        </div>

        <Outlet />
      </main>
    </div>
  )
}