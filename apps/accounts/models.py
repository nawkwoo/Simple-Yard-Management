from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', '관리자'),
        ('staff', '직원'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    gender = models.CharField(max_length=10, choices=[('M', '남성'), ('F', '여성')])
    birth_date = models.DateField(null=True, blank=True)
    has_car = models.BooleanField(default=False)

    def is_admin(self):
        return self.user_type == 'admin'

    def is_staff(self):
        return self.user_type == 'staff'