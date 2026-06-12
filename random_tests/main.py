from Licenta import Active_Current, Offset_and_Noise, Interrupts, PD_Current
import time

if __name__ == '__main__':
    Offset_and_Noise.offset_and_noise()
    time.sleep(0.5)
    Interrupts.interrupts_frequency()
    time.sleep(0.5)
    Active_Current.active_current_test()
    time.sleep(0.5)
    PD_Current.power_down_current_test()


