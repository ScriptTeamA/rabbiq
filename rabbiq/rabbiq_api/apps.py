from django.apps import AppConfig


class RabbiqApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rabbiq_api'
    verbose_name = 'Human Resources'

    def ready(self):
        import rabbiq_api.signals 
