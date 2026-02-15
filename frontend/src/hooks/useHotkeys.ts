import { useEffect, useCallback } from 'react';

/**
 * useHotkeys Hook
 * Allows registering global keyboard shortcuts for rapid navigation and actions.
 * 
 * Usage:
 * useHotkeys('b', () => console.log('Buy triggered'));
 * useHotkeys('shift+r', () => console.log('Refresh triggered'));
 */

export const useHotkeys = (key: string, callback: () => void, deps: any[] = []) => {
    const handler = useCallback((event: KeyboardEvent) => {
        const keys = key.toLowerCase().split('+');

        const isCtrl = keys.includes('ctrl') || keys.includes('control');
        const isShift = keys.includes('shift');
        const isAlt = keys.includes('alt');
        const isMeta = keys.includes('meta') || keys.includes('cmd');

        const targetKey = keys.filter(k => !['ctrl', 'control', 'shift', 'alt', 'meta', 'cmd'].includes(k))[0];

        const matchKey = event.key.toLowerCase() === targetKey;
        const matchCtrl = event.ctrlKey === isCtrl;
        const matchShift = event.shiftKey === isShift;
        const matchAlt = event.altKey === isAlt;
        const matchMeta = event.metaKey === isMeta;

        if (matchKey && matchCtrl && matchShift && matchAlt && matchMeta) {
            // Don't trigger if user is typing in an input
            const target = event.target as HTMLElement;
            if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
                return;
            }

            event.preventDefault();
            callback();
        }
    }, [key, callback, ...deps]);

    useEffect(() => {
        window.addEventListener('keydown', handler);
        return () => {
            window.removeEventListener('keydown', handler);
        };
    }, [handler]);
};
