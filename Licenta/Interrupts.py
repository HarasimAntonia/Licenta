import serial
import time

# Serial communication and sample number
PORT = 'COM10'
BAUDRATE = 115200
SAMPLE = 1

def interrupts_frequency():
    arduino = None
    try:
        print(f"[{PORT}] Connecting to Arduino.")
        arduino = serial.Serial(PORT, BAUDRATE, timeout=10.0)
        time.sleep(2)

        print(f"[{PORT}] Reset sensor.")
        arduino.write('reset_sensor\n'.encode('utf-8'))

        print(f"[{PORT}] Supply the sensor from the Arduino.")
        arduino.write('power_arduino\n'.encode('utf-8'))
        time.sleep(1)

        print(f"Sending command to Arduino to read the interrupt frequency for SAMPLE {SAMPLE}.\n")
        arduino.write('interrupts\n'.encode('utf-8'))

        received_lines = 0
        while received_lines < 3:
            read_line = arduino.readline()

            if not read_line:
                print("\n[TIMEOUT] No data read.")
                break

            data = read_line.decode('utf-8').strip()
            if data:
                print(f"{data}")
                received_lines += 1

    except Exception as e:
        print(f"\n[ERROR] Something went wrong :) {e}")
    finally:
        print("\nClosing the communication.")
        arduino.close()

if __name__ == '__main__':
    interrupts_frequency()