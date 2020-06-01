need to enable I2C/1Wire using `sudo raspi-config`

# TODO: add supervisor to make sure program keeps running, and defaults to start running when rpi boots

# TODO: implement pid controller using PWM of hot plate https://simple-pid.readthedocs.io/en/latest/simple_pid.html#module-simple_pid.PID
# tune values: https://newton.ex.ac.uk/teaching/CDHW/Feedback/Setup-PID.html

# Humidity? maybe separate PID that just turns output and overhead fans on if too wet, and turns humidifier on if too dry

# Maybe PID won't work because we only have on/off switches... think about how to do that
