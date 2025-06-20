import { useState, useEffect, useCallback } from 'react';
import { authApi } from '../services/api';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

interface UseAuthReturn extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => Promise<void>;
  loading: boolean;
  error: string | null;
}

export const useAuth = (): UseAuthReturn => {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: localStorage.getItem('token'),
    isAuthenticated: false,
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUser = useCallback(async () => {
    if (!state.token) {
      setLoading(false);
      return;
    }

    try {
      const response = await authApi.getCurrentUser();
      setState((prev) => ({
        ...prev,
        user: response.data,
        isAuthenticated: true,
      }));
    } catch (err) {
      console.error('Error fetching user:', err);
      setState((prev) => ({
        ...prev,
        user: null,
        token: null,
        isAuthenticated: false,
      }));
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  }, [state.token]);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = async (email: string, password: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await authApi.login({ email, password });
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setState({
        user,
        token,
        isAuthenticated: true,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const register = async (email: string, password: string, name: string) => {
    try {
      setLoading(true);
      setError(null);
      const response = await authApi.register({ email, password, name });
      const { token, user } = response.data;
      localStorage.setItem('token', token);
      setState({
        user,
        token,
        isAuthenticated: true,
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const logout = async () => {
    try {
      setLoading(true);
      await authApi.logout();
    } catch (err) {
      console.error('Error during logout:', err);
    } finally {
      localStorage.removeItem('token');
      setState({
        user: null,
        token: null,
        isAuthenticated: false,
      });
      setLoading(false);
    }
  };

  return {
    ...state,
    login,
    register,
    logout,
    loading,
    error,
  };
};

export default useAuth; 