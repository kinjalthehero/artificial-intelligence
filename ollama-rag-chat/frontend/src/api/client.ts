import type {
  Conversation,
  ConversationDetail,
  Document,
  HealthResponse,
  ModelsResponse,
  SSEEvent,
} from '../types';

const BASE = '/api';

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init);
  if (!res.ok) {
    const body = await res.text();
    throw new Error(body || res.statusText);
  }
  return res.json();
}

export const api = {
  health(): Promise<HealthResponse> {
    return fetchJSON('/health');
  },

  models(): Promise<ModelsResponse> {
    return fetchJSON('/models');
  },

  listConversations(): Promise<Conversation[]> {
    return fetchJSON('/conversations');
  },

  getConversation(id: string): Promise<ConversationDetail> {
    return fetchJSON(`/conversations/${id}`);
  },

  createConversation(title?: string): Promise<Conversation> {
    return fetchJSON('/conversations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title }),
    });
  },

  async deleteConversation(id: string): Promise<void> {
    const res = await fetch(`${BASE}/conversations/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(res.statusText);
  },

  searchConversations(q: string): Promise<Conversation[]> {
    return fetchJSON(`/conversations/search?q=${encodeURIComponent(q)}`);
  },

  async uploadDocument(file: File): Promise<Document> {
    const form = new FormData();
    form.append('file', file);
    const res = await fetch(`${BASE}/documents/upload`, { method: 'POST', body: form });
    if (!res.ok) {
      const body = await res.text();
      throw new Error(body || res.statusText);
    }
    return res.json();
  },

  listDocuments(): Promise<Document[]> {
    return fetchJSON('/documents');
  },

  async deleteDocument(id: string): Promise<void> {
    const res = await fetch(`${BASE}/documents/${id}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(res.statusText);
  },

  streamChat(
    message: string,
    conversationId: string | null,
    model: string | null,
    documentIds: string[],
    onEvent: (event: SSEEvent) => void,
    signal?: AbortSignal,
  ): Promise<void> {
    return new Promise(async (resolve, reject) => {
      try {
        const res = await fetch(`${BASE}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            message,
            conversation_id: conversationId,
            model,
            document_ids: documentIds,
          }),
          signal,
        });

        if (!res.ok) {
          const body = await res.text();
          reject(new Error(body || res.statusText));
          return;
        }

        const reader = res.body?.getReader();
        if (!reader) {
          reject(new Error('No response body'));
          return;
        }

        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';

          for (const line of lines) {
            const trimmed = line.trim();
            if (trimmed.startsWith('data: ')) {
              try {
                const event: SSEEvent = JSON.parse(trimmed.slice(6));
                onEvent(event);
              } catch {
                // skip malformed lines
              }
            }
          }
        }

        if (buffer.trim().startsWith('data: ')) {
          try {
            const event: SSEEvent = JSON.parse(buffer.trim().slice(6));
            onEvent(event);
          } catch {
            // skip
          }
        }

        resolve();
      } catch (err) {
        if (signal?.aborted) resolve();
        else reject(err);
      }
    });
  },
};
