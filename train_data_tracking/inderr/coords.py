
import serial
import pynmea2
import logging
logger = logging.getLogger("inderr.coords")
from datetime import datetime, timedelta
from django.core.cache import cache
import math
import random

from .models import Temp
from .serial_connection import serial_gps_conn

# Get the global variable
def get_global_variable(var_name):
    value = cache.get(var_name)
    if value:
        return value
    else:
        return None

# Update the global variable
def update_global_variable(var_name, value):
    cache.set(var_name, value)

class GPSPoint:
    def __init__(self, latitude, longitude, timestamp):
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp

# for testing purpose
class GPSData2:
    def __init__(self, gps_coords, first_gps_obj=None, prev_gps_obj=None):
        self.gps_coords = (gps_coords['lat'], gps_coords['lon'])
        self.timestamp = datetime.now()
        self.instant_speed = random.randint(30, 50)
        self.avg_speed = 0
        self.instant_distance = 0
        self.total_distance = 0
        self.gps_data_line = None
        self.first_gps_obj = first_gps_obj
        self.prev_gps_obj = prev_gps_obj
        # self.gps_data_line = serial_gps_conn.readline().decode('utf-8', errors='ignore')
        self.main()

    def haversine_distance(self, source, target):
        lat1, lon1 = source
        lat2, lon2 = target
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
        print('dis ', distance)
        return distance

    def main(self):
        if self.first_gps_obj is not None:
            self.get_total_distance()
            # to initialize average speed
            self.get_avg_speed()
        if self.prev_gps_obj is not None:
            # to initializer instant and total distance 
            self.calc_instant_distance()

    def calc_instant_distance(self):
        if self.prev_gps_obj is not None:
            instant_distance = self.haversine_distance(self.prev_gps_obj.gps_coords, self.gps_coords)
            self.instant_distance = round(instant_distance, 2)
        else:
            self.instant_distance = 0

    def get_avg_speed(self):
        total_time = self.timestamp - self.first_gps_obj.timestamp 
        total_distance = self.total_distance
        print('first_obj gps coords ', self.first_gps_obj.gps_coords)
        print('total distance ', self.total_distance)
        self.avg_speed = round(total_distance / (total_time.total_seconds()/3600), 2)
        print('avg speed ', self.avg_speed)
        print('instant speed ', self.instant_speed)
        print('time to reach', datetime.now() + timedelta(hours=total_distance / self.instant_speed))


    def get_total_distance(self):
        self.total_distance = self.haversine_distance(self.first_gps_obj.gps_coords, self.gps_coords)



class GPSData:
    def __init__(self, gps_conn, first_gps_obj=None, prev_gps_obj=None):
        self.gps_coords = None
        self.timestamp = None
        self.instant_speed = 0
        self.avg_speed = 0
        self.instant_distance = 0
        self.total_distance = 0
        self.gps_data_line = None
        self.first_gps_obj = first_gps_obj
        self.prev_gps_obj = prev_gps_obj
        # self.gps_data_line = serial_gps_conn.readline().decode('utf-8', errors='ignore')

        self.parse_gps_data(gps_conn)

    def haversine_distance(self, source, target):
        lat1, lon1 = source
        lat2, lon2 = target
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

    def parse_gps_data(self, gps_conn):
        try:
            self.gps_data_line = serial_gps_conn.readline().decode('utf-8', errors='ignore')
            # to initialize current coordinates and current timestamp
            self.setup_coords()
            # to initialize current speed
            self.get_instant_speed()
            if self.first_gps_obj is not None:
                self.get_total_distance()
                # to initialize average speed
                self.get_avg_speed()
            if self.prev_gps_obj is not None:
                # to initializer instant and total distance 
                self.calc_instant_distance()
        except Exception as e:
            print('line exception : ', e)

    def transform_coord(self, lat, lon):
        ''' To convert (2318.9678, 7721.4645) format coordinate into (23.189678, 77.214645) format coodinate because haversine function 
        take coordinate in (23.189678, 77.214645) format '''
        # Split the coordinates into degrees and decimal minutes
        lat_degrees = int(lat) // 100  # Extract degrees for latitude
        lat_minutes = (lat % 100) / 60  # Extract decimal minutes for latitude and convert to degrees

        lon_degrees = int(lon) // 100  # Extract degrees for longitude
        lon_minutes = (lon % 100) / 60  # Extract decimal minutes for longitude and convert to degrees

        latitude = lat_degrees + lat_minutes
        longitude = lon_degrees + lon_minutes

        return (latitude, longitude)

    def setup_coords(self):
        try:
            msg = pynmea2.parse(self.gps_data_line)
            lat = msg.latitude
            lon = msg.longitude
            if lat and lon:
                transform_lat_lon = self.transform_coord(float(lat), float(lon))
                self.gps_coords = transform_lat_lon
                self.timestamp = datetime.now()
        except pynmea2.ParseError as e:
            print("Parse error: {0}".format(e))
        except Exception as e:
            print("Unknown Exception: {}".format(e))

    def knots_to_kmph(self, speed_knots):
        # Conversion factor from knots to km/h
        conversion_factor = 1.852
        # Convert speed from knots to km/h
        speed_kmph = speed_knots * conversion_factor
        return speed_kmph

    def get_instant_speed(self):
        data_fields = self.line.split(',')
        # Check if the data line is valid and contains enough fields
        if len(data_fields) >= 8:
            # Extract the speed over ground (SOG) in knots
            speed_knots_str = data_fields[7]
            try:
                # Convert speed from string to float
                speed_knots = float(speed_knots_str)
                # Convert speed from knots to km/h
                speed_kmph = self.knots_to_kmph(speed_knots)
                # return speed_kmph
                print("Speed is : {:.2f}".format(speed_kmph))
                self.instant_speed = round(speed_kmph, 2)
            except ValueError:
                # return None
                print("Value Error")
            except Exception as e:
                print("Unknown Exception: {}".format(e))
        else:
            # return None
            print("Getting None")

    def calc_instant_distance(self):
        if self.prev_gps_obj is not None:
            instant_distance = self.haversine_distance(self.prev_gps_obj.gps_coords, self.gps_coords)
            self.instant_distance = round(instant_distance, 2)
        else:
            self.instant_distance = 0

    def get_avg_speed(self):
        total_time = self.timestamp - self.first_gps_obj.timestamp 
        print('first_obj gps coords ', self.first_gps_obj.gps_coords)
        print('total distance ', self.total_distance)
        total_distance = self.total_distance
        self.avg_speed = round(total_distance / (total_time.total_seconds()/3600), 2)

    def get_total_distance(self):
        self.total_distance = self.haversine_distance(self.first_gps_obj.gps_coords, self.gps_coords)



