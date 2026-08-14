import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { ModelOption, SseEvent, TemplateOption } from './api.models';

@Injectable({ providedIn: 'root' })
export class ChatApiService {
  private readonly http = inject(HttpClient);
  private readonly baseUrl = 'http://127.0.0.1:8000';

  getModels(): Promise<ModelOption[]> {
    return firstValueFrom(this.http.get<ModelOption[]>(`${this.baseUrl}/models`));
  }

  getTemplates(): Promise<TemplateOption[]> {
    return firstValueFrom(this.http.get<TemplateOption[]>(`${this.baseUrl}/templates`));
  }

  streamGeneralChat(body: object): AsyncGenerator<SseEvent> {
    return this.stream('/chat/stream', body);
  }

  streamTemplateChat(templateId: string, body: object): AsyncGenerator<SseEvent> {
    return this.stream(`/templates/${encodeURIComponent(templateId)}/stream`, body);
  }

  private async *stream(path: string, body: object): AsyncGenerator<SseEvent> {
    const response = await fetch(`${this.baseUrl}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => null);
      throw new Error(errorBody?.detail ?? `Request failed with status ${response.status}`);
    }
    if (!response.body) {
      throw new Error('The browser did not provide a response stream.');
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      buffer += decoder.decode(value, { stream: !done }).replace(/\r\n/g, '\n');
      const blocks = buffer.split('\n\n');
      buffer = blocks.pop() ?? '';

      for (const block of blocks) {
        const parsed = this.parseEvent(block);
        if (parsed) yield parsed;
      }

      if (done) break;
    }

    if (buffer.trim()) {
      const parsed = this.parseEvent(buffer);
      if (parsed) yield parsed;
    }
  }

  private parseEvent(block: string): SseEvent | null {
    let event = '';
    const dataLines: string[] = [];
    for (const line of block.split('\n')) {
      if (line.startsWith('event:')) event = line.slice(6).trim();
      if (line.startsWith('data:')) dataLines.push(line.slice(5).trim());
    }
    if (!event || dataLines.length === 0) return null;
    return { event, data: JSON.parse(dataLines.join('\n')) } as SseEvent;
  }
}
