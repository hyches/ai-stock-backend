import { render, screen, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TradingProvider, useTrading } from './TradingContext';
import * as queries from '@/lib/queries';
import * as api from '@/lib/api';
import { vi } from 'vitest';
import React from 'react';

// Mock the external dependencies
vi.mock('@/lib/queries');
vi.mock('@/lib/api');

const createTestQueryClient = () => new QueryClient({
  defaultOptions: {
    queries: {
      retry: false, // Turn off retries for testing
    },
  },
});

const TestComponent = () => {
  const trading = useTrading();
  return (
    <div>
      <button onClick={() => trading.buyStock('AAPL', 'Apple', 10, 150)}>Buy Stock</button>
      <span>{trading.isInWatchlist('AAPL') ? 'In Watchlist' : 'Not In Watchlist'}</span>
    </div>
  );
};

describe('TradingProvider', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.resetAllMocks();
  });

  it('provides trading context and handles buy stock action', async () => {
    const queryClient = createTestQueryClient();

    // Mock the return values of our custom hooks
    (queries.usePortfolio as vi.Mock).mockReturnValue({ data: [], isLoading: false });
    (queries.useWatchlist as vi.Mock).mockReturnValue({ data: [{ symbol: 'GOOGL' }], isLoading: false });

    // Mock the API function
    const placeOrderMock = (api.placeOrder as vi.Mock).mockResolvedValue({ success: true });

    render(
      <QueryClientProvider client={queryClient}>
        <TradingProvider>
          <TestComponent />
        </TradingProvider>
      </QueryClientProvider>
    );

    // Check initial state from mocked providers
    expect(screen.getByText('Not In Watchlist')).toBeInTheDocument();

    // Simulate user action
    const buyButton = screen.getByText('Buy Stock');
    await act(async () => {
      buyButton.click();
    });

    // Assert that the mutation was called with correct parameters
    expect(placeOrderMock).toHaveBeenCalledWith({
      symbol: 'AAPL',
      name: 'Apple',
      quantity: 10,
      price: 150,
      side: 'buy',
    });
  });

  it('correctly identifies if a stock is in the watchlist', () => {
    const queryClient = createTestQueryClient();

    (queries.usePortfolio as vi.Mock).mockReturnValue({ data: [], isLoading: false });
    (queries.useWatchlist as vi.Mock).mockReturnValue({ data: [{ symbol: 'AAPL' }], isLoading: false });

    render(
      <QueryClientProvider client={queryClient}>
        <TradingProvider>
          <TestComponent />
        </TradingProvider>
      </QueryClientProvider>
    );

    expect(screen.getByText('In Watchlist')).toBeInTheDocument();
  });
});
