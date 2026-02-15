import { useEffect } from 'react';
import { useLivePrices } from '@/context/LivePriceContext';

/**
 * useWebSocket Hook (Refactored)
 * Now a consumer of the Global LivePriceContext.
 */

export const useWebSocket = (symbols: string[] = []) => {
    const { prices, isConnected, subscribe, unsubscribe } = useLivePrices();

    useEffect(() => {
        if (symbols.length > 0) {
            subscribe(symbols);
            return () => unsubscribe(symbols);
        }
    }, [symbols, subscribe, unsubscribe]);

    return { data: prices, isConnected, subscribe, unsubscribe };
};
