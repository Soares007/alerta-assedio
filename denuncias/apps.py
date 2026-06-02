from django.apps import AppConfig


class DenunciasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'denuncias'
    
    def ready(self):
        import denuncias.signals
