import time
import yaml
import pandas as pd
from functools import partial
import matplotlib.pyplot as plt
from simple_pid import PID

import signal
import sys
signal.signal(signal.SIGINT, signal.default_int_handler)


# def signal_handler(sig, frame, **kwargs):
    # print('Exiting')
    # sys.exit(0)


class WaterBoiler:
    """
    Simple simulation of a water boiler which can heat up water
    and where the heat dissipates slowly over time
    """

    def __init__(self, temp, max_temp=300, min_temp=20, delay_cycles=10, cooling_speed=0.2):
        self.temp = temp
        self.max_temp = max_temp
        self.min_temp = min_temp
        self.delay_storage = []
        self.delay_cycles = delay_cycles
        self.cooling_speed = cooling_speed

    def update(self, boiler_power, dt):
        self.delay_storage.append((boiler_power, dt))
        if len(self.delay_storage) > self.delay_cycles:
            self.delay_storage = self.delay_storage[1:]
        elif len(self.delay_storage) < self.delay_cycles:
            return self.temp
        boiler_power, dt = self.delay_storage[0]
        if boiler_power > 0:
            # boiler can only produce heat, not cold
            if self.temp < self.max_temp:
                self.temp += boiler_power * dt

        # some heat dissipation
        if self.temp > self.min_temp:
            self.temp -= self.cooling_speed * dt
        return self.temp

def set_pid(pid, filename):
    try:
        with open(filename) as f:
            new_config = yaml.safe_load(f)
        tunings = tuple(new_config['tunings'])
        setpoint = new_config['setpoint']
    except Exception as e:
        print("unable to load new config")
        return
    if tunings != pid.tunings:
        print(f"setting tunings to {tunings}")
        try:
            pid.tunings = [float(x) for x in tunings]
        except (ValueError, TypeError):
            print("Unable to set tunings")
            return
    if setpoint != pid.setpoint:
        print(f"setting setpoint to {setpoint}")
        try:
            pid.setpoint = float(setpoint)
        except (ValueError, TypeError):
            print("Unable to set setpoint")
    return tunings, setpoint

if __name__ == '__main__':
    pid = PID(1, 0, 0)
    res = set_pid(pid, 'tuning.yml')
    if res:
        tunings, setpoint = res
    boiler = WaterBoiler(setpoint, delay_cycles=10, cooling_speed=1)
    temp = boiler.temp
    pid.output_limits = (0, 100)

    start_time = time.time()
    last_time = start_time

    # keep track of values for plotting
    setpoints = []
    times = []
    powers = []
    temps = []

    #while time.time() - start_time < 10:
    # signal.signal(signal.SIGINT, partial(
        # signal_handler, times=times, temps=temps, powers=powers, setpoints=setpoints
    # ))
    # TODO in jupyter, dynamically/automatically load water_boiler.csv and graph it
    last_save = None
    last_update = None
    checkpoint_time = 0.5
    update_tuning_time = 0.5
    interval = 0.001
    num_samples_to_keep = 10000
    while True:
        num_saved = len(powers)
        current_time = time.time()
        dt = current_time - last_time
        time_since_start = current_time - start_time

        power = pid(temp)
        temp = boiler.update(power, dt)

        last_time = current_time

        powers.append(power)
        times.append(time_since_start)
        temps.append(temp)
        setpoints.append(pid.setpoint)
        if len(powers) > num_samples_to_keep:
            powers = powers[-num_samples_to_keep:]
        if len(times) > num_samples_to_keep:
            times = times[-num_samples_to_keep:]
        if len(temps) > num_samples_to_keep:
            temps = temps[-num_samples_to_keep:]
        if len(setpoints) > num_samples_to_keep:
            setpoints = setpoints[-num_samples_to_keep:]

        if last_save is None:
            last_save = time.time()
        if time.time() - (last_save or time.time()) > checkpoint_time:
            pd.DataFrame({'powers': powers,
                          'times': times,
                          'temps': temps,
                          'setpoints': setpoints}).to_csv('water_boiler.csv', index=False)
            last_save = time.time()
        if last_update is None:
            last_update = time.time()
        if time.time() - last_update > update_tuning_time:
            res = set_pid(pid, 'tuning.yml')
            if res:
                tunings, setpoint
            last_update = time.time()
        time.sleep(interval)
