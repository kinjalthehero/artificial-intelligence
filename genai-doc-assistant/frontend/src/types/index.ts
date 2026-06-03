export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  agent_steps?: string | null;
  sources?: string | null;
  created_at: string;
}

export interface AgentStep {
  agent: 'planner' | 'retriever' | 'reasoning' | 'response' | 'verification';
  action: string;
  result: string;
  duration_ms: number;
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

export interface HealthResponse {
  status: string;
  gemini_connected: boolean;
  version: string;
  documents_count: number;
  environment: string;
}

export interface Document {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  chunk_count: number;
  collection_name: string;
  status: string;
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
  | { type: 'agent_step'; value: AgentStep }
  | { type: 'token'; value: string }
  | { type: 'sources'; value: SourceChunk[] }
  | { type: 'agent_steps'; value: AgentStep[] }
  | { type: 'done' }
  | { type: 'error'; value: string };
