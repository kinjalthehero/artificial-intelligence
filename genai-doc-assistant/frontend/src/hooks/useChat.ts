import { useCallback, useRef, useState } from 'react';
import { api } from '../api/client';
import type { AgentStep, Message, SourceChunk } from '../types';

export interface MessageWithSources extends Message {
  parsedSources?: SourceChunk[];
  agentSteps?: AgentStep[];
}

interface UseChatReturn {
  messages: MessageWithSources[];
  setMessages: React.Dispatch<React.SetStateAction<MessageWithSources[]>>;
  isStreaming: boolean;
  currentAgent: string | null;
  sendMessage: (
    text: string,
    conversationId: string | null,
    documentIds: string[],
  ) => Promise<string | null>;
  stopStreaming: () => void;
}

export function useChat(): UseChatReturn {
  const [messages, setMessages] = useState<MessageWithSources[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentAgent, setCurrentAgent] = useState<string | null>(null);
  const abortRef = useRef<AbortController | null>(null);

  const stopStreaming = useCallback(() => {
    abortRef.current?.abort();
    abortRef.current = null;
    setIsStreaming(false);
    setCurrentAgent(null);
  }, []);

  const sendMessage = useCallback(
    async (
      text: string,
      conversationId: string | null,
      documentIds: string[],
    ): Promise<string | null> => {
      const userMsg: MessageWithSources = {
        id: self.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2) + Date.now().toString(36),
        conversation_id: conversationId || '',
        role: 'user',
        content: text,
        created_at: new Date().toISOString(),
      };
      setMessages((prev) => [...prev, userMsg]);

      const assistantMsg: MessageWithSources = {
        id: self.crypto?.randomUUID?.() ?? Math.random().toString(36).slice(2) + Date.now().toString(36),
        conversation_id: conversationId || '',
        role: 'assistant',
        content: '',
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
              case 'agent_step':
                setCurrentAgent(event.value.agent);
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last?.role === 'assistant') {
                    const steps = last.agentSteps || [];
                    updated[updated.length - 1] = {
                      ...last,
                      agentSteps: [...steps, event.value],
                    };
                  }
                  return updated;
                });
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
                      parsedSources: event.value,
                    };
                  }
                  return updated;
                });
                break;
              case 'agent_steps':
                setMessages((prev) => {
                  const updated = [...prev];
                  const last = updated[updated.length - 1];
                  if (last?.role === 'assistant') {
                    updated[updated.length - 1] = {
                      ...last,
                      agentSteps: event.value,
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
        // abort or network error
      } finally {
        setIsStreaming(false);
        setCurrentAgent(null);
        abortRef.current = null;
      }

      return resolvedConversationId;
    },
    [],
  );

  return { messages, setMessages, isStreaming, currentAgent, sendMessage, stopStreaming };
}
