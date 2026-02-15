import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ReactQueryDevtools } from "@tanstack/react-query-devtools";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { TradingProvider } from "@/context/TradingContext";
import { StockDataProvider } from "@/context/StockDataContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import ErrorBoundary from "@/components/ErrorBoundary";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import StockDetails from "./pages/StockDetails";
import NotFound from "./pages/NotFound";
import Screener from "./pages/Screener";
import Research from "./pages/Research";
import Optimizer from "./pages/Optimizer";
import Trading from "./pages/Trading";
import Policy from "./pages/Policy";
import Reports from "./pages/Reports";
import Settings from "./pages/Settings";
import Login from "./pages/Login";
import Transactions from "./pages/Transactions";
import Investments from "./pages/Investments";

// Configure React Query with optimal settings for stock market data
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      // Cache data for 5 minutes (market data changes frequently)
      staleTime: 5 * 60 * 1000,
      // Keep unused data in cache for 10 minutes
      gcTime: 10 * 60 * 1000,
      // Retry failed requests 2 times
      retry: 2,
      // Refetch on window focus for real-time updates
      refetchOnWindowFocus: true,
      // Refetch on reconnect
      refetchOnReconnect: true,
      // Don't refetch on mount if data is fresh
      refetchOnMount: false,
    },
    mutations: {
      // Retry mutations once on failure
      retry: 1,
    },
  },
});

const App = () => (
  <ErrorBoundary>
    <ThemeProvider>
      <TradingProvider>
        <QueryClientProvider client={queryClient}>
          <ReactQueryDevtools initialIsOpen={false} />
          <AuthProvider>
            <TooltipProvider>
                <Toaster />
                <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/stock/:symbol" element={<StockDataProvider><StockDetails /></StockDataProvider>} />

              {/* Protected routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/screener" element={<Screener />} />
                <Route path="/research" element={<Research />} />
                <Route path="/optimizer" element={<Optimizer />} />
                <Route path="/trading" element={<Trading />} />
                <Route path="/investments" element={<Investments />} />
                <Route path="/transactions" element={<Transactions />} />
                        <Route path="/policy" element={<Policy />} />
                        <Route path="/reports" element={<Reports />} />
                        <Route path="/settings" element={<Settings />} />
              </Route>

              {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
              <Route path="*" element={<NotFound />} />
            </Routes>
                </BrowserRouter>
            </TooltipProvider>
          </AuthProvider>
        </QueryClientProvider>
    </TradingProvider>
  </ThemeProvider>
</ErrorBoundary>
);

export default App;
