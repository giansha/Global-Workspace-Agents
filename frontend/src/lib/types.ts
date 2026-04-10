export interface TickSnapshot {
  tick: number
  rag_queries: string[]
  rag_context: string
  entropy: number
  T_gen: number
  candidates: string[]
  evaluations: [number, string][]
  winning_thought: string
  transition_tag: 'THINK_MORE' | 'RESPONSE'
  stm_token_count: number
  compressed: boolean
  final_response: string | null
}

export interface GWAConfig {
  api_base_url: string
  api_key: string
  chat_model: string
  low_level_model: string
  high_level_model: string
  embedding_model: string
  N: number
  K: number
  T_base: number
  alpha: number
  beta: number
  tau: number
  theta: number
  entropy_window: number
  max_ticks: number
  critic_temperature: number
  meta_temperature: number
  top_k_rag: number
  chroma_persist_dir: string
  attention_max_tokens: number
  generator_max_tokens: number
  critic_max_tokens: number
  meta_max_tokens: number
  response_max_tokens: number
  idle_interval: number
  idle_enabled: boolean
  default_language: string
}

export interface WorkspaceStats {
  initialized: boolean
  stm_tokens: number
  ltm_documents: number
  total_ticks: number
  last_entropy: number
  last_T_gen: number
}

export interface DebugEvent {
  agent: 'attention' | 'generator' | 'critic' | 'meta' | 'response'
  tick: number
  token: string
}

export interface ConversationTurn {
  id: string
  role: 'user' | 'assistant'
  content: string
  ticks: TickSnapshot[]
}

export const DEFAULT_CONFIG: GWAConfig = {
  api_base_url: 'https://api.openai.com/v1',
  api_key: '',
  chat_model: 'gpt-4o',
  low_level_model: '',
  high_level_model: '',
  embedding_model: 'text-embedding-3-small',
  N: 3,
  K: 5,
  T_base: 0.7,
  alpha: 1.3,
  beta: 2.0,
  tau: 0.5,
  theta: 3000,
  entropy_window: 10,
  max_ticks: 8,
  critic_temperature: 0.1,
  meta_temperature: 0.3,
  top_k_rag: 3,
  chroma_persist_dir: './chroma_db',
  attention_max_tokens: 256,
  generator_max_tokens: 1024,
  critic_max_tokens: 1024,
  meta_max_tokens: 1024,
  response_max_tokens: 512,
  idle_interval: 30,
  idle_enabled: false,
  default_language: 'English',
}

export interface StmEntry {
  role: string
  content: string
  tick: number
}

export interface WorkspaceData {
  stm_entries: StmEntry[]
  ltm_count: number
  ltm_last_knowledge: string
  rag_context: string
  rag_queries: string[]
}
