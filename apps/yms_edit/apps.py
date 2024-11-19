from django.apps import AppConfig


class YmsEditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.yms_edit"
    
    def ready(self):
        from .models import Division
        Division.create_default_divisions()