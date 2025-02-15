import { Link, useLocation } from 'react-router-dom';
import { colors, spacing, shadows, rounded } from '../styles/theme';
import {
  LayoutDashboard,
  BookOpen,
  AlignLeft,
  FolderKanban,
  Clock,
  Settings,
} from 'lucide-react';

const navItems = [
  { path: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { path: '/study_activities', label: 'Study Activities', icon: BookOpen },
  { path: '/words', label: 'Words', icon: AlignLeft },
  { path: '/groups', label: 'Groups', icon: FolderKanban },
  { path: '/study_sessions', label: 'Study Sessions', icon: Clock },
  { path: '/settings', label: 'Settings', icon: Settings },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Sidebar */}
      <nav className="w-72 bg-white border-r border-gray-200 fixed h-full overflow-y-auto">
        <div className="px-6 py-8">
          <Link to="/dashboard" className="block mb-8">
            <h1 className="text-2xl font-bold text-gray-800">
              Japanese Study Portal
            </h1>
          </Link>
          <ul className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center px-4 py-3 ${rounded.button} transition-all
                      ${
                        location.pathname === item.path
                          ? 'bg-primary-50 text-primary-700 font-medium translate-x-2'
                          : 'text-gray-600 hover:bg-gray-50 hover:translate-x-2'
                      }`}
                  >
                    <Icon className="w-5 h-5 mr-3" />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      </nav>

      {/* Main Content */}
      <main className="flex-1 ml-72">
        <div className={`${spacing.page} max-w-5xl mx-auto`}>
          {children}
        </div>
      </main>
    </div>
  );
} 