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
  response_content: string;
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
  event: 'start' | 'token' | 'done' | 'error' | 'model_result' | 'model_error';
  data: T;
}

export interface ReviewAnalysis {
  sentiment: 'positive' | 'neutral' | 'negative';
  rating: number;
  summary: string;
  pros: string[];
  cons: string[];
  recommendation: boolean;
}

export interface ReviewModelResult {
  model_id: string;
  provider: string;
  model_name: string;
  strategy: 'native' | 'parser';
  analysis: ReviewAnalysis;
  details: ResponseDetails;
}

export interface ReviewResultCard {
  model: ModelOption;
  status: 'pending' | 'success' | 'error';
  result?: ReviewModelResult;
  error?: string;
}
