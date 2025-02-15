import { Link, useLocation } from 'react-router-dom';

const navItems = [
  { path: '/dashboard', label: 'Dashboard' },
  { path: '/study_activities', label: 'Study Activities' },
  { path: '/words', label: 'Words' },
  { path: '/groups', label: 'Groups' },
  { path: '/study_sessions', label: 'Study Sessions' },
  { path: '/settings', label: 'Settings' },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen flex">
      {/* Sidebar Navigation */}
      <nav className="w-64 bg-gray-800 text-white p-4">
        <h1 className="text-xl font-bold mb-8 px-4">Japanese Study Portal</h1>
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.path}>
              <Link
                to={item.path}
                className={`block px-4 py-2 rounded-lg ${
                  location.pathname === item.path
                    ? 'bg-blue-600'
                    : 'hover:bg-gray-700'
                }`}
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Main Content */}
      <main className="flex-1 bg-gray-100">
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
} 