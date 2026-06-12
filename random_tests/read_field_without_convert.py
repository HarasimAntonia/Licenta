import serial
PORT = 'COM10'
BAUDRATE = 115200
import time
READINGS=100

def funct():
        arduino = serial.Serial(PORT, BAUDRATE, timeout=2.0)
        time.sleep(2)

        arduino.write('reading_sensitivity\n'.encode('utf-8'))
        active_readings = 0
        while active_readings < READINGS:
            line_before = arduino.readline()
            if not line_before:
                print("\n[ERROR] Timeout.")
                break
            line_after = line_before.decode('utf-8').strip()
            elements = line_after.split()
            if len(elements) == 4:
                x = int(elements[0])
                y = int(elements[1])
                z = int(elements[2])
                active_readings += 1
                print(f"[{active_readings:03d}/{READINGS}] X: {x:} | Y: {y:} | Z: {z:}")

if __name__ == '__main__':
    funct()