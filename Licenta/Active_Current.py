import serial
import time
from openpyxl import Workbook
from openpyxl.chart import LineChart, Reference
from openpyxl.chart.series import SeriesLabel
from Licenta.drivers.SourceMeter import Keithley2400

# SMU address
SMU_ADDR = 'GPIB0::1::INSTR'

# Serial communication and sample number
PORT = 'COM10'
BAUDRATE = 115200
SAMPLE = 1

# Number of measurements and name of the Excel file where the measurements will be saved
READINGS = 100
EXCEL_FILE = f'../Active_Current_SAMPLE{SAMPLE}.xlsx'

def create_active_current_graphic(sheet, readings, position):
    """ Generate the graphic for Active Current """

    chart = LineChart()
    chart.title = "Active Current Analysis"
    chart.style = 13
    chart.y_axis.title = "Current (mA)"
    chart.x_axis.title = "Number of measurement"
    chart.width = 20
    chart.height = 10

    # Limit on Y axis
    chart.y_axis.scaling.min = 0.0
    chart.y_axis.scaling.max = 1.5

    # Read measured data (Column B)
    data_measured = Reference(sheet, min_col=2, min_row=1, max_col=2, max_row=readings + 1)
    chart.add_data(data_measured, titles_from_data=True)

    # Legend
    if len(chart.series) >= 1:
        chart.series[0].title = SeriesLabel(v="Measured Current")

    sheet.add_chart(chart, position)

def active_current_test():
    smu = Keithley2400()
    arduino = None
    try:
        print(f"[{PORT}] Connecting to Arduino.")
        arduino = serial.Serial(PORT, BAUDRATE, timeout=3.0)
        time.sleep(2)

        print(f"[{PORT}] Reset sensor.")
        arduino.write('reset_sensor\n'.encode('utf-8'))

        print(f"[SMU] Initializing SMU.")
        idn = smu.Initialize(visa_addr=SMU_ADDR, IdQuery=True, Reset=True)
        print(f"Connected to: {idn}")

        print(f"[{PORT}] Supply the sensor from the SourceMeter.")
        arduino.write('power_smu\n'.encode('utf-8'))
        time.sleep(0.5)

        print("[SMU] Configure the SMU to source 5V and measure the current.")
        smu.configure_sense_function(mode="CURR")
        smu.configure_source_function(mode="VOLT")
        smu.configure_source_range_value(range_value=20.0)
        smu.configure_compliance(compliance=0.01)
        smu.configure_source_level(level=5.0)
        smu.configure_sense_range(range_value=0.01)

        print("[SMU] Output ON")
        smu.configure_output('ON')
        time.sleep(0.5)

        # Excel initialization
        wb = Workbook()
        sheet = wb.active
        sheet.title = "Active Current Data"

        # Table header
        sheet.append(["No.", "Active Current (mA)"])

        print(f"\nStarting {READINGS} current readings.")
        for i in range(1, READINGS + 1):
            val = smu.read_measurement()
            current_mA = val * 1000  # mA
            print(f"[{i:03d}/{READINGS}] : {current_mA:.3f} mA")
            sheet.append([i, current_mA])
        create_active_current_graphic(sheet, READINGS, position="F2")

        # Saving in Excel
        try:
            wb.save(EXCEL_FILE)
            print(f"\n[SUCCESS] Excel file saved successfully as '{EXCEL_FILE}'.")
        except PermissionError:
            print(f"\n[ERROR] Cannot save '{EXCEL_FILE}'.")

    except Exception as e:
        print(f"\n[ERROR] Something went wrong :) {e}")
    finally:
        print("\nClosing the communication.")
        smu.configure_output('OFF')
        smu.Close()
        arduino.close()

if __name__ == "__main__":
    active_current_test()