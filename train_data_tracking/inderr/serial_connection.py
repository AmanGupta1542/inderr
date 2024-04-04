# serial_connection.py
import serial
import logging

logger = logging.getLogger("inderr.views")

BAUDRATE = 9600
SERIAL_PORT = "COM5"  # Adjust this to your serial port
TIME_DELAY = 25

try:
    serial_connection = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE)
except :
    serial_connection = None
    logger.exception("Unable to connect")
