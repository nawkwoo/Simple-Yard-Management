# apps/yms_edit/apps.py

from django.apps import AppConfig
from django.db.models.signals import post_migrate


class YmsEditConfig(AppConfig):
    """
    yms_edit 앱의 설정 클래스.
    """
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.yms_edit"

    def ready(self):
        """
        앱이 로드될 때 기본 Division 데이터를 생성하는 시그널을 연결합니다.
        """
        from .signals import create_default_divisions
        post_migrate.connect(create_default_divisions, sender=self)
