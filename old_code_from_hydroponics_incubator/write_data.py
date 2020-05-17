from SI7021 import SI7021
import datetime
import os
def write_data():
    sensor = SI7021()
    t = sensor.get_tempC()
    h = sensor.get_humidity()
    time = datetime.datetime.now().strftime("%Y:%m:%d %H:%M:%S")
    filename = "/home/pi/MVP/logs/data.csv"
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("TempC,Humidity,Timestamp\n")
    with open(filename, "a") as f:
        f.write("{},{},{}\n".format(t, h, time))

if __name__ == '__main__':
    write_data()
