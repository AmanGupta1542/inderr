from django.core.cache import cache
import os
import pickle

from .models import States, TrackingData

def cache_init():
    is_cache_setup = cache.get('is_cache_setup')
    if not is_cache_setup:
        tracking_data = list(TrackingData.objects.all())
        if len(tracking_data) > 0:
            crossed_stations = [station for station in tracking_data if station.is_crossed]
            if tracking_data[-1].is_crossed == False:
                crossed_stations.append(tracking_data[-1])

            # convert crossed_stations (list of TrackingData) object into list of dict
            stations_list = []
            for station in crossed_stations:
                stations_is = {
                    'name': station.name,
                    'lat': station.lat,
                    'lon': station.lon,
                    'curr_lat': station.curr_lat,
                    'curr_lon': station.curr_lon,
                    'order': station.order,
                    'other_lang': 'hi',
                    'remaining_distance': station.remaining_distance,
                    'is_crossed': station.is_crossed,
                    'actual_arrival_time': station.actual_arrival_time,
                    'actual_departure_time': station.actual_departure_time,
                    'abbr': station.abbr,
                    'distance': station.distance,
                    'total_distance': station.total_distance,
                    'estimate_time': station.estimate_time,
                    'depart_time': station.depart_time,
                    'halt_time': station.halt_time,
                }
                stations_list.append(stations_is)
            cache.set('stations', stations_list)
        else:
            cache.set('stations', None)
        print('cache stations')
        print(cache.get('stations'))
        cache.set('first_gps_obj', None)
        cache.set('prev_gps_obj', None)
        cache.set('current_or_last_gps_obj', None)
        
        states = list(States.objects.all())
        cache.set('states', states)

        # after initializing cache, setup is_cache_setup flag to true
        cache.set('is_cache_setup', True)


def get_cache_variable(var_name):
    value = cache.get(var_name)
    if value:
        return value
    else:
        return None