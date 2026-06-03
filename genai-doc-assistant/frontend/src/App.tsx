import { useCallback, useState } from 'react';
import { api } from './api/client';
import { Sidebar } from './components/Layout/Sidebar';
import { ChatArea } from './components/Chat/ChatArea';
import { LoadingScreen } from './components/Common/LoadingScreen';
import { useChat } from './hooks/useChat';
import { useConversations } from './hooks/useConversations';
import { useDocuments } from './hooks/useDocuments';
import { useTheme } from './hooks/useTheme';
import { useHealth } from './hooks/useHealth';

function App() {
  const { healthy, geminiConnected } = useHealth();
  const { dark, toggle: toggleTheme } = useTheme();
  const { messages, setMessages, isStreaming, currentAgent, sendMessage, stopStreaming } = useChat();
  const {
    conversations,
    refresh: refreshConversations,
    remove: removeConversation,
    search: searchConversations,
    clearSearch,
    isSearching,
  } = useConversations();
  const {
    documents,
    uploading,
    upload: uploadDocument,
    remove: removeDocument,
    clear: clearDocuments,
  } = useDocuments();

  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);

  const handleSelectConversation = useCallback(
    async (id: string) => {
      if (isStreaming) return;
      try {
        const detail = await api.getConversation(id);
        setActiveConversationId(id);
        setMessages(detail.messages);
      } catch {
        // conversation may have been deleted
      }
    },
    [isStreaming, setMessages],
  );

  const handleNewChat = useCallback(() => {
    if (isStreaming) return;
    setActiveConversationId(null);
    setMessages([]);
    clearDocuments();
  }, [isStreaming, setMessages, clearDocuments]);

  const handleSend = useCallback(
    async (text: string) => {
      const docIds = documents.map((d) => d.id);
      const convId = await sendMessage(text, activeConversationId, docIds);
      if (convId && convId !== activeConversationId) {
        setActiveConversationId(convId);
      }
      refreshConversations();
    },
    [activeConversationId, documents, sendMessage, refreshConversations],
  );

  const handleDelete = useCallback(
    async (id: string) => {
      await removeConversation(id);
      if (activeConversationId === id) {
        setActiveConversationId(null);
        setMessages([]);
      }
    },
    [activeConversationId, removeConversation, setMessages],
  );

  const handleUpload = useCallback(
    async (file: File) => {
      await uploadDocument(file);
    },
    [uploadDocument],
  );

  const handleRemoveDoc = useCallback(
    async (id: string) => {
      await removeDocument(id);
    },
    [removeDocument],
  );

  if (healthy === false) {
    return <LoadingScreen />;
  }

  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar
        conversations={conversations}
        activeId={activeConversationId}
        onSelect={handleSelectConversation}
        onNew={handleNewChat}
        onDelete={handleDelete}
        onSearch={searchConversations}
        onClearSearch={clearSearch}
        isSearching={isSearching}
        dark={dark}
        onToggleTheme={toggleTheme}
      />
      <ChatArea
        messages={messages}
        isStreaming={isStreaming}
        currentAgent={currentAgent}
        onSend={handleSend}
        onStop={stopStreaming}
        onUpload={handleUpload}
        uploading={uploading}
        attachedDocs={documents}
        onRemoveDoc={handleRemoveDoc}
        geminiConnected={geminiConnected}
      />
    </div>
  );
}

export default App;
