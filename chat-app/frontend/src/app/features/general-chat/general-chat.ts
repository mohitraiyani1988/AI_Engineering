import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

import { ChatApiService } from '../../core/chat-api.service';
import { ChatMessage, ModelOption, ResponseDetails } from '../../core/api.models';
import { MessageList } from '../../shared/message-list/message-list';

@Component({
  selector: 'app-general-chat',
  imports: [FormsModule, MessageList],
  templateUrl: './general-chat.html',
  styleUrl: './general-chat.scss',
})
export class GeneralChat implements OnInit {
  private readonly api = inject(ChatApiService);

  readonly models = signal<ModelOption[]>([]);
  readonly messages = signal<ChatMessage[]>([]);
  readonly loading = signal(false);
  readonly error = signal('');
  selectedModel = '';
  prompt = '';

  async ngOnInit(): Promise<void> {
    try {
      const models = await this.api.getModels();
      this.models.set(models);
      this.selectedModel = models.find((model) => model.configured)?.id ?? models[0]?.id ?? '';
    } catch (error) {
      this.error.set(this.errorMessage(error));
    }
  }

  async send(): Promise<void> {
    const content = this.prompt.trim();
    if (!content || !this.selectedModel || this.loading()) return;

    this.error.set('');
    this.prompt = '';
    const history = this.messages()
      .filter((message) => !message.streaming)
      .map(({ role, content: messageContent }) => ({ role, content: messageContent }));
    const userMessage: ChatMessage = { id: crypto.randomUUID(), role: 'user', content };
    const assistantId = crypto.randomUUID();
    this.messages.update((items) => [
      ...items,
      userMessage,
      { id: assistantId, role: 'assistant', content: '', streaming: true },
    ]);
    this.loading.set(true);

    try {
      for await (const event of this.api.streamGeneralChat({
        model_id: this.selectedModel,
        message: content,
        history,
      })) {
        if (event.event === 'token') {
          this.updateAssistant(assistantId, (message) => ({
            ...message,
            content: message.content + String(event.data['text'] ?? ''),
          }));
        } else if (event.event === 'done') {
          this.updateAssistant(assistantId, (message) => ({
            ...message,
            streaming: false,
            details: event.data['details'] as ResponseDetails,
          }));
        } else if (event.event === 'error') {
          throw new Error(String(event.data['message'] ?? 'The model request failed.'));
        }
      }
    } catch (error) {
      this.error.set(this.errorMessage(error));
      this.updateAssistant(assistantId, (message) => ({
        ...message,
        content: message.content || 'Unable to generate a response.',
        streaming: false,
      }));
    } finally {
      this.loading.set(false);
    }
  }

  clear(): void {
    this.messages.set([]);
    this.error.set('');
  }

  private updateAssistant(id: string, update: (message: ChatMessage) => ChatMessage): void {
    this.messages.update((items) => items.map((item) => (item.id === id ? update(item) : item)));
  }

  private errorMessage(error: unknown): string {
    return error instanceof Error ? error.message : 'Unable to connect to the backend.';
  }
}
