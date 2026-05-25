import { useEffect, useRef } from 'react';
import type { Document } from '../../types';
import type { MessageWithSources } from '../../hooks/useChat';
import { ChatHeader } from './ChatHeader';
import { MessageBubble } from './MessageBubble';
import { MessageInput } from './MessageInput';

interface ChatAreaProps {
  messages: MessageWithSources[];
  isStreaming: boolean;
  selectedModel: string;
  onModelChange: (model: string) => void;
  onSend: (text: string) => void;
  onStop: () => void;
  onUpload: (file: File) => Promise<void>;
  uploading: boolean;
  attachedDocs: Document[];
  onRemoveDoc: (id: string) => void;
}

export function ChatArea({
  messages,
  isStreaming,
  selectedModel,
  onModelChange,
  onSend,
  onStop,
  onUpload,
  uploading,
  attachedDocs,
  onRemoveDoc,
}: ChatAreaProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="flex flex-1 flex-col" style={{ backgroundColor: 'var(--color-bg-primary)' }}>
      <ChatHeader selectedModel={selectedModel} onModelChange={onModelChange} />

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="flex h-full flex-col items-center justify-center">
            <svg
              width="48"
              height="48"
              viewBox="0 0 24 24"
              fill="none"
              stroke="var(--color-text-tertiary)"
              strokeWidth="1.5"
              className="mb-4"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <h2
              className="mb-1 text-lg font-medium"
              style={{ color: 'var(--color-text-primary)' }}
            >
              Start a conversation
            </h2>
            <p
              className="mb-4 text-center text-sm"
              style={{ color: 'var(--color-text-secondary)' }}
            >
              Ask anything — everything runs locally on your machine
            </p>
            <p
              className="text-center text-xs"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              Attach a PDF, TXT, or MD file to chat with your documents
            </p>
          </div>
        ) : (
          <>
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isStreaming && (
              <div className="mb-4 flex items-center gap-2 px-11">
                <div className="flex gap-1">
                  <span
                    className="h-2 w-2 animate-bounce rounded-full"
                    style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '0ms' }}
                  />
                  <span
                    className="h-2 w-2 animate-bounce rounded-full"
                    style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '150ms' }}
                  />
                  <span
                    className="h-2 w-2 animate-bounce rounded-full"
                    style={{ backgroundColor: 'var(--color-text-tertiary)', animationDelay: '300ms' }}
                  />
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </>
        )}
      </div>

      <MessageInput
        onSend={onSend}
        onStop={onStop}
        onUpload={onUpload}
        isStreaming={isStreaming}
        uploading={uploading}
        disabled={false}
        attachedDocs={attachedDocs}
        onRemoveDoc={onRemoveDoc}
      />
    </div>
  );
}
