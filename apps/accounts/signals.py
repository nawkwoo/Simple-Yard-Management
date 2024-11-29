# apps/accounts/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Driver
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=CustomUser)
def create_driver_profile(sender, instance, created, **kwargs):
    if created and instance.user_type == 'staff':
        try:
            Driver.objects.create(user=instance, driver_id=generate_driver_id(instance))
            logger.info(f"Driver profile created for user {instance.username}")
        except Exception as e:
            logger.error(f"Error creating driver profile for user {instance.username}: {e}")

def generate_driver_id(user):
    # 드라이버 ID 생성 로직 구현
    # 예시: 유저 이름의 첫 6글자와 ID의 마지막 2자리
    return f"{user.username[:6].upper()}{str(user.id).zfill(2)}"
