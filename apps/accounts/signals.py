import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, Profile, Driver

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """
    CustomUser가 생성될 때, Profile을 생성하고 user_type이 'staff'인 경우 Driver 프로필을 생성합니다.
    """
    if created:
        Profile.objects.create(user=instance)
        logger.info(f"Profile created for user {instance.username}")

        if instance.user_type == 'staff':
            try:
                driver_id = generate_driver_id(instance)
                Driver.objects.create(profile=instance.profile, driver_id=driver_id)
                logger.info(f"Driver profile created for user {instance.username} with ID {driver_id}")
            except Exception as e:
                logger.error(f"Error creating driver profile for user {instance.username}: {e}")


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    """
    CustomUser가 저장될 때, Profile도 저장합니다.
    """
    instance.profile.save()


def generate_driver_id(user):
    """
    드라이버 ID 생성 로직
    - 유저 이름의 첫 6글자 (대문자) + 유저 ID의 마지막 2자리 (0으로 패딩)
    - 예: 'JOHNDOE' + 1 => 'JOHNDO01'

    중복 시 간단한 로직으로 ID를 변경하여 생성합니다.
    """
    username_part = user.username[:6].upper().ljust(6, 'X')  # 6자 미만일 경우 'X'로 패딩
    user_id_part = str(user.id).zfill(2)[-2:]  # 유저 ID가 2자리 이상인지 확인
    driver_id = f"{username_part}{user_id_part}"

    # 중복 확인
    if Driver.objects.filter(driver_id=driver_id).exists():
        logger.warning(f"Duplicate driver_id {driver_id} detected. Generating a unique ID.")
        driver_id = f"{username_part}{str(user.id + 100).zfill(2)[-2:]}"  # 간단한 예시로 100을 더함

    return driver_id
