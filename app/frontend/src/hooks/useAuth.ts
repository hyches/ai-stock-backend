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

/**
 * Provides authentication hooks and functionalities.
 * @example
 * useAuthReturn.login('email@example.com', 'password123')
 * // Initiates a login process and updates the auth state
 * @returns {UseAuthReturn} Object containing authentication state and functions.
 * @description
 *   - Manages user authentication state including user details, token, and authentication status.
 *   - Interacts with localStorage to persist authentication data and manages API calls for login, registration, and logout.
 *   - Includes loading and error states to handle UI feedback during asynchronous authentication processes.
 */
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

  /**
  * Authenticates a user by email and password, updating state with user data and a token.
  * @example
  * sync('user@example.com', 'securePassword')
  * Throws an error if login fails.
  * @param {string} email - The email of the user attempting to log in.
  * @param {string} password - The password of the user.
  * @returns {Promise<void>} Resolves with no value upon successful authentication.
  * @description
  *   - Sets a loading state while processing the authentication.
  *   - Catches errors and updates the error state with appropriate messages.
  *   - Stores the authentication token in the browser's local storage.
  */
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

  /**
  * Registers a new user using their email, password, and name, while updating application state and storing a token.
  * @example
  * sync("user@example.com", "securePassword", "John Doe")
  * Throws an error if registration fails with message 'Registration failed', or specific error message.
  * @param {string} email - The user's email address.
  * @param {string} password - The user's password.
  * @param {string} name - The user's full name.
  * @returns {void} Updates state to include user information and authentication status.
  * @description
  *   - Uses authApi to send registration data.
  *   - Stores authentication token in local storage.
  *   - Handles loading state during registration process.
  */
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

  /**
  * Handles user logout process, clearing session and resetting state.
  * @example
  * sync()
  * // Returns undefined, updates application state for logged-out user
  * @param none
  * @returns {undefined} No return value as function is used for side effects.
  * @description
  *   - Sets a loading state to true to indicate the ongoing logout process.
  *   - Fetches the 'logout' functionality from the authentication API.
  *   - Removes token from localStorage to clear session.
  *   - Resets application state to reflect logged-out user status.
  */
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