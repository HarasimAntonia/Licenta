
from Licenta.drivers.SourceMeter import Keithley2400

def func():
    smu = Keithley2400()
    smu.Initialize(visa_addr='GPIB0::21::INSTR',IdQuery=True,Reset=True)
    #print(smu.read_measurement())
    smu.configure_source_function(mode="CURR")
    smu.configure_sense_function(mode="VOLT")

    smu.configure_source_range_value(range_value=3)
    smu.configure_sense_range(range_value=20.0)
    smu.configure_compliance(compliance=20.0)
    smu.configure_source_level(level=0.001)
    smu.configure_output(state="ON")
    smu.output_off_step(step = 0.0001)

if __name__ == "__main__":
    func()