from django.apps import AppConfig
from django.core.cache import cache

CACHE_FILE_PATH = 'restart.pkl'

def clear_cache():
    # Clear all cache
    cache.clear()

class InderrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inderr'

    def ready(self):
        # Call the function to set the global variable
        clear_cache()
        cache.set('is_cache_setup', False)