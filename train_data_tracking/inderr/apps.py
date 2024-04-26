from django.apps import AppConfig
from django.core.cache import cache

def clear_cache():
    # Clear all cache
    cache.clear()

def set_global_variable():
    # Clear cache before setting new cache variables
    clear_cache()
    
    cache.set('first_gps_obj', None)
    cache.set('prev_gps_obj', None)
    cache.set('current_or_last_gps_obj', None)


class InderrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inderr'

    def ready(self):
        # Call the function to set the global variable
        set_global_variable()
