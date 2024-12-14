# apps/dashboard/apps.py

from django.apps import AppConfig
from apps.dashboard.tasks import OrderTableMonitor  # OrderTableMonitor 임포트

class DashboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dashboard'

    def ready(self):
        """
        Django 앱이 시작될 때 OrderTableMonitor 스레드를 실행합니다.
        """
        import threading

        def start_order_monitor():
            from apps.dashboard.tasks import OrderTableMonitor  # 여기에서 임포트
            monitor = OrderTableMonitor(interval=5)
            monitor.start()

        # 별도 스레드에서 실행
        threading.Thread(target=start_order_monitor, daemon=True).start()
            