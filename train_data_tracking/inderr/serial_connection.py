# serial_connection.py
import serial

BAUDRATE = 9600
SERIAL_PORT = "COM5"  # Adjust this to your serial port

serial_connection = serial.Serial(SERIAL_PORT, baudrate=BAUDRATE)
