import { CommonModule } from '@angular/common';
import { Component, OnInit, inject } from '@angular/core';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { ApiService, TutorSubject } from '../../services/api.service';
import { HeaderComponent } from '../header/header';
import { FooterComponent } from '../footer/footer';

@Component({
  selector: 'app-become-tutor',
  imports: [CommonModule, ReactiveFormsModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './become-tutor.html',
  styleUrl: './become-tutor.css',
})
export class BecomeTutor implements OnInit {
  private readonly fb = inject(FormBuilder);
  private readonly apiService = inject(ApiService);
  private readonly router = inject(Router);

  isSubmitting = false;
  submitError = '';
  submitSuccess = false;
  subjects: TutorSubject[] = [];
  serverErrors: Record<string, string> = {};

  ngOnInit(): void {
    this.apiService.getSubjects().subscribe({
      next: (subjects) => { this.subjects = subjects; },
    });
  }

  form = this.fb.group({
    subject_id: [null as number | null, Validators.required],
    experience_years: [null as number | null, [Validators.required, Validators.min(2), Validators.max(10)]],
    bio: ['', [Validators.required, Validators.minLength(50)]],
    hourly_rate: [null as number | null, [Validators.required, Validators.min(500), Validators.max(10000)]],
  });

  get f() { return this.form.controls; }

  serverError(field: string): string {
    return this.serverErrors[field] ?? '';
  }

  onSubmit(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.isSubmitting = true;
    this.submitError = '';
    this.serverErrors = {};
    const { subject_id, experience_years, bio, hourly_rate } = this.form.value;
    this.apiService.createTutorProfile({
      subject_id: subject_id!,
      experience_years: experience_years!,
      bio: bio!,
      hourly_rate: hourly_rate!,
    }).subscribe({
      next: () => {
        this.isSubmitting = false;
        this.submitSuccess = true;
        setTimeout(() => this.router.navigate(['/'], { state: { toast: 'Ваш профиль тьютора создан!' } }), 1800);
      },
      error: (err) => {
        this.isSubmitting = false;
        const body = err?.error;
        if (body && typeof body === 'object' && !body['detail']) {
          const fieldMap: Record<string, string> = {
            subject_id: 'subject_id',
            experience_years: 'experience_years',
            bio: 'bio',
            hourly_rate: 'hourly_rate',
          };
          for (const key of Object.keys(fieldMap)) {
            if (body[key]) {
              this.serverErrors[key] = Array.isArray(body[key]) ? body[key][0] : body[key];
            }
          }
          if (Object.keys(this.serverErrors).length === 0) {
            this.submitError = body['non_field_errors']?.[0] ?? 'Ошибка при сохранении. Попробуйте ещё раз.';
          }
        } else {
          this.submitError = body?.['detail'] ?? 'Ошибка при сохранении. Попробуйте ещё раз.';
        }
      },
    });
  }
}
