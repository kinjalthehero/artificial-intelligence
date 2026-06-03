import { useEffect, useRef } from 'react';
import type { MessageWithSources } from '../../hooks/useChat';
import type { Document } from '../../types';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';

interface ChatAreaProps {
  messages: MessageWithSources[];
  isStreaming: boolean;
  currentAgent: string | null;
  onSend: (text: string) => void;
  onStop: () => void;
  onUpload: (file: File) => void;
  uploading: boolean;
  attachedDocs: Document[];
  onRemoveDoc: (id: string) => void;
  geminiConnected: boolean;
}

export function ChatArea({
  messages,
  isStreaming,
  currentAgent,
  onSend,
  onStop,
  onUpload,
  uploading,
  attachedDocs,
  onRemoveDoc,
  geminiConnected,
}: ChatAreaProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex-1 flex flex-col min-w-0">
      {/* Header */}
      <div
        className="flex items-center justify-between px-6 py-3"
        style={{ borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-secondary)' }}
      >
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-semibold">GenAI Document Assistant</h1>
          <span
            className="text-xs px-2 py-0.5 rounded-full"
            style={{
              backgroundColor: geminiConnected ? '#dcfce7' : '#fee2e2',
              color: geminiConnected ? '#166534' : '#991b1b',
            }}
          >
            {geminiConnected ? 'Gemini Connected' : 'Gemini Offline'}
          </span>
        </div>
        <span className="text-xs" style={{ color: 'var(--color-text-tertiary)' }}>
          Powered by Gemini 2.5 Flash
        </span>
      </div>

      {/* Attached Documents */}
      {attachedDocs.length > 0 && (
        <div
          className="flex flex-wrap gap-2 px-6 py-2"
          style={{ borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-secondary)' }}
        >
          {attachedDocs.map((doc) => (
            <span
              key={doc.id}
              className="inline-flex items-center gap-1 text-xs px-2 py-1 rounded-full"
              style={{ backgroundColor: 'var(--color-bg-tertiary)', color: 'var(--color-text-secondary)' }}
            >
              {doc.filename} ({doc.chunk_count} chunks)
              <button
                onClick={() => onRemoveDoc(doc.id)}
                className="ml-1 hover:opacity-70 cursor-pointer"
                style={{ color: 'var(--color-danger)' }}
              >
                x
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-4">
            <div className="text-6xl">📄</div>
            <h2 className="text-xl font-semibold" style={{ color: 'var(--color-text-primary)' }}>
              Upload a document to get started
            </h2>
            <p className="text-sm text-center max-w-md" style={{ color: 'var(--color-text-secondary)' }}>
              Upload PDF, TXT, CSV, Excel, JSON, or YAML files, then ask questions.
              The AI will analyze your documents using a multi-agent reasoning pipeline.
            </p>
          </div>
        ) : (
          messages.map((msg, i) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              currentAgent={currentAgent}
              isLast={i === messages.length - 1}
            />
          ))
        )}
      </div>

      {/* Input */}
      <MessageInput
        onSend={onSend}
        onStop={onStop}
        isStreaming={isStreaming}
        onUpload={onUpload}
        uploading={uploading}
      />
    </div>
  );
}
