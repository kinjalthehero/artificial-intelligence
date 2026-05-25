import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import type { Conversation } from '../types';

interface UseConversationsReturn {
  conversations: Conversation[];
  loading: boolean;
  refresh: () => Promise<void>;
  remove: (id: string) => Promise<void>;
  search: (q: string) => Promise<void>;
  clearSearch: () => void;
  isSearching: boolean;
}

export function useConversations(): UseConversationsReturn {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);
  const [isSearching, setIsSearching] = useState(false);

  const refresh = useCallback(async () => {
    setLoading(true);
    setIsSearching(false);
    try {
      const data = await api.listConversations();
      setConversations(data);
    } catch {
      // offline or backend not running
    } finally {
      setLoading(false);
    }
  }, []);

  const remove = useCallback(
    async (id: string) => {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
    },
    [],
  );

  const search = useCallback(async (q: string) => {
    if (!q.trim()) return;
    setLoading(true);
    setIsSearching(true);
    try {
      const data = await api.searchConversations(q);
      setConversations(data);
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, []);

  const clearSearch = useCallback(() => {
    setIsSearching(false);
    refresh();
  }, [refresh]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  return { conversations, loading, refresh, remove, search, clearSearch, isSearching };
}
