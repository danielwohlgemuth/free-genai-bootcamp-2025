import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { fetchJson } from '../api/client';

type Theme = 'light' | 'dark' | 'system';

export default function Settings() {
  const navigate = useNavigate();
  const [theme, setTheme] = useState<Theme>('system');
  const [isConfirmingReset, setIsConfirmingReset] = useState(false);
  const [isConfirmingFullReset, setIsConfirmingFullReset] = useState(false);

  const resetHistoryMutation = useMutation({
    mutationFn: () => fetchJson('/reset_history', { method: 'POST' }),
    onSuccess: () => {
      navigate('/dashboard');
    },
  });

  const fullResetMutation = useMutation({
    mutationFn: () => fetchJson('/full_reset', { method: 'POST' }),
    onSuccess: () => {
      navigate('/dashboard');
    },
  });

  const handleThemeChange = (newTheme: Theme) => {
    setTheme(newTheme);
    // Here you would typically persist the theme preference
    // and update the application's theme
  };

  const handleResetHistory = () => {
    if (isConfirmingReset) {
      resetHistoryMutation.mutate();
      setIsConfirmingReset(false);
    } else {
      setIsConfirmingReset(true);
      setIsConfirmingFullReset(false);
    }
  };

  const handleFullReset = () => {
    if (isConfirmingFullReset) {
      fullResetMutation.mutate();
      setIsConfirmingFullReset(false);
    } else {
      setIsConfirmingFullReset(true);
      setIsConfirmingReset(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">Settings</h1>

      {/* Theme Selection */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Theme</h2>
        <div className="space-y-2">
          {(['light', 'dark', 'system'] as Theme[]).map((themeOption) => (
            <label key={themeOption} className="flex items-center space-x-2">
              <input
                type="radio"
                name="theme"
                value={themeOption}
                checked={theme === themeOption}
                onChange={() => handleThemeChange(themeOption)}
                className="text-blue-600"
              />
              <span className="capitalize">{themeOption}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Reset History */}
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-xl font-semibold mb-4">Reset History</h2>
        <p className="text-gray-600 mb-4">
          This will delete all study sessions and word review items.
        </p>
        <button
          onClick={handleResetHistory}
          disabled={resetHistoryMutation.isPending}
          className={`w-full py-2 px-4 rounded-lg ${
            isConfirmingReset
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-blue-600 hover:bg-blue-700'
          } text-white transition-colors`}
        >
          {resetHistoryMutation.isPending
            ? 'Resetting...'
            : isConfirmingReset
            ? 'Click again to confirm reset'
            : 'Reset History'}
        </button>
      </div>

      {/* Full Reset */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Full Reset</h2>
        <p className="text-gray-600 mb-4">
          This will drop all tables and re-create with seed data.
        </p>
        <button
          onClick={handleFullReset}
          disabled={fullResetMutation.isPending}
          className={`w-full py-2 px-4 rounded-lg ${
            isConfirmingFullReset
              ? 'bg-red-600 hover:bg-red-700'
              : 'bg-blue-600 hover:bg-blue-700'
          } text-white transition-colors`}
        >
          {fullResetMutation.isPending
            ? 'Resetting...'
            : isConfirmingFullReset
            ? 'Click again to confirm full reset'
            : 'Full Reset'}
        </button>
      </div>
    </div>
  );
} 