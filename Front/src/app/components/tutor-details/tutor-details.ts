import { CommonModule } from '@angular/common';
import { ChangeDetectorRef, Component, OnInit, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { ApiService, ReviewItem, TutorDetail } from '../../services/api.service';
import { AuthService } from '../../services/auth';
import { HeaderComponent } from '../header/header';
import { FooterComponent } from '../footer/footer';

@Component({
  selector: 'app-tutor-details',
  imports: [CommonModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './tutor-details.html',
  styleUrl: './tutor-details.css',
})
export class TutorDetails implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly apiService = inject(ApiService);
  private readonly authService = inject(AuthService);
  private readonly cdr = inject(ChangeDetectorRef);

  tutorId = 0;
  tutor: TutorDetail | null = null;
  tutorNotFound = false;
  reviews: ReviewItem[] = [];

  isSubmitting = false;
  bookingNotice = '';
  bookingSuccess = false;

  selectedScore = 0;
  hoverScore = 0;
  ratingNotice = '';

  readonly stars = [1, 2, 3, 4, 5];

  get roundedRating(): number {
    return Math.round(Number(this.tutor?.rating) || 0);
  }

  get isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }

  ngOnInit(): void {
    this.tutorId = Number(this.route.snapshot.paramMap.get('id'));
    console.log('[TutorDetails] loading tutorId:', this.tutorId, '→', `${this.apiService.baseUrl}/tutors/${this.tutorId}/`);

    this.apiService.getTutorById(this.tutorId).subscribe({
      next: (tutor) => {
        console.log('[TutorDetails] tutor loaded:', tutor);
        this.tutor = tutor;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('[TutorDetails] getTutorById failed — status:', err?.status, err);
        this.tutorNotFound = true;
        this.cdr.detectChanges();
      },
    });

    this.apiService.getTutorReviews(this.tutorId).subscribe({
      next: (reviews) => (this.reviews = reviews),
      error: (err) => { console.error('[TutorDetails] getTutorReviews failed:', err?.status, err); },
    });
  }

  bookLesson(): void {
    if (!this.isAuthenticated) {
      this.bookingNotice = 'Войдите в систему, чтобы забронировать занятие.';
      this.bookingSuccess = false;
      return;
    }
    this.isSubmitting = true;
    this.bookingNotice = '';
    this.apiService.createBooking({
      tutor: this.tutorId,
      date: new Date().toISOString(),
      status: 'pending',
    }).subscribe({
      next: () => {
        this.bookingNotice = 'Занятие успешно забронировано! Проверьте профиль.';
        this.bookingSuccess = true;
        this.isSubmitting = false;
      },
      error: () => {
        this.bookingNotice = 'Не удалось забронировать. Попробуйте ещё раз.';
        this.bookingSuccess = false;
        this.isSubmitting = false;
      },
    });
  }

  rateTutor(score: number): void {
    this.selectedScore = score;
    this.apiService.rateTutor(this.tutorId, score).subscribe({
      next: (response) => {
        if (this.tutor) this.tutor.rating = String(response.rating);
        this.ratingNotice = 'Оценка сохранена!';
        setTimeout(() => (this.ratingNotice = ''), 3000);
      },
      error: () => {
        this.ratingNotice = 'Не удалось сохранить оценку.';
        setTimeout(() => (this.ratingNotice = ''), 3000);
      },
    });
  }
}
