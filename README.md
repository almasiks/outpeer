# Образовательная платформа "KBTU Tutor"

## Описание проекта

**KBTU Tutor** — веб-приложение для студентов КБТУ, которое помогает найти тьюторов среди сокурсников. Платформа позволяет бронировать время для консультаций по сложным предметам, помогать с лабораторными работами и готовиться к экзаменам.

---
Author: Magrupov Almas
---

## Технологический стек

### Frontend
- **Angular 17+** — SPA с роутингом и reactive forms
- **TypeScript** — строгая типизация
- **Angular SSR** — серверный рендеринг для production
- **Nginx** — раздача статики в Docker-контейнере

### Backend
- **Django 4+** — основной фреймворк
- **Django REST Framework (DRF)** — REST API
- **PostgreSQL** — основная база данных
- **Gunicorn** — WSGI-сервер для production

### Auth & Security
- **Token-based Authentication** (DRF Token Auth)
- **Email verification** — подтверждение почты с UUID-токеном (24ч TTL)
- **Роли пользователей**: `student`, `tutor`, `admin`

### DevOps
- **Docker** + **Docker Compose** — контейнеризация всех сервисов
- **PostgreSQL 16 Alpine** — БД в отдельном контейнере с healthcheck
- **Environment variables** через `.env` файл

---

## Реализованный функционал

### Аутентификация
- Регистрация с подтверждением email
- Вход / выход
- Профиль пользователя
- Верификация email по ссылке

### Тьюторы
- Список всех тьюторов
- Страница конкретного тьютора (детальная информация: предмет, опыт, рейтинг, биография, почасовая ставка)
- Фильтрация тьюторов по предмету
- Создание / редактирование профиля тьютора
- Стать тьютором (форма подачи заявки)

### Бронирование
- Просмотр свободных слотов тьютора
- Бронирование времени для сессии
- Мои бронирования (история)
- Статусы: `pending` / `confirmed` / `cancelled`

### Отзывы и рейтинг
- Оставить отзыв после занятия (оценка + комментарий)
- Просмотр всех отзывов тьютора
- Удаление своего отзыва
- Автоматический расчёт рейтинга

### Предметы
- Список предметов
- Привязка тьютора к предмету

### Email-уведомления
- Письмо с подтверждением регистрации
- Подтверждение бронирования

### Админ
- Управление пользователями через API (`/api/admin/users/`)

---

## Структура проекта

```
outpeer_final_project/
├── back/                  # Django backend
│   ├── accounts/          # Пользователи, роли, email-верификация
│   ├── api/               # Тьюторы, бронирования, отзывы, предметы
│   ├── myproject/         # Настройки Django
│   ├── templates/         # Email-шаблоны
│   ├── requirements.txt
│   └── Dockerfile
├── Front/                 # Angular frontend
│   ├── src/app/
│   │   ├── components/    # home, login, register, profile, tutor-details,
│   │   │                  # subject-tutors, become-tutor, verify-email, header, footer
│   │   ├── services/      # auth, api
│   │   └── interceptors/  # JWT-заголовки
│   └── Dockerfile
├── docker-compose.yml
└── .env.example
```

---

## Запуск через Docker

### 1. Клонировать репозиторий
```bash
git clone https://github.com/almasiks/outpeer.git
cd outpeer
```

### 2. Создать `.env` файл
```bash
cp .env.example .env
```
Заполнить переменные в `.env`:
```env
SECRET_KEY=your-secret-key
DEBUG=False
DB_NAME=kbtutor
DB_USER=postgres
DB_PASSWORD=postgres
ALLOWED_HOSTS=localhost,127.0.0.1
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
FRONTEND_URL=http://localhost
```

### 3. Запустить
```bash
docker-compose up --build
```

Приложение будет доступно по адресу: **http://localhost**

---

## Локальный запуск (без Docker)

### Backend
```bash
cd back
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend
```bash
cd Front
npm install
ng serve
```

Frontend: http://localhost:4200  
Backend API: http://localhost:8000/api/

---

## API эндпоинты

| Метод | URL | Описание |
|-------|-----|----------|
| POST | `/api/auth/register/` | Регистрация |
| POST | `/api/auth/login/` | Вход |
| POST | `/api/auth/logout/` | Выход |
| GET/PUT | `/api/auth/profile/` | Профиль пользователя |
| GET | `/api/auth/verify-email/` | Верификация email |
| GET | `/api/tutors/` | Список тьюторов |
| GET | `/api/tutors/<id>/` | Детали тьютора |
| GET | `/api/tutors/<id>/slots/` | Слоты тьютора |
| POST/GET | `/api/tutors/<id>/reviews/` | Отзывы тьютора |
| GET | `/api/subjects/` | Список предметов |
| POST/GET | `/api/bookings/` | Бронирования |
| GET | `/api/my-bookings/` | Мои бронирования |
