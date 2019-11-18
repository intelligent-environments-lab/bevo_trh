import time
import board
import busio
import adafruit_sht31d
import csv
from datetime import datetime  #storeage for time 
 
 
# Create library object using our Bus I2C port
i2c = busio.I2C(board.SCL, board.SDA)
sensor = adafruit_sht31d.SHT31D(i2c)
 
loopcount = 0

with open('Sensor_data.csv', mode='w') as J:
 data_writer.writerow(['Time','Temperature', 'Relative Humidity'])

 while True:
     print("\nTemperature: %0.1f C" % sensor.temperature)
     print("Humidity: %0.1f %%" % sensor.relative_humidity)
     loopcount += 1
     time.sleep(10)
     
     data_writer = csv.writer(J, delimiter=',')
     data_writer.writerow([datetime.now(), sensor.temperature,sensor.relative_humidity]）

    # every 10 passes turn on the heater for 1 second
    #if loopcount == 10:
        #loopcount = 0
        #sensor.heater = True
        #print("Sensor Heater status =", sensor.heater)
        #time.sleep(1)
        #sensor.heater = False
         #print("Sensor Heater status =", sensor.heater)
