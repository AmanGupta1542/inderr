
import serial
import pynmea2

# Replace 'COMx' with the actual COM port or serial device of your GPS receiver
def get_coords():
    data = { 'lat': 0, 'lon': 0 }
    try:
        ser = serial.Serial('COM4', 9600, timeout=5.0)
    except Exception as e:
        print(e)
        return data
    line = ser.readline().decode('utf-8')
    if line.startswith('$GNGLL'):
        try:
            msg = pynmea2.parse(line)
            data = {
                'lat': msg.latitude,
                'lon': msg.longitude
            }
            print("Latitude: {0}, Longitude: {1}".format(msg.latitude, msg.longitude))
            print("Raw NMEA data: {0}".format(line))
        except pynmea2.ParseError as e:
            print("Parse error: {0}".format(e))
        finally :
            return data
    else:
        print("$GNGLL Not Found")
        return data
