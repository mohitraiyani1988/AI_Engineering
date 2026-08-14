import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ChatApiService } from '../../core/chat-api.service';
import { ChatMessage, ModelOption, ResponseDetails, TemplateOption } from '../../core/api.models';
import { MessageList } from '../../shared/message-list/message-list';

@Component({
  selector: 'app-template-chat',
  imports: [FormsModule, MessageList],
  templateUrl: './template-chat.html',
  styleUrl: './template-chat.scss',
})
export class TemplateChat implements OnInit {
  private readonly api = inject(ChatApiService);
  readonly models = signal<ModelOption[]>([]);
  readonly templates = signal<TemplateOption[]>([]);
  readonly messages = signal<ChatMessage[]>([]);
  readonly loading = signal(false);
  readonly error = signal('');
  selectedModel = '';
  selectedTemplateId = '';
  inputs: Record<string, string | number> = {};

  get selectedTemplate(): TemplateOption | undefined {
    return this.templates().find((template) => template.id === this.selectedTemplateId);
  }

  async ngOnInit(): Promise<void> {
    try {
      const [models, templates] = await Promise.all([this.api.getModels(), this.api.getTemplates()]);
      this.models.set(models);
      this.templates.set(templates);
      this.selectedModel = models.find((model) => model.configured)?.id ?? models[0]?.id ?? '';
      this.selectedTemplateId = templates[0]?.id ?? '';
      this.resetInputs();
    } catch (error) {
      this.error.set(this.errorMessage(error));
    }
  }

  resetInputs(): void {
    this.inputs = Object.fromEntries(
      (this.selectedTemplate?.fields ?? []).map((field) => [field.name, field.default ?? '']),
    );
  }

  async generate(): Promise<void> {
    if (!this.selectedTemplate || !this.selectedModel || this.loading()) return;
    this.error.set('');
    const summary = this.selectedTemplate.fields
      .map((field) => `${field.label}: ${this.inputs[field.name]}`)
      .join('\n');
    const assistantId = crypto.randomUUID();
    this.messages.update((items) => [
      ...items,
      { id: crypto.randomUUID(), role: 'user', content: summary },
      { id: assistantId, role: 'assistant', content: '', streaming: true },
    ]);
    this.loading.set(true);

    try {
      for await (const event of this.api.streamTemplateChat(this.selectedTemplate.id, {
        model_id: this.selectedModel,
        inputs: this.inputs,
      })) {
        if (event.event === 'token') {
          this.updateAssistant(assistantId, (message) => ({ ...message, content: message.content + String(event.data['text'] ?? '') }));
        } else if (event.event === 'done') {
          this.updateAssistant(assistantId, (message) => ({ ...message, streaming: false, details: event.data['details'] as ResponseDetails }));
        } else if (event.event === 'error') {
          throw new Error(String(event.data['message'] ?? 'The model request failed.'));
        }
      }
    } catch (error) {
      this.error.set(this.errorMessage(error));
      this.updateAssistant(assistantId, (message) => ({ ...message, content: message.content || 'Unable to generate a response.', streaming: false }));
    } finally {
      this.loading.set(false);
    }
  }

  private updateAssistant(id: string, update: (message: ChatMessage) => ChatMessage): void {
    this.messages.update((items) => items.map((item) => (item.id === id ? update(item) : item)));
  }

  private errorMessage(error: unknown): string {
    return error instanceof Error ? error.message : 'Unable to connect to the backend.';
  }
}
