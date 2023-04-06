from django.apps import AppConfig


class NseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'nse_app'

    # def ready(self):
    #     print('Staring Scheduler ...')
    #     from .Scheduler import updater
    #     updater.start()