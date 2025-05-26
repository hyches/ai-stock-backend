import { useState, useEffect, useCallback } from 'react';

interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: string;
  read: boolean;
  data?: Record<string, any>;
}

interface UseNotificationsReturn {
  notifications: Notification[];
  unreadCount: number;
  loading: boolean;
  error: string | null;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  removeNotification: (id: string) => Promise<void>;
  clearAll: () => Promise<void>;
  addNotification: (notification: Omit<Notification, 'id' | 'timestamp' | 'read'>) => void;
}

/**
 * Provides functionalities to manage notifications including fetching, marking as read, removing, and adding notifications.
 * @example
 * useNotifications()
 * { notifications: Notification[], unreadCount: number, loading: boolean, error: string | null, markAsRead: function, markAllAsRead: function, removeNotification: function, clearAll: function, addNotification: function }
 * @returns {UseNotificationsReturn} An object containing notifications and related operations.
 * @description
 *   - Fetches notifications from a predefined API endpoint and updates the state accordingly.
 *   - Handles notification state including marking notifications as read and removing them.
 *   - Provides a count of unread notifications.
 */
export const useNotifications = (): UseNotificationsReturn => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchNotifications = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      // TODO: Replace with actual API call
      const response = await fetch('/api/notifications');
      const data = await response.json();
      setNotifications(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch notifications');
      console.error('Error fetching notifications:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  /**
   * Marks a notification as read asynchronously.
   * @example
   * sync('notificationId')
   * // Marks the notification with the given id as read.
   * @param {string} id - Identifier of the notification to be marked as read.
   * @returns {void} Updates the read status of the specified notification.
   * @description
   *   - Assumes the existence of a server endpoint at `/api/notifications/{id}/read`.
   *   - Uses HTTP POST method to mark the notification as read.
   *   - Handles errors by logging to the console.
   */
  const markAsRead = async (id: string) => {
    try {
      // TODO: Replace with actual API call
      await fetch(`/api/notifications/${id}/read`, { method: 'POST' });
      setNotifications((prev) =>
        prev.map((notification) =>
          notification.id === id
            ? { ...notification, read: true }
            : notification
        )
      );
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const markAllAsRead = async () => {
    try {
      // TODO: Replace with actual API call
      await fetch('/api/notifications/read-all', { method: 'POST' });
      setNotifications((prev) =>
        prev.map((notification) => ({ ...notification, read: true }))
      );
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  };

  const removeNotification = async (id: string) => {
    try {
      // TODO: Replace with actual API call
      await fetch(`/api/notifications/${id}`, { method: 'DELETE' });
      setNotifications((prev) =>
        prev.filter((notification) => notification.id !== id)
      );
    } catch (err) {
      console.error('Error removing notification:', err);
    }
  };

  const clearAll = async () => {
    try {
      // TODO: Replace with actual API call
      await fetch('/api/notifications', { method: 'DELETE' });
      setNotifications([]);
    } catch (err) {
      console.error('Error clearing notifications:', err);
    }
  };

  const addNotification = (
    notification: Omit<Notification, 'id' | 'timestamp' | 'read'>
  ) => {
    const newNotification: Notification = {
      ...notification,
      id: Math.random().toString(36).substr(2, 9),
      timestamp: new Date().toISOString(),
      read: false,
    };
    setNotifications((prev) => [newNotification, ...prev]);
  };

  const unreadCount = notifications.filter((n) => !n.read).length;

  return {
    notifications,
    unreadCount,
    loading,
    error,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    addNotification,
  };
};

export default useNotifications; 