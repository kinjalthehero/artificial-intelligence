import { useCallback, useRef, useState } from 'react';
import { api } from '../api/client';
import type { Message, SourceChunk } from '../types';

export interface MessageWithSources extends Message {
  sources?: SourceChunk[];
}

interface UseChatReturn {
  messages: MessageWithSources[];
  setMessages: React.Dispatch<React.SetStateAction<MessageWithSources[]>>;
  isStreaming: boolean;
  sendMessage: (
    text: string,
    conversationId: string | null,
    model: string | null,
    documentIds: string[],
  ) => Promise<string | null>;
  stopStreaming: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<MessageWithSources[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const abortRef = useRef<AbortController | null>(null);

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setIsStreaming(false);
  }, []);

  const sendMessage = useCallback(
    async (
      text: string,
      conversationId: string | null,
      model: string | null,
      documentIds: string[],
    ): Promise<string | null> => {
      const userMsg: MessageWithSources = {
        id: crypto.randomUUID(),
        conversation_id: conversationId || '',
        role: 'user',
        content: text,
        model: null,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      const assistantMsg: MessageWithSources = {
        id: crypto.randomUUID(),
        conversation_id: conversationId || '',
        role: 'assistant',
        content: '',
        model,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, assistantMsg]);

      setIsStreaming(true);
      abortRef.current = new AbortController();

      let resolvedConversationId: string | null = conversationId;

      try {
        await api.streamChat(
          text,
          conversationId,
          model,
          documentIds,
          (event) => {
            switch (event.type) {
              case 'conversation_id':
                resolvedConversationId = event.value;
                setMessages((prev) =>
                  prev.map((m) =>
                    m.conversation_id === ''
                      ? { ...m, conversation_id: event.value }
                      : m,
                  ),
                );
                break;
              case 'token':
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last?.role === 'assistant') {
                    updated[updated.length - 1] = {
                      ...last,
                      content: last.content + event.value,
                    };
                  }
                  return updated;
                });
                break;
              case 'sources':
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last?.role === 'assistant') {
                    updated[updated.length - 1] = {
                      ...last,
                      sources: event.value,
                    };
                  }
                  return updated;
                });
                break;
              case 'error':
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last?.role === 'assistant') {
                    updated[updated.length - 1] = {
                      ...last,
                      content: `Error: ${event.value}`,
                    };
                  }
                  return updated;
                });
                break;
              case 'done':
                break;
            }
          },
          abortRef.current.signal,
        );
      } catch {
        // abort or network error — handled in UI
      } finally {
        setIsStreaming(false);
        abortRef.current = null;
      }

      return resolvedConversationId;
    },
    [],
  );

  return { messages, setMessages, isStreaming, sendMessage, stopStreaming };
}
