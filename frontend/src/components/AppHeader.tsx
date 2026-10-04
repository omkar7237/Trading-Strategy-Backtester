import React from 'react';
import { useNavigate } from 'react-router-dom';
import { StockSearchBar } from './StockSearchBar';

interface AppHeaderProps {
  /** Rendered right-aligned next to the search bar; omitted on the home page. */
  children?: React.ReactNode;
}

/**
 * Shared header for every page. The title doubles as the link home so users
 * always have one consistent way back to the dashboard.
 */
export const AppHeader: React.FC<AppHeaderProps> = ({ children }) => {
  const navigate = useNavigate();

  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 gap-4">
          <button
            onClick={() => navigate('/')}
            title="Go to home"
            aria-label="Trading Strategy Backtester — go to home"
            className="text-xl font-bold text-gray-900 hover:text-primary-600 transition-colors text-left shrink-0"
          >
            Trading Strategy Backtester
          </button>
          {children}
          <StockSearchBar />
        </div>
      </div>
    </header>
  );
};