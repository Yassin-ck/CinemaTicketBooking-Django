from django.apps import AppConfig


class AuthenticationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentications'

    def ready(self) -> None:
        import authentications.modules.signals