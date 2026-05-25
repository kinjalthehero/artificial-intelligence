export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  model: string | null;
  created_at: string;
}

export interface Conversation {
  id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface ConversationDetail extends Conversation {
  messages: Message[];
}

export interface ModelInfo {
  name: string;
  size: number | null;
  modified_at: string | null;
}

export interface ModelsResponse {
  models: ModelInfo[];
  default_model: string;
}

export interface HealthResponse {
  status: string;
  ollama_connected: boolean;
  ollama_host: string;
}

export interface Document {
  id: string;
  conversation_id: string | null;
  filename: string;
  file_type: string;
  chunk_count: number;
  collection_name: string;
  uploaded_at: string;
}

export interface SourceChunk {
  document_id: string;
  filename: string;
  chunk_index: number;
  page: number;
  content: string;
  score: number;
}

export type SSEEvent =
  | { type: 'conversation_id'; value: string }
  | { type: 'token'; value: string }
  | { type: 'sources'; value: SourceChunk[] }
  | { type: 'done' }
  | { type: 'error'; value: string };
