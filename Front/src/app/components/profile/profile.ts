import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, OnInit, inject, PLATFORM_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ApiService, BookingItem } from '../../services/api.service';
import { AuthService } from '../../services/auth';
import { HeaderComponent } from '../header/header';
import { FooterComponent } from '../footer/footer';

@Component({
  selector: 'app-profile',
  imports: [CommonModule, FormsModule, HeaderComponent, FooterComponent],
  templateUrl: './profile.html',
  styleUrl: './profile.css',
})
export class Profile implements OnInit {
  private readonly apiService = inject(ApiService);
  private readonly authService = inject(AuthService);
  private readonly platformId = inject(PLATFORM_ID);

  bookings: BookingItem[] = [];
  toast: { message: string; success: boolean } | null = null;
  username = '';

  cancelModal: { bookingId: number; tutorName: string } | null = null;
  selectedReason = '';
  isCancelling = false;
  cancelDone = false;

  readonly statusLabels: Record<string, string | undefined> = {
    pending:   'Ожидает',
    confirmed: 'Подтверждено',
    cancelled: 'Отменено',
  };

  readonly cancelReasons = [
    'Нет времени',
    'Нашёл другого тьютора',
    'Изменились планы',
    'Тьютор не ответил на связь',
    'Ошибочное бронирование',
    'Другая причина',
  ];

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      const msg = window.history.state?.['toast'] as string | undefined;
      if (msg) { this.showToast(msg, true); }
    }
    this.apiService.getMyBookings().subscribe({
      next: (items) => { this.bookings = items; },
      error: (err) => { console.error('[Profile] getMyBookings failed:', err); },
    });
  }

  logout(): void {
    this.authService.logout();
    window.location.href = '/';
  }

  openCancelModal(b: BookingItem): void {
    this.cancelModal = { bookingId: b.id, tutorName: b.tutor_name };
    this.selectedReason = '';
  }

  closeCancelModal(): void {
    this.cancelModal = null;
    this.selectedReason = '';
  }

  confirmCancel(): void {
    if (!this.cancelModal || !this.selectedReason || this.isCancelling) return;
    this.isCancelling = true;
    const id = this.cancelModal.bookingId;
    this.apiService.cancelBooking(id).subscribe({
      next: () => {
        this.bookings = this.bookings.map(b =>
          b.id === id ? { ...b, status: 'cancelled' as const } : b
        );
        this.closeCancelModal();
        this.isCancelling = false;
        this.showToast('Бронирование отменено', true);
      },
      error: () => {
        this.isCancelling = false;
        this.showToast('Не удалось отменить. Попробуйте ещё раз.', false);
      },
    });
  }

  private showToast(message: string, success: boolean): void {
    this.toast = { message, success };
    setTimeout(() => (this.toast = null), 4000);
  }
}
