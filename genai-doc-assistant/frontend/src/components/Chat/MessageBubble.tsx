import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import type { MessageWithSources } from '../../hooks/useChat';
import { AgentWorkflow } from './AgentWorkflow';
import { useState } from 'react';

interface MessageBubbleProps {
  message: MessageWithSources;
  currentAgent: string | null;
  isLast: boolean;
}

export function MessageBubble({ message, currentAgent, isLast }: MessageBubbleProps) {
  const [showSources, setShowSources] = useState(false);
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div
        className={`max-w-[80%] rounded-2xl px-4 py-3 ${isUser ? 'rounded-br-sm' : 'rounded-bl-sm'}`}
        style={{
          backgroundColor: isUser ? 'var(--color-bg-user-msg)' : 'var(--color-bg-assistant-msg)',
          color: isUser ? 'var(--color-text-on-primary)' : 'var(--color-text-primary)',
        }}
      >
        {!isUser && message.agentSteps && message.agentSteps.length > 0 && (
          <AgentWorkflow
            steps={message.agentSteps}
            currentAgent={isLast ? currentAgent : null}
          />
        )}

        {!isUser && isLast && currentAgent && (!message.agentSteps || message.agentSteps.length === 0) && (
          <AgentWorkflow steps={[]} currentAgent={currentAgent} />
        )}

        <div className="message-content">
          {isUser ? (
            <p className="whitespace-pre-wrap">{message.content}</p>
          ) : message.content ? (
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
          ) : (
            <span className="agent-pulse" style={{ color: 'var(--color-text-tertiary)' }}>
              Thinking...
            </span>
          )}
        </div>

        {!isUser && message.parsedSources && message.parsedSources.length > 0 && (
          <div className="mt-2 pt-2" style={{ borderTop: '1px solid var(--color-border)' }}>
            <button
              onClick={() => setShowSources(!showSources)}
              className="text-xs font-medium cursor-pointer"
              style={{ color: 'var(--color-accent)' }}
            >
              {showSources ? 'Hide' : 'Show'} {message.parsedSources.length} source(s)
            </button>
            {showSources && (
              <div className="mt-2 space-y-2">
                {message.parsedSources.map((src, i) => (
                  <div
                    key={i}
                    className="text-xs p-2 rounded"
                    style={{ backgroundColor: 'var(--color-bg-tertiary)' }}
                  >
                    <div className="font-medium">
                      {src.filename} (page {src.page}) — {(src.score * 100).toFixed(0)}% match
                    </div>
                    <div className="mt-1 opacity-80">{src.content}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
