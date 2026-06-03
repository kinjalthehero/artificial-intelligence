import { useCallback, useRef, useState } from 'react';

interface MessageInputProps {
  onSend: (text: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  onUpload: (file: File) => void;
  uploading: boolean;
}

const ACCEPTED = '.pdf,.txt,.csv,.xlsx,.xls,.json,.yaml,.yml';

export function MessageInput({ onSend, onStop, isStreaming, onUpload, uploading }: MessageInputProps) {
  const [text, setText] = useState('');
  const fileRef = useRef<HTMLInputElement>(null);

  const handleSubmit = useCallback(() => {
    const trimmed = text.trim();
    if (!trimmed || isStreaming) return;
    onSend(trimmed);
    setText('');
  }, [text, isStreaming, onSend]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit],
  );

  const handleFileChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) onUpload(file);
      e.target.value = '';
    },
    [onUpload],
  );

  return (
    <div
      className="flex items-end gap-2 p-4"
      style={{ borderTop: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-primary)' }}
    >
      <button
        onClick={() => fileRef.current?.click()}
        disabled={uploading}
        className="p-2 rounded-lg hover:opacity-80 cursor-pointer disabled:opacity-50"
        style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}
        title="Upload document"
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48" />
        </svg>
      </button>
      <input ref={fileRef} type="file" accept={ACCEPTED} onChange={handleFileChange} className="hidden" />

      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask a question about your documents..."
        rows={1}
        className="flex-1 resize-none rounded-xl px-4 py-3 outline-none"
        style={{
          backgroundColor: 'var(--color-bg-input)',
          border: '1px solid var(--color-border)',
          color: 'var(--color-text-primary)',
          minHeight: '48px',
          maxHeight: '120px',
        }}
      />

      {isStreaming ? (
        <button
          onClick={onStop}
          className="px-4 py-3 rounded-xl font-medium cursor-pointer"
          style={{ backgroundColor: 'var(--color-danger)', color: 'white' }}
        >
          Stop
        </button>
      ) : (
        <button
          onClick={handleSubmit}
          disabled={!text.trim()}
          className="px-4 py-3 rounded-xl font-medium cursor-pointer disabled:opacity-50"
          style={{ backgroundColor: 'var(--color-accent)', color: 'white' }}
        >
          Send
        </button>
      )}
    </div>
  );
}
