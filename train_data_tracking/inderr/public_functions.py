import math
from decimal import Decimal

from .models import Trains, TrainInnerStation
from .coords import get_coords

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

# Example usage:
# lat1, lon1 = Decimal('37.7749'), Decimal('-122.4194')
# lat2, lon2 = Decimal('37.7749'), Decimal('-122.4193')

# result_distance = haversine_distance(lat1, lon1, lat2, lon2)
# print(f'Distance: {result_distance:.2f} kilometers')

def get_next_station(train_id):
    stop_stations = TrainInnerStation.objects.filter(train_id=train_id).order_by('order')
    curr_location = get_coords()
    next_stations = None
    if curr_location['lat'] != 0 and curr_location['lon'] != 0 :
        stop_list = []
        for stations in stop_stations:
            # print(stations.station_id.name)
            dict = {
                    'name': stations.station_id.name,
                    'lat': stations.station_id.lat,
                    'lon':stations.station_id.lon,
                    'order': stations.order,
                    'distance': haversine_distance(curr_location['lat'], curr_location['lon'], stations.station_id.lat, stations.station_id.lon)
                }
            stop_list.append(dict)
        from_station = stop_list[0]
        sorted_stations = stop_list
        sorted_stations.sort(key=lambda x: x['distance'])
        min_stat = sorted_stations[0]

        # From station to current location (selected place)
        FSTCL = haversine_distance(from_station['lat'], from_station['lon'], curr_location['lat'], curr_location['lon'])

        # From station to miminum station (min_stat)
        FSTMS = haversine_distance(from_station['lat'], from_station['lon'], min_stat['lat'], min_stat['lon'])
        if(FSTMS < FSTCL or FSTMS == 0):
            next_stations = [stat for stat in sorted_stations if min_stat['order']+1 == stat['order']][0]
        else :
            next_stations = min_stat
        return next_stations
    else:
        return next_stations