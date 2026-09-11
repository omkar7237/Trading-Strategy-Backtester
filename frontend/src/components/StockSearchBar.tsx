import React, { useState, useCallback, useRef, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Search, X } from 'lucide-react';
import { searchStocks } from '../api';
import type { StockSearchResult } from '../types';

interface StockSearchBarProps {
  onStockSelect?: (ticker: string) => void;
}

export const StockSearchBar: React.FC<StockSearchBarProps> = ({ onStockSelect }) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const navigate = useNavigate();
  const wrapperRef = useRef<HTMLDivElement>(null);

  const { data, isLoading, isError } = useQuery({
    queryKey: ['stockSearch', query],
    queryFn: () => searchStocks(query),
    enabled: query.length >= 2,
    staleTime: 5 * 60 * 1000,
  });

  const handleSelect = useCallback((result: StockSearchResult) => {
    setQuery('');
    setIsOpen(false);
    if (onStockSelect) {
      onStockSelect(result.symbol);
    } else {
      navigate(`/stock/${result.symbol}`);
    }
  }, [navigate, onStockSelect]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
    setIsOpen(true);
  };

  const handleClear = () => {
    setQuery('');
    setIsOpen(false);
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={wrapperRef} className="relative w-full max-w-md">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={() => query.length >= 2 && setIsOpen(true)}
          placeholder="Search stocks by ticker or name..."
          className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        />
        {query && (
          <button
            onClick={handleClear}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      {isOpen && query.length >= 2 && (
        <div className="absolute z-50 w-full mt-1 bg-white rounded-lg shadow-lg border border-gray-200 max-h-80 overflow-y-auto">
          {isLoading && (
            <div className="p-4 text-center text-gray-500">Searching...</div>
          )}
          
          {isError && (
            <div className="p-4 text-center text-danger">Error searching stocks</div>
          )}

          {!isLoading && !isError && data?.results.length === 0 && (
            <div className="p-4 text-center text-gray-500">No results found</div>
          )}

          {!isLoading && !isError && data?.results.map((result) => (
            <button
              key={result.symbol}
              onClick={() => handleSelect(result)}
              className="w-full px-4 py-3 text-left hover:bg-gray-50 border-b border-gray-100 last:border-b-0 transition-colors"
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-semibold text-gray-900">{result.symbol}</span>
                  <span className="ml-2 text-sm text-gray-500">{result.name}</span>
                </div>
                <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded">
                  {result.exchange}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
