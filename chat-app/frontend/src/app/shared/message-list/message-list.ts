import { Component, input } from '@angular/core';
import { JsonPipe } from '@angular/common';

import { ChatMessage } from '../../core/api.models';

@Component({
  selector: 'app-message-list',
  imports: [JsonPipe],
  templateUrl: './message-list.html',
  styleUrl: './message-list.scss',
})
export class MessageList {
  readonly messages = input.required<ChatMessage[]>();
}
