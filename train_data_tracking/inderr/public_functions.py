import math
from decimal import Decimal

from .models import Trains, TrainInnerStation
from .coords import get_coords
import logging
from datetime import datetime, timedelta, time

logger = logging.getLogger("inderr.public_functions")


def haversine_distance(lat1, lon1, lat2, lon2):
    # Convert Decimal values to float
    lat1, lon1, lat2, lon2 = map(float, [lat1, lon1, lat2, lon2])

    R = 6371  # Radius of the Earth in kilometers
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)

    a = (
        math.sin(d_lat / 2) * math.sin(d_lat / 2) +
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
        math.sin(d_lon / 2) * math.sin(d_lon / 2)
    )
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def remaining_distance_from_stat():
    pass

def total_remaining_distance():
    pass 

def convert_seconds(seconds):
    print('getting seconds ', seconds)
    # Calculate hours, minutes, and remaining seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    
    # Construct the result string
    result = ""
    if hours > 0:
        result += f"{hours} hour{'s' if hours > 1 else ''} "
    if minutes > 0:
        result += f"{minutes} minute{'s' if minutes > 1 else ''}"
    
    return result.strip()  # Remove leading/trailing spaces

def get_next_stat_time_obj(est_time_str):
    # Get the current date
    today = datetime.today().date()

    # Parse the time string
    time_str = est_time_str
    hour, minute = map(int, time_str.split(':'))

    # Create a time object with the parsed hour and minute
    time_obj = time(hour, minute)

    # Combine the current date with the parsed time to get the datetime object
    datetime_obj = datetime.combine(today, time_obj)

    # Print the datetime object
    print(datetime_obj)
    return datetime_obj

def add_late_early_time(next_station, gps_obj):
    remaining_distance = next_station['remaining_distance']
    instent_speed = gps_obj.instant_speed # in kmph
    if instent_speed == 0:
        late_by = "Train is on time"
        minutes_difference = 0 
    else:
        time = remaining_distance/instent_speed # in hours
        print('time is, ',time)
        totaL_time_to_reach = datetime.now() + timedelta(hours=time)
        print('totaL_time_to_reach', totaL_time_to_reach)
        next_station['totaL_time_to_reach'] = totaL_time_to_reach.strftime("%m-%d-%Y %H:%M:%S")
        next_station['instant_distance'] = gps_obj.instant_distance
        next_station['instant_speed'] = gps_obj.instant_speed
        # convert next station arrived(estimate_time ) string in python datetime obj
        next_stat_time = get_next_stat_time_obj(next_station['estimate_time'])
        print('next_stat_time', next_stat_time)
        time_difference  = next_stat_time - totaL_time_to_reach # positive value means trian is early, negative value means train is late, for 0 train is on time
        print('time_difference', time_difference)
        print('time_difference', time_difference.total_seconds())
        print('time_difference min', time_difference.total_seconds()/60)
        print('time_difference min', time_difference.total_seconds()//60)
        hours = int(time_difference.total_seconds() // 3600)
        minutes = int((time_difference.total_seconds() % 3600) // 60)
        seconds = int(time_difference.total_seconds() % 60)
        # Print the result
        print(f"Total time difference: {hours} hours, {minutes} minutes, {seconds} seconds")
        # minutes_difference = time_difference.total_seconds() / 60
        time_for_late_early = convert_seconds(time_difference.total_seconds())
        
        # Check if the train is early, late, or on time
        if time_difference.total_seconds() > 0:
            print("Train is early by {}".format(abs(time_difference)))
            late_by = "Train is early by {}".format(time_for_late_early)
        elif time_difference.total_seconds() == timedelta(0):
            print("Train is on time")
            late_by = "Train is on time"
        else:
            print("Train is late by {}".format(time_difference))
            late_by = "Train is late by {}".format(time_for_late_early)
    next_station['late_by'] = late_by
    print('time to reach next station', time_for_late_early)
    print('next station lat lon: ', next_station['lat'], next_station['lon'])
    return next_station


def get_next_station(train_id):
    stop_stations = TrainInnerStation.objects.filter(train_id=train_id).order_by('order')
    gps_obj = get_coords()
    lat, lon = gps_obj.gps_coords
    next_stations = None
    total_distance = 0
    if lat != 0 and lon != 0 :
        stop_list = []
        for stations in stop_stations:
            if stations.distance: total_distance +=stations.distance
            dict = {
                    'name': stations.station_id.name,
                    'lat': str(stations.station_id.lat),
                    'lon': str(stations.station_id.lon),
                    'order': stations.order,
                    'remaining_distance': haversine_distance(lat, lon, stations.station_id.lat, stations.station_id.lon),

                    'abbr': stations.station_id.code,
                    'distance': stations.distance,
                    'total_distance': total_distance,
                    'estimate_time': stations.arrives.strftime('%H:%M') if stations.arrives is not None else None,
                    'depart_time': stations.departs.strftime('%H:%M') if stations.departs is not None else None, # change key to depart_time
                    'halt_time': stations.halt_time
                }
            stop_list.append(dict)
        from_station = stop_list[0]
        sorted_stations = stop_list
        sorted_stations.sort(key=lambda x: x['remaining_distance'])
        min_stat = sorted_stations[0]

        # From station to current location (selected place)
        FSTCL = haversine_distance(from_station['lat'], from_station['lon'], lat, lon)

        # From station to miminum station (min_stat)
        FSTMS = haversine_distance(from_station['lat'], from_station['lon'], min_stat['lat'], min_stat['lon'])
        if(FSTMS < FSTCL or FSTMS == 0):
            next_stations = [stat for stat in sorted_stations if min_stat['order']+1 == stat['order']][0]
        else :
            next_stations = min_stat
        return add_late_early_time(next_stations, gps_obj), gps_obj, stop_list
    else:
        return add_late_early_time(next_stations, gps_obj), gps_obj, stop_list