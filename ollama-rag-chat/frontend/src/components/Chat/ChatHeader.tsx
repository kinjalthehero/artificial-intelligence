import { useEffect, useState } from 'react';
import { api } from '../../api/client';
import type { ModelInfo } from '../../types';

interface ChatHeaderProps {
  selectedModel: string;
  onModelChange: (model: string) => void;
}

export function ChatHeader({ selectedModel, onModelChange }: ChatHeaderProps) {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [ollamaConnected, setOllamaConnected] = useState(true);

  useEffect(() => {
    api.models().then((res) => {
      setModels(res.models);
      setOllamaConnected(true);
    }).catch(() => setOllamaConnected(false));
  }, []);

  return (
    <header
      className="flex items-center justify-between border-b px-6 py-3"
      style={{ borderColor: 'var(--color-border)' }}
    >
      <div className="flex items-center gap-3">
        <select
          value={selectedModel}
          onChange={(e) => onModelChange(e.target.value)}
          className="cursor-pointer rounded-md border px-3 py-1.5 text-sm outline-none"
          style={{
            backgroundColor: 'var(--color-bg-input)',
            borderColor: 'var(--color-border)',
            color: 'var(--color-text-primary)',
          }}
        >
          {models.map((m) => (
            <option key={m.name} value={m.name}>
              {m.name}
            </option>
          ))}
        </select>
      </div>
      <div className="flex items-center gap-2 text-xs">
        <span
          className={`inline-block h-2 w-2 rounded-full ${
            ollamaConnected ? 'bg-green-500' : 'bg-red-500'
          }`}
        />
        <span style={{ color: 'var(--color-text-secondary)' }}>
          {ollamaConnected ? 'Ollama connected' : 'Ollama disconnected'}
        </span>
      </div>
    </header>
  );
}
