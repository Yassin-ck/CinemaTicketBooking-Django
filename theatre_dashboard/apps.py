from django.apps import AppConfig


class TheatreDashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "theatre_dashboard"

    def ready(self) -> None:
        import theatre_dashboard.signals
