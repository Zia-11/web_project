from django.apps import AppConfig

# класс конфигурации для приложения 'core'
class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'
    
     # метод вызывается при инициализации приложения
    def ready(self):
        import core.signals