import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';

/**
 * Global Live Price Context
 * Ensures a singleton WebSocket connection for all market data.
 */

interface TickData {
    symbol: string;
    data: {
        ltp: number;
        volume: number;
        bid: number;
        ask: number;
        change_pct: number;
        timestamp: string;
    };
}

interface LivePriceContextType {
    prices: Record<string, TickData['data']>;
    isConnected: boolean;
    subscribe: (symbols: string[]) => void;
    unsubscribe: (symbols: string[]) => void;
}

const LivePriceContext = createContext<LivePriceContextType | undefined>(undefined);

export const LivePriceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [prices, setPrices] = useState<Record<string, TickData['data']>>({});
    const [isConnected, setIsConnected] = useState(false);
    const ws = useRef<WebSocket | null>(null);
    const subscribers = useRef<Set<string>>(new Set());

    const connect = useCallback(() => {
        if (ws.current?.readyState === WebSocket.OPEN) return;

        try {
            const socket = new WebSocket('ws://localhost:8000/api/v1/websocket/ws/market-data');

            socket.onopen = () => {
                console.log('🌐 Global Price WebSocket Connected');
                setIsConnected(true);

                // Resubscribe to existing symbols on reconnect
                if (subscribers.current.size > 0) {
                    socket.send(JSON.stringify({
                        action: 'subscribe',
                        symbols: Array.from(subscribers.current)
                    }));
                }
            };

            socket.onmessage = (event) => {
                const message = JSON.parse(event.data);
                if (message.type === 'tick') {
                    setPrices(prev => ({
                        ...prev,
                        [message.symbol]: message.data
                    }));
                }
            };

            socket.onclose = () => {
                console.log('🌐 Global Price WebSocket Disconnected');
                setIsConnected(false);
                setTimeout(connect, 3000);
            };

            ws.current = socket;
        } catch (error) {
            console.error('WebSocket Error:', error);
            setTimeout(connect, 5000);
        }
    }, []);

    useEffect(() => {
        connect();
        return () => ws.current?.close();
    }, [connect]);

    const subscribe = (symbols: string[]) => {
        symbols.forEach(s => subscribers.current.add(s));
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ action: 'subscribe', symbols }));
        }
    };

    const unsubscribe = (symbols: string[]) => {
        symbols.forEach(s => subscribers.current.delete(s));
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ action: 'unsubscribe', symbols }));
        }
    };

    return (
        <LivePriceContext.Provider value={{ prices, isConnected, subscribe, unsubscribe }}>
            {children}
        </LivePriceContext.Provider>
    );
};

export const useLivePrices = () => {
    const context = useContext(LivePriceContext);
    if (!context) throw new Error('useLivePrices must be used within LivePriceProvider');
    return context;
};
