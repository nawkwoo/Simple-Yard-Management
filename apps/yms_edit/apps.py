from django.apps import AppConfig
from django.db.models.signals import post_migrate

class YmsEditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.yms_edit"

    def ready(self):
        from django.db import connection
        from .models import Division
        
        # post_migrate 시그널 연결
        post_migrate.connect(self.create_default_divisions, sender=self)

    @staticmethod
    def create_default_divisions(sender, **kwargs):
        from .models import Division
        
        if 'default' in sender.apps.get_app_configs():
            try:
                Division.create_default_divisions()
                print("기본 Division이 성공적으로 생성되었습니다.")
            except Exception as e:
                print(f"기본 Division 생성 중 오류 발생: {e}")