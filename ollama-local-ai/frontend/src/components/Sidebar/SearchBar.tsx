import { useState } from 'react';

interface SearchBarProps {
  onSearch: (q: string) => void;
  onClear: () => void;
  isSearching: boolean;
}

export function SearchBar({ onSearch, onClear, isSearching }: SearchBarProps) {
  const [query, setQuery] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) onSearch(query.trim());
  };

  const handleClear = () => {
    setQuery('');
    onClear();
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <svg
        className="absolute left-2.5 top-1/2 -translate-y-1/2"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="var(--color-text-tertiary)"
        strokeWidth="2"
      >
        <circle cx="11" cy="11" r="8" />
        <path d="m21 21-4.35-4.35" />
      </svg>
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search conversations..."
        className="w-full rounded-md border py-1.5 pl-8 pr-8 text-sm outline-none transition-colors"
        style={{
          backgroundColor: 'var(--color-bg-input)',
          borderColor: 'var(--color-border)',
          color: 'var(--color-text-primary)',
        }}
        onFocus={(e) => (e.currentTarget.style.borderColor = 'var(--color-border-focus)')}
        onBlur={(e) => (e.currentTarget.style.borderColor = 'var(--color-border)')}
      />
      {isSearching && (
        <button
          type="button"
          onClick={handleClear}
          className="absolute right-2 top-1/2 -translate-y-1/2"
          style={{ color: 'var(--color-text-tertiary)' }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M18 6 6 18M6 6l12 12" />
          </svg>
        </button>
      )}
    </form>
  );
}
