# apps/dashboard/apps.py

from django.apps import AppConfig


class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'

    def ready(self):
        # 시그널을 사용하는 경우 여기에 임포트
        pass
