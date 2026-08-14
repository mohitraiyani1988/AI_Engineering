export interface ModelOption {
  id: string;
  provider: 'gemini' | 'groq' | 'mistral';
  display_name: string;
  model_name: string;
  configured: boolean;
}

export interface TemplateField {
  name: string;
  label: string;
  type: 'text' | 'select' | 'number';
  required: boolean;
  options: string[];
  default: string | number | null;
}

export interface TemplateOption {
  id: string;
  name: string;
  description: string;
  fields: TemplateField[];
}

export interface ResponseDetails {
  provider: string;
  model_id: string;
  model_name: string;
  input_tokens: number | null;
  output_tokens: number | null;
  total_tokens: number | null;
  reasoning_tokens: number | null;
  finish_reason: string | null;
  latency_ms: number;
  time_to_first_token_ms: number | null;
  chunk_count: number;
  raw_usage_metadata: Record<string, unknown>;
  raw_response_metadata: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  details?: ResponseDetails;
  streaming?: boolean;
}

export interface SseEvent<T = Record<string, unknown>> {
  event: 'start' | 'token' | 'done' | 'error';
  data: T;
}
