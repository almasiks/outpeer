import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, OnInit, inject, PLATFORM_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService, TutorDetail, TutorSubject } from '../../services/api.service';
import { AuthService } from '../../services/auth';
import { HeaderComponent } from '../header/header';
import { FooterComponent } from '../footer/footer';

interface SubjectItem extends TutorSubject {
  icon: string;
}

@Component({
  selector: 'app-home',
  imports: [CommonModule, FormsModule, HeaderComponent, FooterComponent],
  templateUrl: './home.html',
  styleUrl: './home.css',
})
export class Home implements OnInit {
  private readonly apiService = inject(ApiService);
  private readonly authService = inject(AuthService);
  private readonly router = inject(Router);
  private readonly platformId = inject(PLATFORM_ID);

  tutors: TutorDetail[] = [];
  filteredTutors: TutorDetail[] = [];
  subjectItems: SubjectItem[] = [];
  tutorsLoaded = false;
  ratingInProgress: number | null = null;
  toast: { message: string; success: boolean } | null = null;

  searchQuery = '';
  selectedSubject = '';

  readonly maxStars = 5;

  private readonly iconMap: Record<string, string> = {
    'Web Разработка': '</>',
    'Академический казахский язык (B2)': 'Aқ',
    'Введение в машинное обучение': 'AI',
    'ИТ инфраструктура и Компьютерные сети': 'NET',
    'Объектно-ориентированное программирование и дизайн': 'OOP',
    'Физическая культура': 'RUN',
    'Алгоритмы и структуры данных': 'DS',
    'Архитектура компьютерных систем': 'CPU',
    'Базы данных': 'SQL',
    'Принципы программирования I/II': 'CODE',
    'Статистика': 'STAT',
    'Дискретные структуры': 'DISC',
    'Иностранный язык (английский B2)': 'EN',
    'Исчисление 1/2': '∫',
    'Модуль социально-политических знаний': 'SP',
    'Философия': 'Φ',
    'Информационно-коммуникационные технологии': 'ICT',
    'История Казахстана': 'KZ',
    'Линейная алгебра для инженеров': 'LA',
    'Дифференциальные уравнения': 'DU',
    'Теория вероятностей': 'TV',
  };

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      const msg = window.history.state?.['toast'] as string | undefined;
      if (msg) { this.showToast(msg, true); }
    }
    this.loadSubjects();
    this.refreshFromServer();
  }

  private loadSubjects(): void {
    this.apiService.getSubjects().subscribe({
      next: (subjects) => {
        this.subjectItems = subjects.map(s => ({
          ...s,
          icon: this.iconMap[s.name] ?? s.name.slice(0, 3).toUpperCase(),
        }));
      },
      error: (err) => { console.error('[Home] getSubjects failed:', err); },
    });
  }

  get isAuthenticated(): boolean {
    return this.authService.isAuthenticated();
  }

  applyFilter(): void {
    const normalized = this.searchQuery.trim().toLowerCase();
    this.filteredTutors = this.tutors.filter((tutor) => {
      const subject = tutor.subject?.name ?? '';
      const matchesQuery =
        normalized.length === 0 ||
        tutor.user.username.toLowerCase().includes(normalized) ||
        subject.toLowerCase().includes(normalized);
      const matchesSubject = !this.selectedSubject || subject === this.selectedSubject;
      return matchesQuery && matchesSubject;
    });
  }

  filterBySubject(subject: string): void {
    this.selectedSubject = this.selectedSubject === subject ? '' : subject;
    this.applyFilter();
  }

  goToSubject(item: SubjectItem): void {
    this.router.navigate(['/tutors/subject', item.id], { state: { subjectName: item.name } });
  }

  refreshFromServer(): void {
    this.apiService.getTutors().subscribe({
      next: (tutors) => {
        this.tutors = tutors;
        this.tutorsLoaded = true;
        this.applyFilter();
      },
      error: (err) => { console.error('[Home] getTutors failed:', err); },
    });
  }

  private showToast(message: string, success: boolean): void {
    this.toast = { message, success };
    setTimeout(() => (this.toast = null), 3000);
  }

  selectTutor(tutorId: number): void {
    this.router.navigate(['/tutor', tutorId]);
  }

  rateTutor(tutorId: number, rating: number): void {
    this.ratingInProgress = tutorId;
    this.apiService.rateTutor(tutorId, rating).subscribe({
      next: () => {
        this.ratingInProgress = null;
        this.refreshFromServer();
      },
      error: () => {
        this.ratingInProgress = null;
      },
    });
  }

  getStars(ratingValue: string): boolean[] {
    const rating = Number(ratingValue) || 0;
    const filled = Math.round(rating);
    return Array.from({ length: this.maxStars }, (_, index) => index < filled);
  }
}
