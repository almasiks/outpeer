import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';

export interface TutorSubject {
  id: number;
  name: string;
  description: string;
}

export interface TutorUser {
  id: number;
  username: string;
  email: string;
}

export interface TutorDetail {
  id: number;
  user: TutorUser;
  subject: TutorSubject | null;
  experience_years: number;
  bio: string;
  hourly_rate: string;
  rating: string;
}

export interface LoginPayload {
  username: string;
  password: string;
}

export interface RegisterPayload {
  username: string;
  email: string;
  password: string;
  is_tutor?: boolean;
}

export interface LoginResponse {
  token?: string;
  access?: string;
  refresh?: string;
  user?: {
    id: number;
    username: string;
    email: string;
    role?: string;
  };
  user_id: number;
  username: string;
}

export interface BookingItem {
  id: number;
  tutor: number;
  tutor_name: string;
  tutor_subject: string;
  tutor_hourly_rate: string;
  student: number;
  student_username: string;
  date: string;
  status: 'pending' | 'confirmed' | 'cancelled';
}

export interface BookingPayload {
  tutor: number;
  date: string;
  status?: 'pending' | 'confirmed' | 'cancelled';
}

export interface TutorProfilePayload {
  subject_id: number;
  experience_years: number;
  bio: string;
  hourly_rate: number;
}

export interface ReviewItem {
  id: number;
  tutor: number;
  student: number;
  student_username: string;
  booking: number | null;
  rating: number;
  comment: string;
  created_at: string;
}

export interface ReviewPayload {
  rating: number;
  comment?: string;
  booking?: number | null;
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly http = inject(HttpClient);
  readonly baseUrl = environment.apiUrl;

  getTutors(): Observable<TutorDetail[]> {
    return this.http.get<TutorDetail[]>(`${this.baseUrl}/tutors/`);
  }

  getTutorById(id: number): Observable<TutorDetail> {
    return this.http.get<TutorDetail>(`${this.baseUrl}/tutors/${id}/`);
  }

  login(credentials: LoginPayload): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/auth/login/`, credentials);
  }

  register(data: RegisterPayload): Observable<LoginResponse> {
    return this.http.post<LoginResponse>(`${this.baseUrl}/auth/register/`, data);
  }

  createBooking(payload: BookingPayload): Observable<BookingItem> {
    return this.http.post<BookingItem>(`${this.baseUrl}/bookings/`, payload);
  }

  getMyBookings(): Observable<BookingItem[]> {
    return this.http.get<BookingItem[]>(`${this.baseUrl}/my-bookings/`);
  }

  cancelBooking(id: number): Observable<BookingItem> {
    return this.http.patch<BookingItem>(`${this.baseUrl}/bookings/${id}/`, { status: 'cancelled' });
  }

  rateTutor(tutorId: number, score: number): Observable<{ rating: string }> {
    return this.http.post<{ rating: string }>(`${this.baseUrl}/tutors/${tutorId}/rate/`, { score });
  }

  getMyProfile(): Observable<TutorDetail> {
    return this.http.get<TutorDetail>(`${this.baseUrl}/tutors/profile/`);
  }

  getTutorsBySubject(subjectId: string | number): Observable<TutorDetail[]> {
    return this.http.get<TutorDetail[]>(`${this.baseUrl}/tutors/?subject=${subjectId}`);
  }

  createTutorProfile(payload: TutorProfilePayload): Observable<TutorDetail> {
    return this.http.post<TutorDetail>(`${this.baseUrl}/tutors/create/`, payload);
  }

  getSubjects(): Observable<TutorSubject[]> {
    return this.http.get<TutorSubject[]>(`${this.baseUrl}/subjects/`);
  }

  verifyEmail(token: string): Observable<{ detail: string }> {
    return this.http.get<{ detail: string }>(`${this.baseUrl}/auth/verify-email/`, { params: { token } });
  }

  getTutorReviews(tutorId: number): Observable<ReviewItem[]> {
    return this.http.get<ReviewItem[]>(`${this.baseUrl}/tutors/${tutorId}/reviews/`);
  }

  createReview(tutorId: number, payload: ReviewPayload): Observable<ReviewItem> {
    return this.http.post<ReviewItem>(`${this.baseUrl}/tutors/${tutorId}/reviews/`, payload);
  }
}
