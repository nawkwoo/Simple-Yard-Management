from django.apps import AppConfig
from django.db.models.signals import post_migrate

class YmsEditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.yms_edit"

    def ready(self):
        from .models import Division
        post_migrate.connect(self.create_default_divisions, sender=self)

    @staticmethod
    def create_default_divisions(sender, **kwargs):
        """기본 Division 데이터를 생성"""
        from .models import Division
        try:
            Division.create_default_divisions()
            print("기본 Division이 성공적으로 생성되었습니다.")
        except Exception as e:
            print(f"기본 Division 생성 중 오류 발생: {e}")