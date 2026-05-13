import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-verify-email',
  imports: [CommonModule, RouterLink],
  template: `
    <div style="max-width:480px;margin:80px auto;text-align:center;font-family:Arial,sans-serif">
      <ng-container *ngIf="state === 'loading'">
        <p>Подтверждаем ваш email...</p>
      </ng-container>
      <ng-container *ngIf="state === 'success'">
        <h2 style="color:#4f46e5">Email подтверждён!</h2>
        <p>Ваш аккаунт успешно активирован.</p>
        <a routerLink="/login" style="color:#4f46e5">Войти</a>
      </ng-container>
      <ng-container *ngIf="state === 'error'">
        <h2 style="color:#dc2626">Ошибка</h2>
        <p>{{ errorMessage }}</p>
        <a routerLink="/" style="color:#4f46e5">На главную</a>
      </ng-container>
    </div>
  `,
})
export class VerifyEmail implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly apiService = inject(ApiService);

  state: 'loading' | 'success' | 'error' = 'loading';
  errorMessage = '';

  ngOnInit(): void {
    const token = this.route.snapshot.queryParamMap.get('token') ?? '';
    if (!token) {
      this.state = 'error';
      this.errorMessage = 'Токен не найден в ссылке.';
      return;
    }
    this.apiService.verifyEmail(token).subscribe({
      next: () => { this.state = 'success'; },
      error: (err) => {
        this.state = 'error';
        this.errorMessage = err?.error?.detail ?? 'Недействительная или устаревшая ссылка.';
      },
    });
  }
}
