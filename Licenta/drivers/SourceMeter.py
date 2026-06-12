import time

import pyvisa
from pyvisa.resources import MessageBasedResource

VALID_VOLT_RANGES = [0.02, 0.2, 2.0, 20.0, 200.0] # V
VALID_CURR_RANGES = [10e-9, 100e-9, 1e-6, 10e-6, 100e-6, 1e-3, 10e-3, 100e-3, 1.0, 3.0] # A

class Keithley2400:
    def __init__(self, visa_addr: str = None):
        self.visa_addr = visa_addr
        self._session = None

    def Initialize(self, visa_addr: str, IdQuery: bool = True, Reset: bool = False):
        if visa_addr:
            self.visa_addr = visa_addr

        rm = pyvisa.ResourceManager()
        self._session: MessageBasedResource = rm.open_resource(self.visa_addr)

        self._session.write("*CLS")
        if Reset:
            self._session.write("*RST")
        if IdQuery:
            return self._session.query("*IDN?")
        return None

    def Close(self):
        self._session.close()

    def read_source_function(self) -> str:
        query = self._session.query("SOUR:FUNC?").strip().replace('"', '').upper()
        if 'VOLT' in query:
            return 'VOLT'
        return 'CURR'

    def read_sense_function(self) -> str:
        query = self._session.query("SENS:FUNC?").strip().replace('"', '').upper()
        if 'VOLT' in query:
            return 'VOLT'
        return 'CURR'

    def configure_sense_function(self, mode: str):
        mode = mode.upper()

        if mode not in ["VOLT","CURR"]:
            raise ValueError("The measurement mode needs to be 'VOLT' or 'CURR'")

        self._session.write(f'SENS:FUNC "{mode}"')

    def configure_source_function(self, mode: str):
        if mode not in ["VOLT", "CURR"]:
            raise ValueError("The source mode needs to be 'VOLT' or 'CURR'")

        self._session.write(f"SOUR:FUNC {mode}")

    def configure_source_range_value(self, range_value: float):
        mode = self.read_source_function()
        if mode == 'VOLT':
            if range_value not in VALID_VOLT_RANGES:
                raise ValueError(f"The range needs to be: {VALID_VOLT_RANGES} V")
        elif mode == 'CURR':
            if range_value not in VALID_CURR_RANGES:
                raise ValueError(f"The range needs to be: {VALID_CURR_RANGES} A")
        else:
            raise ValueError("The source mode needs to be 'VOLT' or 'CURR'")

        self._session.write(f"SOUR:{mode}:RANG {range_value}")

    def configure_compliance(self, compliance: float):
        mode = self.read_sense_function()
        if mode not in ['VOLT', 'CURR']:
            raise ValueError("The source mode needs to be 'VOLT' or 'CURR'")

        self._session.write(f"SENS:{mode}:PROT {compliance}")

    def configure_source_level(self, level: float):
        mode = self.read_source_function()
        if mode not in ['VOLT','CURR']:
            raise ValueError("The source mode needs to be 'VOLT' or 'CURR'")

        self._session.write(f"SOUR:{mode}:LEV {level}")

    def configure_sense_range(self, range_value: float):
        mode = self.read_sense_function()
        if mode == 'VOLT':
            if range_value not in VALID_VOLT_RANGES:
                raise ValueError(f"The range needs to be: {VALID_VOLT_RANGES} V")
        elif mode == 'CURR':
            if range_value not in VALID_CURR_RANGES:
                raise ValueError(f"The range needs to be: {VALID_CURR_RANGES} A")
        else:
            raise ValueError("The measurement mode needs to be 'VOLT' or 'CURR'")

        self._session.write(f"SENS:{mode}:RANG {range_value}")

    def configure_output(self, state: str):
        self._session.write(f":OUTP {state}")

    def read_measurement(self) -> float:
        query = self._session.query(":READ?").strip().split(',')
        return float(query[1])

    def output_off_step(self, step: float = 0.2):
        mode = self.read_source_function()
        if mode not in ['VOLT', 'CURR']:
            raise ValueError("The source mode needs to be 'VOLT' or 'CURR'")

        if mode == 'CURR':
            current_val = self.read_measurement()

            if current_val > 0:
                while current_val > 0:
                    current_val = current_val - step

                    if current_val < 0:
                        current_val = 0.0
                    self.configure_source_level(current_val)
                    time.sleep(1.5)
            elif current_val < 0:
                while current_val < 0:
                    current_val += step
                    if current_val > 0:
                        current_val = 0.0

                    self.configure_source_level(current_val)
                    time.sleep(1.5)
        self.configure_output(state="OFF")
