import { useState } from 'react';
import type { MessageWithSources } from '../../hooks/useChat';
import type { SourceChunk } from '../../types';

interface MessageBubbleProps {
  message: MessageWithSources;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className="flex max-w-[75%] gap-3">
        {!isUser && (
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-medium"
            style={{
              backgroundColor: 'var(--color-bg-tertiary)',
              color: 'var(--color-text-secondary)',
            }}
          >
            AI
          </div>
        )}
        <div>
          <div
            className={`message-content rounded-2xl px-4 py-2.5 text-sm leading-relaxed ${
              isUser ? 'rounded-br-md' : 'rounded-bl-md'
            }`}
            style={{
              backgroundColor: isUser
                ? 'var(--color-bg-user-msg)'
                : 'var(--color-bg-assistant-msg)',
              color: isUser
                ? 'var(--color-text-on-primary)'
                : 'var(--color-text-primary)',
            }}
          >
            {isUser ? (
              <p className="whitespace-pre-wrap">{message.content}</p>
            ) : (
              <div
                className="whitespace-pre-wrap"
                dangerouslySetInnerHTML={{
                  __html: formatMarkdown(message.content),
                }}
              />
            )}
          </div>
          {!isUser && message.sources && message.sources.length > 0 && (
            <SourceCitations sources={message.sources} />
          )}
          {!isUser && message.model && (
            <p
              className="mt-1 px-1 text-xs"
              style={{ color: 'var(--color-text-tertiary)' }}
            >
              {message.model}
            </p>
          )}
        </div>
        {isUser && (
          <div
            className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-sm font-medium"
            style={{
              backgroundColor: 'var(--color-accent)',
              color: 'white',
            }}
          >
            U
          </div>
        )}
      </div>
    </div>
  );
}

function SourceCitations({ sources }: { sources: SourceChunk[] }) {
  const [expanded, setExpanded] = useState(false);

  return (
    <div className="mt-2">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-1 rounded-md px-2 py-1 text-xs transition-colors"
        style={{
          color: 'var(--color-accent)',
          backgroundColor: 'var(--color-bg-tertiary)',
        }}
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <path d="M14 2v6h6" />
        </svg>
        {sources.length} source{sources.length > 1 ? 's' : ''}
        <svg
          width="12"
          height="12"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          className={`transition-transform ${expanded ? 'rotate-180' : ''}`}
        >
          <path d="m6 9 6 6 6-6" />
        </svg>
      </button>
      {expanded && (
        <div className="mt-1.5 space-y-1.5">
          {sources.map((src, i) => (
            <div
              key={i}
              className="rounded-lg border px-3 py-2 text-xs"
              style={{
                borderColor: 'var(--color-border)',
                backgroundColor: 'var(--color-bg-secondary)',
              }}
            >
              <div className="mb-1 flex items-center justify-between">
                <span className="font-medium" style={{ color: 'var(--color-text-primary)' }}>
                  {src.filename}
                  <span style={{ color: 'var(--color-text-tertiary)' }}>
                    {' '}p.{src.page}
                  </span>
                </span>
                <span
                  className="rounded px-1.5 py-0.5"
                  style={{
                    backgroundColor: 'var(--color-bg-tertiary)',
                    color: 'var(--color-text-secondary)',
                  }}
                >
                  {Math.round(src.score * 100)}% match
                </span>
              </div>
              <p
                className="line-clamp-3 leading-relaxed"
                style={{ color: 'var(--color-text-secondary)' }}
              >
                {src.content}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function formatMarkdown(text: string): string {
  if (!text) return '';
  let html = text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;');

  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_m, _lang, code) => {
    return `<pre><code>${code.trim()}</code></pre>`;
  });

  html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');
  html = html.replace(/^- (.+)$/gm, '<li>$1</li>');
  html = html.replace(/(<li>.*<\/li>\n?)+/g, '<ul>$&</ul>');
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');

  return html;
}
