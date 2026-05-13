from rest_framework import serializers
from django.contrib.auth import authenticate, get_user_model

User = get_user_model()
from .models import Subject, TutorProfile, LessonSlot, Booking, Review


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    role = serializers.ChoiceField(choices=['student', 'tutor'])

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken.")
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', 'student')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role,
        )
        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid credentials.")
        if not user.is_active:
            raise serializers.ValidationError("Account disabled.")
        data['user'] = user
        return data



class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'name', 'description']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class TutorProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        queryset=Subject.objects.all(), source='subject', write_only=True, required=True
    )

    class Meta:
        model = TutorProfile
        fields = ['id', 'user', 'subject', 'subject_id', 'experience_years', 'bio', 'hourly_rate', 'rating']
        read_only_fields = ['rating']

    def validate_experience_years(self, value):
        if value < 2:
            raise serializers.ValidationError("Стать тьютором могут только студенты от 2 курса")
        return value

    def validate_bio(self, value):
        if len(value.strip()) < 50:
            raise serializers.ValidationError("Расскажите о себе подробнее — минимум 50 символов")
        return value

    def validate_hourly_rate(self, value):
        if value < 500:
            raise serializers.ValidationError("Минимальная ставка — 500 ₸/час")
        if value > 10000:
            raise serializers.ValidationError("Максимальная ставка — 10 000 ₸/час")
        return value


class LessonSlotSerializer(serializers.ModelSerializer):
    tutor_username = serializers.CharField(source='tutor.user.username', read_only=True)
    tutor_subject = serializers.CharField(source='tutor.subject.name', read_only=True, default=None)
    tutor_hourly_rate = serializers.DecimalField(source='tutor.hourly_rate', max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = LessonSlot
        fields = ['id', 'tutor', 'tutor_username', 'tutor_subject', 'tutor_hourly_rate', 'start_time', 'end_time', 'is_booked']
        read_only_fields = ['tutor', 'is_booked']

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("end_time must be after start_time.")
        return data


class BookingSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.username', read_only=True)
    tutor_name = serializers.CharField(source='tutor.user.username', read_only=True)
    tutor_subject = serializers.CharField(source='tutor.subject.name', read_only=True, default='')
    tutor_hourly_rate = serializers.DecimalField(source='tutor.hourly_rate', max_digits=8, decimal_places=2, read_only=True)

    class Meta:
        model = Booking
        fields = ['id', 'tutor', 'tutor_name', 'tutor_subject', 'tutor_hourly_rate', 'student', 'student_username', 'date', 'status']
        read_only_fields = ['student']


class ReviewSerializer(serializers.ModelSerializer):
    student_username = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'tutor', 'student', 'student_username', 'booking', 'rating', 'comment', 'created_at']
        read_only_fields = ['student', 'created_at']

    def validate_rating(self, value):
        if not 1 <= value <= 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return value

    def validate(self, data):
        request = self.context.get('request')
        tutor = data.get('tutor')
        if request and tutor and Review.objects.filter(tutor=tutor, student=request.user).exists():
            raise serializers.ValidationError("You have already reviewed this tutor.")
        return data
