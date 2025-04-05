import { Link, Outlet, useLocation } from 'react-router-dom'
import { useAuth } from "react-oidc-context";
import { useEffect } from 'react';

export function MainLayout() {
  const location = useLocation()
  const auth = useAuth();

  if (auth.isLoading) {
    return <div>Loading...</div>;
  }

  if (auth.error) {
    return <div>Authentication error: {auth.error.message}</div>;
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
              Language Portal
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
        <Outlet />
      </main>
    </div>
  )
} 