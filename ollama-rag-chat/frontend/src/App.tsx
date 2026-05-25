import { useCallback, useState } from 'react';
import { api } from './api/client';
import { Sidebar } from './components/Sidebar/Sidebar';
import { ChatArea } from './components/Chat/ChatArea';
import { useChat } from './hooks/useChat';
import { useConversations } from './hooks/useConversations';
import { useDocuments } from './hooks/useDocuments';
import { useTheme } from './hooks/useTheme';

function App() {
  const { dark, toggle: toggleTheme } = useTheme();
  const { messages, setMessages, isStreaming, sendMessage, stopStreaming } =
    useChat();
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

  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const [selectedModel, setSelectedModel] = useState('llama3.1:8b');

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
      const convId = await sendMessage(
        text,
        activeConversationId,
        selectedModel,
        docIds,
      );
      if (convId && convId !== activeConversationId) {
        setActiveConversationId(convId);
      }
      refreshConversations();
    },
    [activeConversationId, selectedModel, documents, sendMessage, refreshConversations],
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
        selectedModel={selectedModel}
        onModelChange={setSelectedModel}
        onSend={handleSend}
        onStop={stopStreaming}
        onUpload={handleUpload}
        uploading={uploading}
        attachedDocs={documents}
        onRemoveDoc={handleRemoveDoc}
      />
    </div>
  );
}

export default App;
