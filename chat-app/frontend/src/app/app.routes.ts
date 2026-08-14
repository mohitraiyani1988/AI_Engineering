import { Routes } from '@angular/router';
import { GeneralChat } from './features/general-chat/general-chat';
import { TemplateChat } from './features/template-chat/template-chat';

export const routes: Routes = [
  { path: 'general-chat', component: GeneralChat, title: 'General Chat' },
  { path: 'template-chat', component: TemplateChat, title: 'Template Chat' },
  { path: '', pathMatch: 'full', redirectTo: 'general-chat' },
  { path: '**', redirectTo: 'general-chat' },
];
