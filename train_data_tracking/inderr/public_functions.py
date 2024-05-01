import math
from decimal import Decimal

from .models import Trains, TrainInnerStation
from .coords import get_coords
import logging
from datetime import datetime, timedelta, time
from django.core.cache import cache

logger = logging.getLogger("inderr.public_functions")


'''Now, take 1 more scenario
A train is stopped at the outer location and train is stationary, today's current time is 18:00 and station 2 scheduled arrival time is 18:10, and after 2 minutes train is still stationary and how long it will stationary it is unexpected (it can be 5 min, 10 min, 20 min or may be 2 hour), In this case how can I calculate station 2 expected arrival time
ChatGPT
In this scenario, where the train is unexpectedly stationary at an outer location with no specific duration, estimating the expected arrival time at station 2 becomes challenging. However, we can make an assumption based on typical delays or historical data.

One approach is to use an average delay time for trains stopped at outer locations. You can determine this average delay based on historical data or typical delays experienced by trains in similar situations.

Here's how you can estimate the expected arrival time at station 2:

Calculate the delay between the scheduled arrival time at station 2 and the current time.
Add the average delay time for trains stopped at outer locations to this delay.
Add this adjusted delay to the scheduled arrival time at station 2 to get the estimated arrival time.
Here's a Python function to estimate the arrival time at station 2 in this scenario:
'''
def estimateArrivalTimeAtStation2_at_outer(expectedArrivalTime, currentTime, averageDelay):
    # parameters
    # expectedArrivalTime = "18:10"
    # currentTime = "18:05"
    # averageDelay = 10  # Assume an average delay of 10 minutes for trains stopped at outer locations

    # Parse the expected arrival time and current time
    arrival = datetime.strptime(expectedArrivalTime, "%H:%M")
    current = datetime.strptime(currentTime, "%H:%M")

    # Calculate the delay between scheduled arrival and current time
    delay = current - arrival

    # Add the average delay time for trains stopped at outer locations
    adjustedDelay = delay + timedelta(minutes=averageDelay)

    # Add the adjusted delay to the expected arrival time at station 2
    estimatedArrival = arrival + adjustedDelay

    return estimatedArrival.strftime("%H:%M")


'''
Departure time of a train from station 1 is 17:55 and next station expected (station 2) arrival time is 18:32, but train is still on the station 1, and current time is 18:05, then how to estimate arrival time to station 2.
ChatGPT
To estimate the arrival time at station 2 in this scenario, you can calculate the delay between the scheduled departure time from station 1 and the current time. Then, you can add this delay to the expected arrival time at station 2 to get the estimated arrival time at station 2.

Here's how you can do it:

Calculate the delay between the scheduled departure time from station 1 and the current time.
Add this delay to the expected arrival time at station 2.
Here's a Python function to estimate the arrival time at station 2:
'''
from datetime import datetime, timedelta

