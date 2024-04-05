# serial_connection.py
import serial
import logging

logger = logging.getLogger("inderr.serial_connection")

BAUDRATE = 9600
LED_BOARD_SERIAL_PORT = "COM5"  # Adjust this to your serial port
GPS_SERIAL_PORT = "COM4"
TIME_DELAY = 25

try:
    serial_connection = serial.Serial(LED_BOARD_SERIAL_PORT, baudrate=BAUDRATE)
except :
    serial_connection = None
    logger.exception("Unable to connect with LED board")

try:
    serial_gps_conn = serial.Serial(GPS_SERIAL_PORT, BAUDRATE, timeout=5.0)
except:
    serial_gps_conn = None
    logger.exception("Unable to connect with the GPS")