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
        style={{ borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-primary)' }}
      >
        <div className="flex items-center gap-3">
          <h1 className="text-lg font-bold gradient-text">GenAI Document Assistant</h1>
          <span
            className="text-xs px-2.5 py-1 rounded-full font-medium"
            style={{
              backgroundColor: geminiConnected ? 'var(--color-accent-light)' : '#fee2e2',
              color: geminiConnected ? '#059669' : '#991b1b',
            }}
          >
            {geminiConnected ? 'Gemini Connected' : 'Gemini Offline'}
          </span>
        </div>
        <span className="text-xs font-medium" style={{ color: 'var(--color-text-tertiary)' }}>
          Powered by Gemini 2.5 Flash
        </span>
      </div>

      {/* Attached Documents */}
      {attachedDocs.length > 0 && (
        <div
          className="flex flex-wrap gap-2 px-6 py-2.5"
          style={{ borderBottom: '1px solid var(--color-border)', backgroundColor: 'var(--color-bg-secondary)' }}
        >
          {attachedDocs.map((doc) => (
            <span
              key={doc.id}
              className="inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full font-medium"
              style={{ backgroundColor: 'var(--color-accent-light)', color: 'var(--color-accent-hover)' }}
            >
              {doc.filename} ({doc.chunk_count} chunks)
              <button
                onClick={() => onRemoveDoc(doc.id)}
                className="ml-0.5 hover:opacity-70 cursor-pointer font-bold"
                style={{ color: 'var(--color-danger)' }}
              >
                x
              </button>
            </span>
          ))}
        </div>
      )}

      {/* Messages or Welcome Screen */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-6">
        {messages.length === 0 ? (
          <WelcomeScreen />
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

function WelcomeScreen() {
  return (
    <div className="flex flex-col items-center justify-center h-full gap-6 max-w-2xl mx-auto">
      {/* Hero */}
      <div className="text-center">
        <div className="text-5xl mb-4">
          <span className="gradient-text text-6xl font-bold">AI</span>
        </div>
        <h2 className="text-2xl font-bold mb-2" style={{ color: 'var(--color-text-primary)' }}>
          Intelligent Document Analysis
        </h2>
        <p className="text-sm leading-relaxed" style={{ color: 'var(--color-text-secondary)' }}>
          Upload any document and ask questions. Get accurate, grounded answers
          powered by a multi-agent AI reasoning pipeline.
        </p>
      </div>

      {/* How it works */}
      <div className="grid grid-cols-3 gap-3 w-full">
        <StepCard number="1" title="Upload" desc="PDF, CSV, Excel, JSON, YAML, or TXT" />
        <StepCard number="2" title="Ask" desc="Type any question about your document" />
        <StepCard number="3" title="Get Answers" desc="AI analyzes with 5-agent pipeline" />
      </div>

      {/* Tech Stack for hiring managers */}
      <div
        className="w-full rounded-xl p-4 mt-2"
        style={{ backgroundColor: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
      >
        <h3 className="text-xs font-bold uppercase tracking-wider mb-3" style={{ color: 'var(--color-text-tertiary)' }}>
          Technical Architecture
        </h3>
        <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs" style={{ color: 'var(--color-text-secondary)' }}>
          <div><span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Frontend:</span> React 19, TypeScript, Tailwind CSS</div>
          <div><span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Backend:</span> FastAPI, Python 3.11</div>
          <div><span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>LLM:</span> Google Gemini 2.5 Flash</div>
          <div><span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Embeddings:</span> Gemini embedding-001</div>
          <div><span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Vector DB:</span> ChromaDB (cosine similarity)</div>
          <div><span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Agents:</span> LlamaIndex (5-agent pipeline)</div>
          <div><span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Database:</span> SQLite (async)</div>
          <div><span className="font-semibold" style={{ color: 'var(--color-text-primary)' }}>Deploy:</span> Docker, AWS EC2, Render</div>
        </div>
        <div className="mt-3 pt-3 text-xs" style={{ borderTop: '1px solid var(--color-border)', color: 'var(--color-text-tertiary)' }}>
          RAG Pipeline: Document upload &rarr; Parse (6 formats) &rarr; Chunk (SentenceSplitter) &rarr; Embed &rarr; Vector Store &rarr; Semantic Search &rarr; Multi-Agent Reasoning &rarr; Grounded Response
        </div>
      </div>
    </div>
  );
}

function StepCard({ number, title, desc }: { number: string; title: string; desc: string }) {
  return (
    <div
      className="rounded-xl p-4 text-center"
      style={{ backgroundColor: 'var(--color-bg-secondary)', border: '1px solid var(--color-border)' }}
    >
      <div
        className="w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-2 text-sm font-bold"
        style={{ background: 'linear-gradient(135deg, var(--color-gradient-start), var(--color-gradient-end))', color: 'white' }}
      >
        {number}
      </div>
      <div className="text-sm font-semibold mb-1" style={{ color: 'var(--color-text-primary)' }}>{title}</div>
      <div className="text-xs" style={{ color: 'var(--color-text-secondary)' }}>{desc}</div>
    </div>
  );
}