def temp():
    first_gps_obj = get_global_variable('first_gps_obj')
    prev_gps_obj = get_global_variable('prev_gps_obj')
    current_or_last_gps_obj = get_global_variable('current_or_last_gps_obj')
    gps_obj = GPSData(serial_gps_conn, first_gps_obj, prev_gps_obj)
    if gps_obj.gps_coords is None:
        # useless object
        return None
    else:
        # useful object
        if first_gps_obj is None:
            # update first_gps_obj
            update_global_variable('first_gps_obj', gps_obj)
            update_global_variable('prev_gps_obj', gps_obj)
            update_global_variable('current_or_last_gps_obj', gps_obj)
        else:
            # update current_or_last_gps_obj
            update_global_variable('current_or_last_gps_obj', gps_obj)
            update_global_variable('prev_gps_obj', current_or_last_gps_obj)
        return gps_obj
    
# for testing purpose
def temp2(gps_coords):
    first_gps_obj = get_global_variable('first_gps_obj')
    prev_gps_obj = get_global_variable('prev_gps_obj')
    current_or_last_gps_obj = get_global_variable('current_or_last_gps_obj')
    gps_obj = GPSData2(gps_coords, first_gps_obj, prev_gps_obj)
    if gps_obj.gps_coords is None:
        # useless object
        return None
    else:
        # useful object
        if first_gps_obj is None:
            # update first_gps_obj
            update_global_variable('first_gps_obj', gps_obj)
            update_global_variable('prev_gps_obj', gps_obj)
            update_global_variable('current_or_last_gps_obj', gps_obj)
        else:
            # update current_or_last_gps_obj
            update_global_variable('current_or_last_gps_obj', gps_obj)
            update_global_variable('prev_gps_obj', current_or_last_gps_obj)
        return gps_obj


def get_coords():
    coords = { 'lat': 0, 'lon': 0 }
    return_data = {
        'coordinates': coords,
        'instant_speed': 0,
        'timestamp': None
    }
    if serial_gps_conn is None:
        id = next_coords()
        place = Temp.objects.get(id=id)
        coords = { 'lat': place.lat, 'lon': place.lon }
        # return_data = { 'coordinates': coords, 'instant_speed': 0, 'timestamp': datetime.now() }
        gps_obj = temp2(coords)
        # end
        while gps_obj is None:
            gps_obj = temp2(coords)
        return gps_obj
    gps_obj = temp()
    # end
    while gps_obj is None:
        gps_obj = temp()
    return gps_obj
    line = serial_gps_conn.readline().decode('utf-8')
    if line.startswith('$GNGLL'):
        try:
            msg = pynmea2.parse(line)
            coords = {
                'lat': msg.latitude,
                'lon': msg.longitude
            }
        except pynmea2.ParseError as e:
            print("Parse error: {0}".format(e))
        finally :
            return_data['coordinates'] = coords
            return_data['timestamp'] = datetime.now()
        
    if line.startswith("$GNRMC"):  # Example of NMEA sentence for GPS data
        data_fields = line.split(',')
        # Check if the data line is valid and contains enough fields
        if len(data_fields) >= 8:
            # Extract the speed over ground (SOG) in knots
            speed_knots_str = data_fields[7]
            try:
                # Convert speed from string to float
                speed_knots = float(speed_knots_str)
                # Convert speed from knots to km/h
                speed_kmph = knots_to_kmph(speed_knots)
                # return speed_kmph
                print("Speed is : {:.2f}".format(speed_kmph))
                return_data['instant_speed'] = round(speed_kmph, 2)
            except ValueError:
                # return None
                print("Value Error")
            except Exception as e:
                print("Unknown Exception: {}".format(e))
        else:
            # return None
            print("Getting None")

    return return_data

def next_coords():
    f = open("temp.txt", "r")
    data = f.read()
    f.close()
    
    if data:
        f1 = open("temp.txt", "w")
        intData = int(data)
        intData+=1
        retData = intData
        f1.write(str(intData))
        f1.close()
    else:
        f1 = open("temp.txt", "w")
        retData = 1
        f1.write("1")
        f1.close()
    return retData