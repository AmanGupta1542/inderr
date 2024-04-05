
import serial
import pynmea2
import logging
logger = logging.getLogger("inderr.coords")

from .models import Temp
from .serial_connection import serial_gps_conn


def get_coords():
    data = { 'lat': 0, 'lon': 0 }
    if serial_gps_conn is None:
        id = next_coords()
        place = Temp.objects.get(id=id)
        data = { 'lat': place.lat, 'lon': place.lon }
        return data
    line = serial_gps_conn.readline().decode('utf-8')
    if line.startswith('$GNGLL'):
        try:
            msg = pynmea2.parse(line)
            data = {
                'lat': msg.latitude,
                'lon': msg.longitude
            }
        except pynmea2.ParseError as e:
            print("Parse error: {0}".format(e))
        finally :
            return data
    else:
        print("$GNGLL Not Found")
        return data

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