def estimateArrivalTimeAtStation2_at_station(departureTime, expectedArrivalTime, currentTime):
    # parameters
    # departureTime = "17:55"
    # expectedArrivalTime = "18:32"
    # currentTime = "18:05"

    # Parse the departure time, expected arrival time, and current time
    departure = datetime.strptime(departureTime, "%H:%M")
    arrival = datetime.strptime(expectedArrivalTime, "%H:%M")
    current = datetime.strptime(currentTime, "%H:%M")

    # Calculate the delay between scheduled departure and current time
    delay = current - departure
    print(delay)

    # Add the delay to the expected arrival time at station 2
    estimatedArrival = arrival + delay
    print(estimatedArrival)

    return estimatedArrival.strftime("%H:%M")


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
    # Calculate hours and remaining seconds
    hours = int(seconds // 3600)
    remaining_seconds = seconds % 3600

    # Calculate minutes
    minutes = int(remaining_seconds // 60)

    # return hours, minutes
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
    instent_speed = 0
    if False:
        late_by = "Train is on time"
        minutes_difference = 0 
    else:
        if int(instent_speed) == 0:
            # logic to check whether train is on station or not
            at_station = remaining_distance < 1
            if at_station :
                waiting_time = int(next_station['halt_time']) # value in minutes
            else:
                waiting_time = 5 # 5 minutes
            totaL_time_to_reach = datetime.now() + timedelta(minutes=waiting_time)
        else:
            time = remaining_distance/instent_speed # in hours
            print('time is, ',time)
            totaL_time_to_reach = datetime.now() + timedelta(hours=time)
        print('totaL_time_to_reach', totaL_time_to_reach)
        next_station['totaL_time_to_reach'] = totaL_time_to_reach.strftime("%m-%d-%Y %H:%M:%S")
        next_station['totaL_time_to_reach'] = totaL_time_to_reach.isoformat()
        next_station['instant_distance'] = gps_obj.instant_distance
        next_station['instant_speed'] = gps_obj.instant_speed
        # convert next station arrived(estimate_time ) string in python datetime obj
        next_stat_time = get_next_stat_time_obj(next_station['estimate_time'])
        print('next_stat_time', next_stat_time)
        time_difference  = next_stat_time - totaL_time_to_reach # positive value means trian is early, negative value means train is late, for 0 train is on time
        print('time_difference', time_difference)
        print('time_difference', time_difference.total_seconds())
        print('time_difference min', time_difference.total_seconds()/60)
        print('time_difference min correct one', time_difference.total_seconds()//60)
        hours = int(time_difference.total_seconds() // 3600)
        minutes = int((time_difference.total_seconds() % 3600) // 60)
        seconds = int(time_difference.total_seconds() % 60)
        # Print the result
        print(f"Total time difference: {hours} hours, {minutes} minutes, {seconds} seconds")
        # minutes_difference = time_difference.total_seconds() / 60
        time_for_late_early = convert_seconds(abs(time_difference.total_seconds()))
        
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

def next_station_checking(next_station, stations):
    cache_stations = cache.get('stations')
    print("##################################################################")
    print("##################################################################")
    print("##################################################################")
    print(cache_stations)
    print(next_station)
    if cache_stations is None:
        print(stations)
        cache.set('stations', [stations[1]])
        print('return 1')
        return stations[1]
    else:
        next_station_registers = list(filter(lambda x: x.get('name') == next_station['name'], cache_stations))
        if next_station_registers:
            next_station_register = next_station_registers[0]
            # if next_station_register['is_crossed']:
                # handling logic if next station is emiting a station which is already crossed

            if next_station['remaining_distance'] <= 1:
                # update is_crossed to true and update cache stations
                if next_station_register['is_crossed']:
                    print('return 7')
                    return next_station
                next_station.update({"is_crossed": True})
                cache_stations.pop()
                cache_stations.append(next_station)
                cache.set('stations', cache_stations)
                print('return 2')
                return next_station
            else:
                print('return 3')
                return next_station
        else:
            last_leaving_station = cache_stations[-1]
            next_expected_station_order = last_leaving_station['order']+1
            if (next_station['order'] == next_expected_station_order) and (last_leaving_station['is_crossed'] == True):
                cache_stations.append(next_station)
                print('update new station in cache')
                print(cache_stations)
                cache.set('stations', cache_stations)
                print('return 4')
                return next_station
            else:
                # running else block means last leaving station is not marked as true or next station order is not correct
                if last_leaving_station['is_crossed'] == False:
                    # update remaining distance
                    next_expected_station = list(filter(lambda x: x.get('name') == last_leaving_station['name'], stations))[0]
                    print("##################################################################")
                    print("breakdown occur")
                    print(next_expected_station)
                    cache_stations.pop()
                    cache_stations.append(next_expected_station)
                    cache.set('stations', cache_stations)
                    print('return 5')
                    # return next_expected_station
                    if next_expected_station['remaining_distance'] <= 1:
                        # update is_crossed to true and update cache stations
                        if next_expected_station['is_crossed']:
                            print('return new 1')
                            return next_expected_station
                        next_expected_station.update({"is_crossed": True})
                        cache_stations.pop()
                        cache_stations.append(next_expected_station)
                        cache.set('stations', cache_stations)
                        print('return new 2')
                        return next_expected_station
                    else:
                        print('return new 3')
                        return next_expected_station
                if next_station['order'] != next_expected_station_order:
                    print("##################################################################")
                    print("breakdown occur 2")
                    next_expected_station = list(filter(lambda x: x.get('order') == next_expected_station_order, stations))[0]
                    print(next_expected_station)
                    print('return 6')
                    return next_expected_station


def get_next_station(train_id):
    stop_stations = TrainInnerStation.objects.filter(train_id=train_id).order_by('order')
    gps_obj = get_coords()
    lat, lon = gps_obj.gps_coords
    print('gps coords', gps_obj.gps_coords)
    next_stations = None
    total_distance = 0
    cache_stations = cache.get('stations')
    if lat != 0 and lon != 0 :
        stop_list = []
        stop_list1 = []
        for stations in stop_stations:
            if stations.distance: 
                total_distance +=stations.distance
            dict = {
                    'name': stations.station_id.name,
                    'lat': str(stations.station_id.lat),
                    'lon': str(stations.station_id.lon),
                    'order': stations.order,
                    'remaining_distance': haversine_distance(lat, lon, stations.station_id.lat, stations.station_id.lon),
                    'is_crossed': False,
                    'abbr': stations.station_id.code,
                    'distance': stations.distance,
                    'total_distance': total_distance,
                    'estimate_time': stations.arrives.strftime('%H:%M') if stations.arrives is not None else None,
                    'depart_time': stations.departs.strftime('%H:%M') if stations.departs is not None else None, # change key to depart_time
                    'halt_time': stations.halt_time
                }
            stop_list.append(dict)
            stop_list1.append(dict)
        from_station = stop_list[0]
        sorted_stations = stop_list
        sorted_stations.sort(key=lambda x: x['remaining_distance'])
        min_stat = sorted_stations[0]
        print(min_stat)
        # From station to current location (selected place)
        FSTCL = haversine_distance(from_station['lat'], from_station['lon'], lat, lon)
        # From station to miminum station (min_stat)
        FSTMS = haversine_distance(from_station['lat'], from_station['lon'], min_stat['lat'], min_stat['lon'])
        if(FSTMS < FSTCL or FSTMS == 0):
            next_stations = [stat for stat in sorted_stations if min_stat['order']+1 == stat['order']][0]
        else :
            next_stations = min_stat
        next_station = next_station_checking(next_stations, stop_list1)
        print("*********** Actual next station ************************")
        print(next_station)
        return add_late_early_time(next_station, gps_obj), gps_obj, stop_list1
    else:
        cache_stations = cache.get('stations')
        if cache_stations is None:
            # next_station = stop_stations[1]
            stop_list = []
            for stations in stop_stations:
                if stations.distance: total_distance +=stations.distance
                dict = {
                        'name': stations.station_id.name,
                        'lat': str(stations.station_id.lat),
                        'lon': str(stations.station_id.lon),
                        'order': stations.order,
                        'remaining_distance': stations.distance,
                        'is_crossed': False,
                        'abbr': stations.station_id.code,
                        'distance': stations.distance,
                        'total_distance': total_distance,
                        'estimate_time': stations.arrives.strftime('%H:%M') if stations.arrives is not None else None,
                        'depart_time': stations.departs.strftime('%H:%M') if stations.departs is not None else None, # change key to depart_time
                        'halt_time': stations.halt_time
                    }
                print(dict)
                stop_list.append(dict)
            next_station = stop_list[1]
        else:
            next_station = cache_stations[-1]
        return add_late_early_time(next_station, gps_obj), gps_obj, stop_stations