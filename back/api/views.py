from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import EmailVerificationToken

from .models import Subject, TutorProfile, LessonSlot, Booking, Review
from .serializers import (
    RegisterSerializer, LoginSerializer,
    SubjectSerializer, TutorProfileSerializer,
    LessonSlotSerializer, BookingSerializer, ReviewSerializer,
)

User = get_user_model()




@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(_request):
    return Response({
        'auth': {
            'register': '/api/auth/register/',
            'login': '/api/auth/login/',
            'logout': '/api/auth/logout/',
            'profile': '/api/auth/profile/',
        },
        'tutors': '/api/tutors/',
        'tutor_profile': '/api/tutors/profile/',
        'slots': '/api/slots/',
        'bookings': '/api/bookings/',
        'subjects': '/api/subjects/',
        'admin_users': '/api/admin/users/',
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()

    # Send verification email (fail_silently so registration still succeeds if SMTP is not configured)
    token_obj = EmailVerificationToken.objects.create(user=user)
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token_obj.token}"
    html_message = render_to_string('email/verify_email.html', {'user': user, 'verify_url': verify_url})
    send_mail(
        subject='Подтвердите email — KBTutor',
        message=f'Перейдите по ссылке для подтверждения email: {verify_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=html_message,
        fail_silently=True,
    )

    refresh = RefreshToken.for_user(user)
    return Response(
        {
            'message': 'User registered successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_email_verified': user.is_email_verified,
            }
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def verify_email(request):
    token_str = request.query_params.get('token')
    if not token_str:
        return Response({'detail': 'Token is required.'}, status=status.HTTP_400_BAD_REQUEST)
    try:
        token_obj = EmailVerificationToken.objects.select_related('user').get(token=token_str)
    except (EmailVerificationToken.DoesNotExist, ValueError):
        return Response({'detail': 'Invalid token.'}, status=status.HTTP_400_BAD_REQUEST)
    if not token_obj.is_valid():
        token_obj.delete()
        return Response({'detail': 'Token expired. Please register again.'}, status=status.HTTP_400_BAD_REQUEST)
    user = token_obj.user
    user.is_email_verified = True
    user.save(update_fields=['is_email_verified'])
    token_obj.delete()
    return Response({'detail': 'Email confirmed successfully.'})


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data['username']
    password = serializer.validated_data['password']

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
            }
        },
        status=status.HTTP_200_OK
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    return Response({'detail': 'Logged out.'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_bookings(request):
    bookings = Booking.objects.filter(student=request.user).select_related('tutor', 'tutor__user', 'tutor__subject')
    return Response(BookingSerializer(bookings, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def tutor_list(request):
    qs = TutorProfile.active.select_related('user', 'subject').all()
    subject_id = request.query_params.get('subject')
    if subject_id:
        qs = qs.filter(subject_id=subject_id)
    return Response(TutorProfileSerializer(qs, many=True).data)


@api_view(['GET'])
@permission_classes([AllowAny])
def tutor_detail(_request, tutor_pk):
    tutor = get_object_or_404(TutorProfile, pk=tutor_pk)
    return Response(TutorProfileSerializer(tutor).data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role,
    }, status=status.HTTP_200_OK
)

class TutorProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            profile = get_object_or_404(TutorProfile, pk=pk)
        else:
            if getattr(request.user, 'is_tutor', False):
                profile, _ = TutorProfile.objects.get_or_create(user=request.user)
            else:
                profile = get_object_or_404(TutorProfile, user=request.user)
        return Response(TutorProfileSerializer(profile).data)

    def post(self, request):
        profile, created = TutorProfile.objects.get_or_create(user=request.user)
        serializer = TutorProfileSerializer(profile, data=request.data, partial=not created)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
        return Response(serializer.data, status=status_code)

    def put(self, request):
        profile = get_object_or_404(TutorProfile, user=request.user)
        serializer = TutorProfileSerializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        profile = get_object_or_404(TutorProfile, user=request.user)
        serializer = TutorProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        profile = get_object_or_404(TutorProfile, user=request.user)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([AllowAny])
def tutor_slots(_request, tutor_pk):
    profile = get_object_or_404(TutorProfile, pk=tutor_pk)
    slots = profile.slots.filter(is_booked=False)
    return Response(LessonSlotSerializer(slots, many=True).data)


class LessonSlotView(APIView):
    permission_classes = [IsAuthenticated]

    def _get_tutor_profile(self, user):
        return get_object_or_404(TutorProfile, user=user)

    def get(self, request, pk=None):
        if pk:
            slot = get_object_or_404(LessonSlot, pk=pk)
            return Response(LessonSlotSerializer(slot).data)
        profile = self._get_tutor_profile(request.user)
        return Response(LessonSlotSerializer(profile.slots.all(), many=True).data)

    def post(self, request):
        profile = self._get_tutor_profile(request.user)
        serializer = LessonSlotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(tutor=profile)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        profile = self._get_tutor_profile(request.user)
        slot = get_object_or_404(LessonSlot, pk=pk, tutor=profile)
        serializer = LessonSlotSerializer(slot, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        profile = self._get_tutor_profile(request.user)
        slot = get_object_or_404(LessonSlot, pk=pk, tutor=profile)
        serializer = LessonSlotSerializer(slot, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        profile = self._get_tutor_profile(request.user)
        slot = get_object_or_404(LessonSlot, pk=pk, tutor=profile)
        slot.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


def _send_booking_confirmation(booking):
    student = booking.student
    if not student.email:
        return
    tutor_profile = booking.tutor
    tutor_name = tutor_profile.user.username
    subject_name = tutor_profile.subject.name if tutor_profile.subject else 'Не указан'
    session_date = booking.date.strftime('%d.%m.%Y %H:%M') if booking.date else '—'

    html_message = render_to_string('email/booking_confirmation.html', {
        'student_name': student.username,
        'tutor_name': tutor_name,
        'subject': subject_name,
        'session_date': session_date,
    })
    send_mail(
        subject='Бронирование подтверждено — KBTutor',
        message=(
            f'Привет, {student.username}!\n'
            f'Ты успешно забронировал сессию с тьютором {tutor_name}.\n'
            f'Предмет: {subject_name}\n'
            f'Дата: {session_date}\n'
            f'Удачи в учёбе!\n— Команда KBTutor'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[student.email],
        html_message=html_message,
        fail_silently=True,
    )


class BookingView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk=None):
        if pk:
            booking = get_object_or_404(Booking, pk=pk, student=request.user)
            return Response(BookingSerializer(booking).data)
        bookings = Booking.objects.filter(student=request.user).select_related('tutor', 'tutor__user', 'tutor__subject')
        return Response(BookingSerializer(bookings, many=True).data)

    def post(self, request):
        serializer = BookingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.save(student=request.user)
        _send_booking_confirmation(booking)
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    def patch(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, student=request.user)
        new_status = request.data.get('status')
        if new_status not in ['pending', 'confirmed', 'cancelled']:
            return Response({'detail': 'Invalid status.'}, status=status.HTTP_400_BAD_REQUEST)
        booking.status = new_status
        booking.save(update_fields=['status'])
        return Response(BookingSerializer(booking).data)

    def delete(self, request, pk):
        booking = get_object_or_404(Booking, pk=pk, student=request.user)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def tutor_rate(request, tutor_pk):
    tutor = get_object_or_404(TutorProfile, pk=tutor_pk)
    score = request.data.get('score')
    try:
        score = int(score)
    except (TypeError, ValueError):
        return Response({'detail': 'Score must be an integer from 1 to 5.'}, status=status.HTTP_400_BAD_REQUEST)

    if score < 1 or score > 5:
        return Response({'detail': 'Score must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

    current_rating = float(tutor.rating or 0)
    current_count = Booking.objects.filter(tutor=tutor, status='confirmed').count()
    new_rating = ((current_rating * current_count) + score) / (current_count + 1)
    tutor.rating = round(new_rating, 2)
    tutor.save(update_fields=['rating'])

    return Response({'rating': tutor.rating}, status=status.HTTP_200_OK)


class SubjectView(APIView):
    permission_classes = [AllowAny]

    def _require_admin(self, request):
        if not request.user.is_authenticated or not request.user.is_staff:
            return Response({'detail': 'Admin only.'}, status=status.HTTP_403_FORBIDDEN)

    def get(self, _request, pk=None):
        if pk:
            return Response(SubjectSerializer(get_object_or_404(Subject, pk=pk)).data)
        return Response(SubjectSerializer(Subject.objects.all(), many=True).data)

    def post(self, request):
        err = self._require_admin(request)
        if err:
            return err
        serializer = SubjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        err = self._require_admin(request)
        if err:
            return err
        subject = get_object_or_404(Subject, pk=pk)
        serializer = SubjectSerializer(subject, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request, pk):
        err = self._require_admin(request)
        if err:
            return err
        subject = get_object_or_404(Subject, pk=pk)
        serializer = SubjectSerializer(subject, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        err = self._require_admin(request)
        if err:
            return err
        get_object_or_404(Subject, pk=pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAdminView(APIView):
    permission_classes = [IsAuthenticated]

    def _require_admin(self, request):
        if not request.user.is_staff:
            return Response({'detail': 'Admin only.'}, status=status.HTTP_403_FORBIDDEN)

    def get(self, request):
        err = self._require_admin(request)
        if err:
            return err
        users = User.objects.all().order_by('id')
        data = [
            {
                'id': u.id,
                'username': u.username,
                'email': u.email,
                'role': u.role,
                'is_staff': u.is_staff,
                'is_active': u.is_active,
            }
            for u in users
        ]
        return Response(data)

    def patch(self, request, pk):
        err = self._require_admin(request)
        if err:
            return err
        user = get_object_or_404(User, pk=pk)
        if 'role' in request.data and request.data['role'] in ['student', 'tutor', 'admin']:
            user.role = request.data['role']
            user.save(update_fields=['role'])
        return Response({
            'id': user.id,
            'username': user.username,
            'role': user.role,
            'is_staff': user.is_staff,
        })


class ReviewView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, tutor_pk):
        tutor = get_object_or_404(TutorProfile, pk=tutor_pk)
        reviews = tutor.reviews.select_related('student').all()
        return Response(ReviewSerializer(reviews, many=True).data)

    def post(self, request, tutor_pk):
        tutor = get_object_or_404(TutorProfile, pk=tutor_pk)
        if tutor.user == request.user:
            return Response({'detail': 'Cannot review yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        data = request.data.copy()
        data['tutor'] = tutor.pk
        serializer = ReviewSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        review = serializer.save(student=request.user)

        # Recalculate tutor rating from all reviews
        all_ratings = list(tutor.reviews.values_list('rating', flat=True))
        tutor.rating = round(sum(all_ratings) / len(all_ratings), 2)
        tutor.save(update_fields=['rating'])

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def review_delete(request, pk):
    review = get_object_or_404(Review, pk=pk, student=request.user)
    tutor = review.tutor
    review.delete()
    remaining = list(tutor.reviews.values_list('rating', flat=True))
    tutor.rating = round(sum(remaining) / len(remaining), 2) if remaining else 0
    tutor.save(update_fields=['rating'])
    return Response(status=status.HTTP_204_NO_CONTENT)