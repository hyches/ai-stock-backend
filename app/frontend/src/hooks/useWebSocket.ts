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