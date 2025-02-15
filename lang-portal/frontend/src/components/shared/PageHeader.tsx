import { useNavigate } from 'react-router-dom';
import { ChevronLeft } from 'lucide-react';
import { Button } from './Button';

interface PageHeaderProps {
  title: string;
  showBack?: boolean;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function PageHeader({ title, showBack = true, action }: PageHeaderProps) {
  const navigate = useNavigate();

  return (
    <div className="flex items-center justify-between mb-8">
      <div className="flex items-center gap-4">
        {showBack && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => navigate(-1)}
            className="flex items-center gap-2"
          >
            <ChevronLeft size={16} />
            Back
          </Button>
        )}
        <h1 className="text-3xl font-bold text-gray-800">{title}</h1>
      </div>
      {action && (
        <Button onClick={action.onClick}>{action.label}</Button>
      )}
    </div>
  );
} 