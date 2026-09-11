import axios from 'axios';
import type { 
  StockSearchResponse, 
  StockOverviewResponse, 
  StrategiesResponse, 
  BacktestRequest, 
  BacktestResponse,
  ErrorResponse
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const searchStocks = async (query: string): Promise<StockSearchResponse> => {
  const response = await apiClient.get('/api/stocks/search', {
    params: { q: query },
  });
  return response.data;
};

export const getStockOverview = async (ticker: string): Promise<StockOverviewResponse> => {
  const response = await apiClient.get(`/api/stocks/${ticker}/overview`);
  return response.data;
};

export const getStrategies = async (): Promise<StrategiesResponse> => {
  const response = await apiClient.get('/api/strategies');
  return response.data;
};

export const runBacktest = async (request: BacktestRequest): Promise<BacktestResponse> => {
  const response = await apiClient.post('/api/backtest', request);
  return response.data;
};

export interface ApiError {
  message: string;
  status?: number;
}

export const handleApiError = (error: any): ApiError => {
  if (axios.isAxiosError(error)) {
    const errorData = error.response?.data as ErrorResponse;
    return {
      message: errorData?.detail || error.message,
      status: error.response?.status,
    };
  }
  return {
    message: error instanceof Error ? error.message : 'An unexpected error occurred',
  };
};
