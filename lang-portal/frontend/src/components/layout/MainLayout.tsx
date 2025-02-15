import { Link, Outlet, useLocation } from 'react-router-dom'

export function MainLayout() {
  const location = useLocation()

  const navItems = [
    { path: '/', label: 'Dashboard' },
    { path: '/study', label: 'Study' },
    { path: '/words', label: 'Words' },
    { path: '/groups', label: 'Groups' },
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