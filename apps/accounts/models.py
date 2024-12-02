# apps/accounts/models.py

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator
from django.db import models


class CustomUserManager(BaseUserManager):
    """
    사용자 관리자를 정의합니다. 일반 사용자 및 슈퍼유저 생성을 담당합니다.
    """
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
        """
        슈퍼유저 생성을 위한 메서드.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('user_type', 'admin')  # 슈퍼유저는 관리자 유형으로 설정

        if extra_fields.get('is_staff') is not True:
            raise ValueError("슈퍼유저는 is_staff=True 이어야 합니다.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("슈퍼유저는 is_superuser=True 이어야 합니다.")
        if extra_fields.get('user_type') != 'admin':
            raise ValueError("슈퍼유저는 user_type='admin' 이어야 합니다.")

        return self.create_user(username, email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    확장된 사용자 모델로, 추가적인 사용자 정보를 포함합니다.
    """
    USER_TYPE_CHOICES = (
        ('admin', '관리자'),
        ('staff', '직원'),
    )

    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)

    objects = CustomUserManager()

    def is_admin(self):
        """사용자가 관리자 유형인지 확인합니다."""
        return self.user_type == 'admin'

    def is_staff_member(self):
        """사용자가 직원 유형인지 확인합니다."""
        return self.user_type == 'staff'


class Profile(models.Model):
    """
    사용자 프로필 모델.
    """
    GENDER_CHOICES = [
        ('M', '남성'),
        ('F', '여성'),
        ('O', '기타'),
    ]

    user = models.OneToOneField('accounts.CustomUser', on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    birth_date = models.DateField(null=True, blank=True)
    has_car = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username}'s Profile"


class Driver(models.Model):
    """
    드라이버 프로필 모델로, Profile과 일대일 관계를 가집니다.
    """
    profile = models.OneToOneField(
        Profile,
        on_delete=models.CASCADE,
        related_name='driver_profile',
        limit_choices_to={"user__user_type": "staff"},
    )
    driver_id = models.CharField(
        max_length=8,
        unique=True,
        validators=[
            RegexValidator(
                regex=r"^[A-Z]{6}\d{2}$",
                message="Driver ID는 6개의 대문자와 2개의 숫자로 구성되어야 합니다."
            )
        ]
    )

    @property
    def has_personal_vehicle(self):
        """드라이버가 개인 차량을 보유하고 있는지 여부를 반환합니다."""
        return self.profile.has_car

    def __str__(self):
        return f"{self.driver_id} - {self.profile.user.username}"
