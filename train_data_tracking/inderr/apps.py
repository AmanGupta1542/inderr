from django.apps import AppConfig
from django.core.cache import cache
from django.db.models.signals import post_migrate
import os
import pickle

CACHE_FILE_PATH = 'restart.pkl'

def clear_cache():
    # Clear all cache
    cache.clear()

def load_data_from_file(file_path):
    """Loads data from a file using pickle. If the file does not exist, it returns an empty dictionary."""
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist. Returning empty dictionary.")
        return {}
    
    with open(file_path, 'rb') as file:
        data = pickle.load(file)
    print(f"Data loaded from file {file_path}")
    return data

def set_global_variable():
    # Clear cache before setting new cache variables
    clear_cache()
    cache.set('stations', None)
    cache.set('first_gps_obj', None)
    cache.set('prev_gps_obj', None)
    cache.set('current_or_last_gps_obj', None)
    from .models import States  # Import your model here
    states = list(States.objects.all())
    cache.set('states', states)


class InderrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'inderr'

    def ready(self):
        # Call the function to set the global variable
        set_global_variable()
