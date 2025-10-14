import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from "@/context/AuthContext";
import { ThemeProvider } from "@/context/ThemeContext";
import { TradingProvider } from "@/context/TradingContext";
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
import Search from "./pages/Search";
import Transactions from "./pages/Transactions";
import Investments from "./pages/Investments";

const queryClient = new QueryClient();

const App = () => (
  <ErrorBoundary>
    <ThemeProvider>
      <TradingProvider>
        <QueryClientProvider client={queryClient}>
          <AuthProvider>
            <TooltipProvider>
              <Toaster />
              <BrowserRouter>
            <Routes>
              {/* Public routes */}
              <Route path="/" element={<Home />} />
              <Route path="/login" element={<Login />} />
              <Route path="/stock/:symbol" element={<StockDetails />} />

              {/* Protected routes */}
              <Route element={<ProtectedRoute />}>
                <Route path="/dashboard" element={<Dashboard />} />
                <Route path="/search" element={<Search />} />
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
