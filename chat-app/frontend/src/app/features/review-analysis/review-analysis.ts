import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { JsonPipe } from '@angular/common';

import { ChatApiService } from '../../core/chat-api.service';
import {
  ModelOption,
  ReviewModelResult,
  ReviewResultCard,
} from '../../core/api.models';

@Component({
  selector: 'app-review-analysis',
  imports: [FormsModule, JsonPipe],
  templateUrl: './review-analysis.html',
  styleUrl: './review-analysis.scss',
})
export class ReviewAnalysis implements OnInit {
  private readonly api = inject(ChatApiService);

  readonly models = signal<ModelOption[]>([]);
  readonly selectedModelIds = signal<Set<string>>(new Set());
  readonly cards = signal<ReviewResultCard[]>([]);
  readonly loading = signal(false);
  readonly error = signal('');

  review = '';
  strategy: 'native' | 'parser' = 'native';

  async ngOnInit(): Promise<void> {
    try {
      const models = await this.api.getModels();
      this.models.set(models);
      this.selectedModelIds.set(
        new Set(models.filter((model) => model.configured).map((model) => model.id)),
      );
    } catch (error) {
      this.error.set(this.errorMessage(error));
    }
  }

  toggleModel(modelId: string, checked: boolean): void {
    this.selectedModelIds.update((current) => {
      const next = new Set(current);
      checked ? next.add(modelId) : next.delete(modelId);
      return next;
    });
  }

  async analyze(): Promise<void> {
    const review = this.review.trim();
    const modelIds = [...this.selectedModelIds()];
    if (!review || modelIds.length === 0 || this.loading()) return;

    this.error.set('');
    this.cards.set(
      modelIds.map((id) => ({
        model: this.models().find((model) => model.id === id)!,
        status: 'pending',
      })),
    );
    this.loading.set(true);

    try {
      for await (const event of this.api.streamReviewAnalysis({
        review,
        model_ids: modelIds,
        strategy: this.strategy,
      })) {
        if (event.event === 'model_result') {
          const result = event.data as unknown as ReviewModelResult;
          this.updateCard(result.model_id, {
            status: 'success',
            result,
          });
        } else if (event.event === 'model_error') {
          this.updateCard(String(event.data['model_id']), {
            status: 'error',
            error: String(event.data['message'] ?? 'Analysis failed.'),
          });
        }
      }
    } catch (error) {
      const message = this.errorMessage(error);
      this.error.set(message);
      this.cards.update((cards) =>
        cards.map((card) =>
          card.status === 'pending' ? { ...card, status: 'error', error: message } : card,
        ),
      );
    } finally {
      this.loading.set(false);
    }
  }

  private updateCard(
    modelId: string,
    change: Pick<ReviewResultCard, 'status' | 'result' | 'error'>,
  ): void {
    this.cards.update((cards) =>
      cards.map((card) => (card.model.id === modelId ? { ...card, ...change } : card)),
    );
  }

  private errorMessage(error: unknown): string {
    return error instanceof Error ? error.message : 'Unable to connect to the backend.';
  }
}
