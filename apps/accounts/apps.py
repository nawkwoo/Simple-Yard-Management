# apps/accounts/apps.py

from django.apps import AppConfig

class AccountsConfig(AppConfig):
    name = 'apps.accounts'

    def ready(self):
        import apps.accounts.signals  # 시그널 임포트
