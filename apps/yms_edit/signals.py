# apps/yms_edit/signals.py

from django.db.models.signals import post_migrate
from django.dispatch import receiver
from .models import Division
import logging

from django.db.models.signals import post_delete
from .models import YardInventory, Truck, Chassis, Container, Trailer

logger = logging.getLogger(__name__)


@receiver(post_migrate)
def create_default_divisions(sender, **kwargs):
    """
    마이그레이션 후 기본 Division 데이터를 생성합니다.
    """
    if sender.name != 'apps.yms_edit':
        return  # 해당 앱에 대해서만 실행

    try:
        Division.create_default_divisions()
        logger.info("기본 Division이 성공적으로 생성되었습니다.")
    except Exception as e:
        logger.error(f"기본 Division 생성 중 오류 발생: {e}")

@receiver(post_delete, sender=Truck)
@receiver(post_delete, sender=Chassis)
@receiver(post_delete, sender=Container)
@receiver(post_delete, sender=Trailer)
def delete_yard_inventory(sender, instance, **kwargs):
    """
    장비가 삭제될 때 해당 장비와 관련된 YardInventory를 삭제합니다.
    """
    YardInventory.objects.filter(equipment_id=instance.id).delete()