from django.apps import AppConfig


class SimulatorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'simulator'
    verbose_name = 'Diagram Simulator'
    
    def ready(self):
        """Initialize app when Django starts"""
        pass
