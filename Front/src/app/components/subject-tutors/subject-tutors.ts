import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, OnInit, inject, PLATFORM_ID } from '@angular/core';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { ApiService, TutorDetail } from '../../services/api.service';
import { HeaderComponent } from '../header/header';
import { FooterComponent } from '../footer/footer';

@Component({
  selector: 'app-subject-tutors',
  imports: [CommonModule, FormsModule, RouterLink, HeaderComponent, FooterComponent],
  templateUrl: './subject-tutors.html',
  styleUrl: './subject-tutors.css',
})
export class SubjectTutors implements OnInit {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly apiService = inject(ApiService);
  private readonly platformId = inject(PLATFORM_ID);

  tutors: TutorDetail[] = [];
  filtered: TutorDetail[] = [];
  subjectName = '';

  minPrice = 0;
  maxPrice = 99999;
  selectedFormat: 'all' | 'online' | 'offline' = 'all';
  minRating = 0;
  selectedCourse = 0;
  sortBy: 'rating' | 'name' = 'rating';

  readonly ratingOptions = [
    { label: 'Любой', value: 0 },
    { label: '3.0+', value: 3 },
    { label: '3.5+', value: 3.5 },
    { label: '4.0+', value: 4 },
    { label: '4.5+', value: 4.5 },
  ];

  readonly courseOptions = [
    { label: 'Все курсы', value: 0 },
    { label: '1 курс', value: 1 },
    { label: '2 курс', value: 2 },
    { label: '3 курс', value: 3 },
    { label: '4 курс', value: 4 },
  ];

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id') ?? '';

    if (isPlatformBrowser(this.platformId)) {
      this.subjectName = (window.history.state?.['subjectName'] as string) ?? '';
    }

    this.apiService.getTutorsBySubject(id).subscribe({
      next: (data) => {
        this.tutors = Array.isArray(data) ? data : (data as any)['results'] ?? [];
        this.applyFilters();
      },
      error: (err) => { console.error('[SubjectTutors] getTutorsBySubject failed:', err); },
    });
  }

  applyFilters(): void {
    this.filtered = this.tutors
      .filter((t) => {
        const rate = Number(t.hourly_rate) || 0;
        const rating = Number(t.rating) || 0;
        const matchesPrice = rate >= this.minPrice && rate <= this.maxPrice;
        const matchesRating = rating >= this.minRating;
        const matchesCourse = this.selectedCourse === 0 || t.experience_years === this.selectedCourse;
        return matchesPrice && matchesRating && matchesCourse;
      })
      .sort((a, b) => {
        if (this.sortBy === 'rating') return (Number(b.rating) || 0) - (Number(a.rating) || 0);
        return a.user.username.localeCompare(b.user.username);
      });
  }

  goToTutor(id: number): void {
    this.router.navigate(['/tutor', id]);
  }

  getStars(rating: string): boolean[] {
    const filled = Math.round(Number(rating) || 0);
    return Array.from({ length: 5 }, (_, i) => i < filled);
  }
}
