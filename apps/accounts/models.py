# apps/accounts/models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일 주소를 입력해야 합니다.")
        email = self.normalize_email(email)
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError("슈퍼유저는 is_staff=True 이어야 합니다.")
        if not extra_fields.get('is_superuser'):
            raise ValueError("슈퍼유저는 is_superuser=True 이어야 합니다.")

        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', '관리자'),
        ('staff', '직원'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    gender = models.CharField(max_length=10, choices=[('M', '남성'), ('F', '여성')])
    birth_date = models.DateField(null=True, blank=True)
    has_car = models.BooleanField(default=False)

    objects = CustomUserManager()

    def is_admin(self):
        return self.user_type == 'admin'

    def is_staff_member(self):
        return self.user_type == 'staff'

class Driver(models.Model):
    """드라이버 모델"""
    user = models.OneToOneField(
        CustomUser,  # 직접 참조
        on_delete=models.CASCADE,
        related_name='accounts_driver_profile',  # 고유한 related_name
        limit_choices_to={"user_type": "staff"},  # 직원만 선택 가능
    )
    driver_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[RegexValidator(
            regex=r"^[A-Z]{6}\d{2}$",
            message="Driver ID must be 6 letters followed by 2 digits."
        )]
    )

    @property
    def has_personal_vehicle(self):
        return self.user.has_car

    def __str__(self):
        return f"{self.driver_id} - {self.user.username}"
