import { useCallback, useEffect, useState } from 'react';
import { api } from '../api/client';
import type { Conversation } from '../types';

interface UseConversationsReturn {
  conversations: Conversation[];
  refresh: () => void;
  remove: (id: string) => Promise<void>;
  search: (q: string) => Promise<void>;
  clearSearch: () => void;
  isSearching: boolean;
}

export function useConversations(): UseConversationsReturn {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isSearching, setIsSearching] = useState(false);

  const loadAll = useCallback(async () => {
    try {
      const list = await api.listConversations();
      setConversations(list);
    } catch {
      // backend not ready yet
    }
  }, []);

  useEffect(() => {
    loadAll();
  }, [loadAll]);

  const refresh = useCallback(() => {
    loadAll();
  }, [loadAll]);

  const remove = useCallback(
    async (id: string) => {
      await api.deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
    },
    [],
  );

  const search = useCallback(async (q: string) => {
    setIsSearching(true);
    try {
      const results = await api.searchConversations(q);
      setConversations(results);
    } catch {
      // ignore
    }
  }, []);

  const clearSearch = useCallback(() => {
    setIsSearching(false);
    loadAll();
  }, [loadAll]);

  return { conversations, refresh, remove, search, clearSearch, isSearching };
}
