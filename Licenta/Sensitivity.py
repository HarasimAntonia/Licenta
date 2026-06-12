import serial
import time
from openpyxl import Workbook
from openpyxl.chart import ScatterChart, Reference
from Licenta.drivers.SourceMeter import Keithley2400
from openpyxl.chart.series_factory import SeriesFactory

# SMU address
SMU_ADDR = 'GPIB0::21::INSTR'

# Serial communication and sample number
PORT = 'COM10'
BAUDRATE = 115200
SAMPLE = 5

# Coil constant
COIL_CONSTANT = 32.9 # mT/A
CURRENT_LIST = [-1.6, -1.4, -1.2, -1.0, -0.8, -0.6, -0.4, -0.2, 0.0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2, 1.4, 1.6]  # vezi ce lista pui in funtie de cat camp simte Amperi
READINGS = 50

# Excel file name
EXCEL_FILE = f'../Sensitivity_SAMPLE{SAMPLE}.xlsx'

def calculate_sensitivity(calculated_field, measured_field):
    n = len(calculated_field)
    mean_x = sum(calculated_field) / n
    mean_y = sum(measured_field) / n
    numarator = sum((x - mean_x) * (y - mean_y) for x, y in zip(calculated_field, measured_field))
    numitor = sum((x - mean_x) ** 2 for x in calculated_field)
    slope = numarator/ numitor
    return slope

def create_sensitivity_graphic(sheet, num_points, position):
    """ Generate the graphic for Sensitivity (Measured Field Z vs Applied Current) """
    chart = ScatterChart()
    chart.title = "Sensitivity Analysis"
    chart.style = 13
    chart.x_axis.title = "Calculated Magnetic Field Z-axis (mT)"
    chart.y_axis.title = "Magnetic Field Z-axis (LSB)"
    chart.width = 20
    chart.height = 10

    # X axis values (Calculated Magnetic Field in mT - Column B)
    x_values = Reference(sheet, min_col=2, min_row=2, max_row=num_points + 1)

    # Y axis values (Measured Magnetic Field in LSB - Column D)
    y_values = Reference(sheet, min_col=4, min_row=2, max_row=num_points + 1)

    series = SeriesFactory(values=y_values, xvalues=x_values, title="Magnetic Field Z-axis")
    chart.series.append(series)
    sheet.add_chart(chart, position)

def sensitivity_test():
    smu = Keithley2400()
    arduino = None
    try:
        print(f"[{PORT}] Connecting to Arduino.")
        arduino = serial.Serial(PORT, BAUDRATE, timeout=3.0)
        time.sleep(2)

        print(f"[{PORT}] Reset sensor.")
        arduino.write('reset_sensor\n'.encode('utf-8'))
        time.sleep(0.5)

        print(f"[{PORT}] Supply the sensor from Arduino.")
        arduino.write('power_arduino\n'.encode('utf-8'))
        time.sleep(1)

        print(f"[SMU] Initializing SMU.")
        idn = smu.Initialize(visa_addr=SMU_ADDR, IdQuery=True, Reset=True)
        print(f"Connected to: {idn}")

        print("[SMU] Configure SMU for coil.")
        smu.configure_source_function(mode="CURR")
        smu.configure_sense_function(mode="VOLT")

        smu.configure_source_range_value(range_value=3.0)
        smu.configure_sense_range(range_value=20.0)
        smu.configure_compliance(compliance=20.0)

        print("[SMU] Output ON")
        smu.configure_output('ON')
        time.sleep(0.5)

        calculated_field = []
        measured_field = []
        raw_data = [] # temporary list

        print(f"\nStarting sensitivity test across {len(CURRENT_LIST)} current steps.")

        for i, current in enumerate(CURRENT_LIST):
            smu.configure_source_level(level=current)
            time.sleep(0.5)
            applied_field = current * COIL_CONSTANT

            print(f"[{i + 1}/{len(CURRENT_LIST)}] Current: {current} A | Applied Field: {applied_field:.3f} mT")
            arduino.write('reading_sensitivity\n'.encode('utf-8'))

            z_sum = 0.0
            active_readings = 0

            while active_readings < READINGS:
                line_before = arduino.readline()
                if not line_before:
                    print("\n[ERROR] Timeout.")
                    break
                line_after = line_before.decode('utf-8').strip()
                elements = line_after.split()
                if len(elements) == 4:
                    z_val = -float(elements[2])
                    z_sum += z_val
                    active_readings += 1

            z_avg = round(z_sum / READINGS, 3)

            calculated_field.append(applied_field)
            measured_field.append(z_avg)

            # Add data to temporary list
            raw_data.append([current, applied_field, z_avg])

        sensitivity = round(calculate_sensitivity(calculated_field, measured_field),3)
        print(f"Calculated Sensitivity (Slope): {sensitivity:.4f}")

        # Excel initialization
        wb = Workbook()
        sheet = wb.active
        sheet.title = "Sensitivity Data"

        # Table header
        sheet.append([
            "Applied Current (A)",
            "Calculated Magnetic Field Z-axis (mT)",
            "Measured Magnetic Field Z-axis (mT)",
            "Measured Magnetic Field Z-axis (LSB)"
        ])

        for data in raw_data:
            current, applied_field, z_avg_lsb = data
            z_avg_mt = round(z_avg_lsb / sensitivity, 2)
            sheet.append([current, applied_field, z_avg_mt, z_avg_lsb])

        # Saving senzitivity in Excel
        sheet['F2'] = "Sensitivity (Slope):"
        sheet['G2'] = sensitivity

        # Create sensitivity graphic
        create_sensitivity_graphic(sheet, num_points=len(CURRENT_LIST), position="F5")

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
        if smu:
            smu.output_off_step(step=0.1)
            smu.Close()
        if arduino:
            arduino.close()

if __name__ == "__main__":
    sensitivity_test()