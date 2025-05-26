import { useState, useEffect, useCallback, useRef } from 'react';

interface WebSocketMessage {
  type: string;
  data: any;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  sendMessage: (message: WebSocketMessage) => void;
  reconnect: () => void;
  error: string | null;
}

/**
 * Establishes and manages a WebSocket connection with options for auto reconnection and handlers for different events.
 * @example
 * useWebSocket('ws://example.com/socket', {
 *   autoReconnect: true,
 *   reconnectInterval: 3000,
 *   onMessage: (message) => console.log(message),
 *   onOpen: () => console.log('Connection opened'),
 *   onClose: () => console.log('Connection closed'),
 *   onError: (error) => console.error(error),
 * });
 * // { isConnected: true, lastMessage: {...}, sendMessage: fn, reconnect: fn, error: null }
 * @param {string} url - The URL for the WebSocket connection.
 * @param {Object} options - Configuration options for the WebSocket.
 * @param {boolean} [options.autoReconnect=true] - Whether to automatically reconnect on connection failure.
 * @param {number} [options.reconnectInterval=5000] - The interval in milliseconds between reconnection attempts.
 * @param {function} [options.onMessage] - Handler called when a message is received.
 * @param {function} [options.onOpen] - Handler called when the WebSocket connection is opened.
 * @param {function} [options.onClose] - Handler called when the WebSocket connection is closed.
 * @param {function} [options.onError] - Handler called when an error occurs with the WebSocket.
 * @returns {Object} An object containing connection status, last received message, and utility functions.
 * @description
 *   - Automatically attempts reconnection using the specified interval if `autoReconnect` is enabled.
 *   - Handlers (onMessage, onOpen, onClose, onError) are optional but provide hooks for custom logic.
 *   - The `reconnect` function can be used to manually trigger a reconnection attempt.
 */
export const useWebSocket = (
  url: string,
  options: {
    autoReconnect?: boolean;
    reconnectInterval?: number;
    onMessage?: (message: WebSocketMessage) => void;
    onOpen?: () => void;
    onClose?: () => void;
    onError?: (error: Event) => void;
  } = {}
): UseWebSocketReturn => {
  const {
    autoReconnect = true,
    reconnectInterval = 5000,
    onMessage,
    onOpen,
    onClose,
    onError,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number>();

  const connect = useCallback(() => {
    try {
      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        onOpen?.();
      };

      ws.onclose = () => {
        setIsConnected(false);
        onClose?.();

        if (autoReconnect) {
          reconnectTimeoutRef.current = window.setTimeout(() => {
            connect();
          }, reconnectInterval);
        }
      };

      ws.onerror = (event) => {
        setError('WebSocket error occurred');
        onError?.(event);
      };

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data) as WebSocketMessage;
          setLastMessage(message);
          onMessage?.(message);
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
        }
      };
    } catch (err) {
      setError('Failed to connect to WebSocket');
      console.error('WebSocket connection error:', err);
    }
  }, [url, autoReconnect, reconnectInterval, onMessage, onOpen, onClose, onError]);

  useEffect(() => {
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (reconnectTimeoutRef.current) {
        window.clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [connect]);

  const sendMessage = useCallback(
    (message: WebSocketMessage) => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify(message));
      } else {
        setError('WebSocket is not connected');
      }
    },
    []
  );

  const reconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
    }
    if (reconnectTimeoutRef.current) {
      window.clearTimeout(reconnectTimeoutRef.current);
    }
    connect();
  }, [connect]);

  return {
    isConnected,
    lastMessage,
    sendMessage,
    reconnect,
    error,
  };
};

export default useWebSocket; 