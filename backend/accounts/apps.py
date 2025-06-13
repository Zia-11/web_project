from django.apps import AppConfig

# этот класс указывается в INSTALLED_APPS чтобы Django знал о приложении
class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
