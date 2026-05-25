import { useRef, useState } from 'react';
import type { Document } from '../../types';

interface MessageInputProps {
  onSend: (text: string) => void;
  onStop: () => void;
  onUpload: (file: File) => Promise<void>;
  isStreaming: boolean;
  uploading: boolean;
  disabled: boolean;
  attachedDocs: Document[];
  onRemoveDoc: (id: string) => void;
}

export function MessageInput({
  onSend,
  onStop,
  onUpload,
  isStreaming,
  uploading,
  disabled,
  attachedDocs,
  onRemoveDoc,
}: MessageInputProps) {
  const [text, setText] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragOver, setDragOver] = useState(false);

  const handleSubmit = () => {
    const trimmed = text.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setText('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = () => {
    const ta = textareaRef.current;
    if (ta) {
      ta.style.height = 'auto';
      ta.style.height = `${Math.min(ta.scrollHeight, 200)}px`;
    }
  };

  const handleFileSelect = async (files: FileList | null) => {
    if (!files) return;
    for (const file of Array.from(files)) {
      await onUpload(file);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    handleFileSelect(e.dataTransfer.files);
  };

  return (
    <div
      className="border-t px-4 py-3"
      style={{ borderColor: 'var(--color-border)' }}
      onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
    >
      {/* Attached documents */}
      {attachedDocs.length > 0 && (
        <div className="mb-2 flex flex-wrap gap-1.5">
          {attachedDocs.map((doc) => (
            <span
              key={doc.id}
              className="inline-flex items-center gap-1 rounded-md border px-2 py-1 text-xs"
              style={{
                borderColor: 'var(--color-border)',
                backgroundColor: 'var(--color-bg-secondary)',
                color: 'var(--color-text-primary)',
              }}
            >
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="var(--color-accent)" strokeWidth="2">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                <path d="M14 2v6h6" />
              </svg>
              {doc.filename}
              <span style={{ color: 'var(--color-text-tertiary)' }}>
                ({doc.chunk_count} chunks)
              </span>
              <button
                onClick={() => onRemoveDoc(doc.id)}
                className="ml-0.5 rounded-full p-0.5 transition-colors"
                style={{ color: 'var(--color-text-tertiary)' }}
              >
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                  <path d="M18 6 6 18M6 6l12 12" />
                </svg>
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Drop zone overlay */}
      {dragOver && (
        <div
          className="mb-2 flex items-center justify-center rounded-lg border-2 border-dashed py-4 text-sm"
          style={{
            borderColor: 'var(--color-accent)',
            color: 'var(--color-accent)',
            backgroundColor: 'var(--color-bg-secondary)',
          }}
        >
          Drop files here (PDF, TXT, MD)
        </div>
      )}

      {/* Uploading indicator */}
      {uploading && (
        <div
          className="mb-2 flex items-center gap-2 text-xs"
          style={{ color: 'var(--color-text-secondary)' }}
        >
          <svg className="h-3 w-3 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
          </svg>
          Processing document...
        </div>
      )}

      <div
        className="flex items-end gap-2 rounded-xl border px-3 py-2 transition-colors"
        style={{
          backgroundColor: 'var(--color-bg-input)',
          borderColor: 'var(--color-border)',
        }}
        onFocus={(e) =>
          (e.currentTarget.style.borderColor = 'var(--color-border-focus)')
        }
        onBlur={(e) =>
          (e.currentTarget.style.borderColor = 'var(--color-border)')
        }
      >
        {/* File attach button */}
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={uploading}
          className="shrink-0 rounded p-1 transition-colors disabled:opacity-40"
          style={{ color: 'var(--color-text-tertiary)' }}
          title="Attach a document (PDF, TXT, MD)"
        >
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="m21.44 11.05-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48" />
          </svg>
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.md,.markdown"
          multiple
          className="hidden"
          onChange={(e) => handleFileSelect(e.target.files)}
        />

        <textarea
          ref={textareaRef}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          onInput={handleInput}
          placeholder={
            attachedDocs.length > 0
              ? 'Ask a question about the attached documents...'
              : 'Type your message... (Enter to send, Shift+Enter for new line)'
          }
          rows={1}
          disabled={disabled}
          className="max-h-[200px] flex-1 resize-none bg-transparent text-sm leading-relaxed outline-none"
          style={{ color: 'var(--color-text-primary)' }}
        />
        {isStreaming ? (
          <button
            onClick={onStop}
            className="flex shrink-0 items-center justify-center rounded-lg px-3 py-1.5 text-sm font-medium text-white transition-colors"
            style={{ backgroundColor: 'var(--color-danger)' }}
            onMouseEnter={(e) =>
              (e.currentTarget.style.backgroundColor = 'var(--color-danger-hover)')
            }
            onMouseLeave={(e) =>
              (e.currentTarget.style.backgroundColor = 'var(--color-danger)')
            }
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" className="mr-1">
              <rect x="6" y="6" width="12" height="12" rx="2" />
            </svg>
            Stop
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={!text.trim() || disabled}
            className="flex shrink-0 items-center justify-center rounded-lg px-3 py-1.5 text-sm font-medium text-white transition-colors disabled:cursor-not-allowed disabled:opacity-40"
            style={{ backgroundColor: 'var(--color-accent)' }}
            onMouseEnter={(e) => {
              if (!e.currentTarget.disabled)
                e.currentTarget.style.backgroundColor = 'var(--color-accent-hover)';
            }}
            onMouseLeave={(e) =>
              (e.currentTarget.style.backgroundColor = 'var(--color-accent)')
            }
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 2 11 13M22 2l-7 20-4-9-9-4 20-7z" />
            </svg>
          </button>
        )}
      </div>
    </div>
  );
}
