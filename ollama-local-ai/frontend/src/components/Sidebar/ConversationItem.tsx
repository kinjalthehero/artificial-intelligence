import type { Conversation } from '../../types';

interface ConversationItemProps {
  conversation: Conversation;
  isActive: boolean;
  isConfirmingDelete: boolean;
  onSelect: () => void;
  onDelete: () => void;
  onCancelDelete: () => void;
}

export function ConversationItem({
  conversation,
  isActive,
  isConfirmingDelete,
  onSelect,
  onDelete,
  onCancelDelete,
}: ConversationItemProps) {
  return (
    <div
      className="group relative mb-0.5 flex cursor-pointer items-center rounded-lg px-3 py-2 text-sm transition-colors"
      style={{
        backgroundColor: isActive ? 'var(--color-bg-active)' : 'transparent',
        color: 'var(--color-text-primary)',
      }}
      onMouseEnter={(e) => {
        if (!isActive)
          e.currentTarget.style.backgroundColor = 'var(--color-bg-hover)';
      }}
      onMouseLeave={(e) => {
        if (!isActive) e.currentTarget.style.backgroundColor = 'transparent';
        onCancelDelete();
      }}
      onClick={onSelect}
    >
      <svg
        className="mr-2 shrink-0"
        width="14"
        height="14"
        viewBox="0 0 24 24"
        fill="none"
        stroke="var(--color-text-tertiary)"
        strokeWidth="2"
      >
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
      </svg>
      <span className="flex-1 truncate">{conversation.title}</span>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onDelete();
        }}
        className="ml-1 shrink-0 rounded p-0.5 opacity-0 transition-opacity group-hover:opacity-100"
        style={{
          color: isConfirmingDelete
            ? 'var(--color-danger)'
            : 'var(--color-text-tertiary)',
        }}
        title={isConfirmingDelete ? 'Click again to confirm' : 'Delete conversation'}
      >
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
        </svg>
      </button>
    </div>
  );
}
