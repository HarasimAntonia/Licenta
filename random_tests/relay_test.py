# Testare
# Sa am alimentare de la SMU

import serial
PORT = 'COM10'
BAUDRATE = 115200
import time
def funct():
        arduino = serial.Serial(PORT, BAUDRATE, timeout=2.0)
        time.sleep(2)

        print("Sending command to Arduino to read the interrupt frequency.")
        arduino.write('connect_SDA_SCL\n'.encode('utf-8'))
        line_before = arduino.readline()
        print(line_before)
if __name__ == '__main__':
    funct()