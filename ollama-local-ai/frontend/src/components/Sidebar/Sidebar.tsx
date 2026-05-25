import { useState } from 'react';
import type { Conversation } from '../../types';
import { SearchBar } from './SearchBar';
import { ConversationItem } from './ConversationItem';

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
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  return (
    <aside
      className="flex h-full w-64 shrink-0 flex-col border-r"
      style={{
        backgroundColor: 'var(--color-bg-sidebar)',
        borderColor: 'var(--color-border)',
      }}
    >
      {/* Header */}
      <div
        className="flex items-center justify-between border-b px-4 py-3"
        style={{ borderColor: 'var(--color-border)' }}
      >
        <h1
          className="text-base font-semibold"
          style={{ color: 'var(--color-text-primary)' }}
        >
          Ollama Local AI
        </h1>
        <button
          onClick={onToggleTheme}
          className="rounded-md p-1.5 transition-colors"
          style={{ color: 'var(--color-text-secondary)' }}
          title={dark ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {dark ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="12" cy="12" r="5" />
              <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          )}
        </button>
      </div>

      {/* New Chat button */}
      <div className="px-3 pt-3">
        <button
          onClick={onNew}
          className="flex w-full items-center justify-center gap-2 rounded-lg px-3 py-2.5 text-sm font-medium text-white transition-colors"
          style={{ backgroundColor: 'var(--color-accent)' }}
          onMouseEnter={(e) =>
            (e.currentTarget.style.backgroundColor = 'var(--color-accent-hover)')
          }
          onMouseLeave={(e) =>
            (e.currentTarget.style.backgroundColor = 'var(--color-accent)')
          }
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
          New Chat
        </button>
      </div>

      {/* Search */}
      <div className="px-3 pt-2">
        <SearchBar
          onSearch={onSearch}
          onClear={onClearSearch}
          isSearching={isSearching}
        />
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-2 py-2">
        {conversations.length === 0 ? (
          <p
            className="px-2 py-8 text-center text-sm"
            style={{ color: 'var(--color-text-tertiary)' }}
          >
            {isSearching ? 'No results found' : 'No conversations yet'}
          </p>
        ) : (
          conversations.map((conv) => (
            <ConversationItem
              key={conv.id}
              conversation={conv}
              isActive={conv.id === activeId}
              isConfirmingDelete={confirmDelete === conv.id}
              onSelect={() => onSelect(conv.id)}
              onDelete={() => {
                if (confirmDelete === conv.id) {
                  onDelete(conv.id);
                  setConfirmDelete(null);
                } else {
                  setConfirmDelete(conv.id);
                }
              }}
              onCancelDelete={() => setConfirmDelete(null)}
            />
          ))
        )}
      </div>

      {/* Footer */}
      <div
        className="border-t px-4 py-2.5 text-center text-xs"
        style={{
          borderColor: 'var(--color-border)',
          color: 'var(--color-text-tertiary)',
        }}
      >
        Powered by Ollama
      </div>
    </aside>
  );
}
