import { useCallback, useState } from 'react';
import type { Conversation } from '../../types';

interface SidebarProps {
  conversations: Conversation[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
  onSearch: (q: string) => void;
  onClearSearch: () => void;
  isSearching: boolean;
  dark: boolean;
  onToggleTheme: () => void;
}

export function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  onSearch,
  onClearSearch,
  isSearching,
  dark,
  onToggleTheme,
}: SidebarProps) {
  const [query, setQuery] = useState('');

  const handleSearch = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      if (query.trim()) onSearch(query.trim());
    },
    [query, onSearch],
  );

  const handleClear = useCallback(() => {
    setQuery('');
    onClearSearch();
  }, [onClearSearch]);

  return (
    <div
      className="w-72 flex flex-col h-screen shrink-0"
      style={{ backgroundColor: 'var(--color-bg-sidebar)', borderRight: '1px solid var(--color-border)' }}
    >
      {/* Header */}
      <div className="p-4 flex items-center justify-between">
        <span className="text-sm font-bold" style={{ color: 'var(--color-accent)' }}>
          DocAssistant
        </span>
        <button
          onClick={onToggleTheme}
          className="text-sm p-1.5 rounded cursor-pointer"
          style={{ color: 'var(--color-text-secondary)' }}
          title={dark ? 'Light mode' : 'Dark mode'}
        >
          {dark ? '☀' : '☾'}
        </button>
      </div>

      {/* New Chat */}
      <div className="px-4 pb-3">
        <button
          onClick={onNew}
          className="w-full py-2 rounded-lg text-sm font-medium cursor-pointer"
          style={{ backgroundColor: 'var(--color-accent)', color: 'white' }}
        >
          + New Chat
        </button>
      </div>

      {/* Search */}
      <form onSubmit={handleSearch} className="px-4 pb-3">
        <div className="flex gap-1">
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search..."
            className="flex-1 text-xs px-2 py-1.5 rounded outline-none"
            style={{
              backgroundColor: 'var(--color-bg-input)',
              border: '1px solid var(--color-border)',
              color: 'var(--color-text-primary)',
            }}
          />
          {isSearching && (
            <button
              type="button"
              onClick={handleClear}
              className="text-xs px-2 rounded cursor-pointer"
              style={{ color: 'var(--color-accent)' }}
            >
              Clear
            </button>
          )}
        </div>
      </form>

      {/* Conversation List */}
      <div className="flex-1 overflow-y-auto px-2">
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className="group flex items-center gap-2 px-3 py-2 rounded-lg mb-0.5 cursor-pointer"
            style={{
              backgroundColor: conv.id === activeId ? 'var(--color-bg-active)' : 'transparent',
            }}
            onClick={() => onSelect(conv.id)}
          >
            <span className="flex-1 text-sm truncate" style={{ color: 'var(--color-text-primary)' }}>
              {conv.title}
            </span>
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(conv.id);
              }}
              className="opacity-0 group-hover:opacity-100 text-xs px-1 cursor-pointer"
              style={{ color: 'var(--color-danger)' }}
            >
              x
            </button>
          </div>
        ))}
      </div>

      {/* Footer */}
      <div className="p-4 text-xs" style={{ color: 'var(--color-text-tertiary)', borderTop: '1px solid var(--color-border)' }}>
        GenAI Document Assistant v1.0
      </div>
    </div>
  );
}
