# **********************************************************************
# The University of Texas at Austin                                    *
# Intelligent Environments Laboratory (IEL)                            *
# Author: Hagen Fritz and Dung Le		                       *
# Project:                                                             *
# Email: hoangdung.le@utexas.edu                                       *
# **********************************************************************

import time
import math
import csv
import datetime
import os
import traceback

# Import sensor-specific libraries
import adafruit_sht31d
from board import SCL, SDA
from busio import I2C

f = open('name.txt','r')
beacon = f.read()

# Create I2C Object for sensors
# Also sets setup mode for GPIO to BCM
def createSensor():
	i2c = I2C(SCL, SDA)
	return i2c

#*****************************************
# File handling
FILEPATH = {
	'trh':'/home/pi/DATA/trh/'
}
filename_writer = {
	'trh': lambda date: FILEPATH['trh'] + 'b' + beacon + '_' + date.strftime('%Y-%m-%d') + '.csv'
}
#*****************************************
# import functions for each of the sensors
def sht31d_scan(sht):
	# Declare all global variables for use outside the functions
	global T, RH

	try:
		# Retrieve sensor scan data
		T = sht.temperature
		RH = sht.relative_humidity
	except:
		print('Error reading from SHT31D')
		T = -100
		RH = -100

	# Outputting
	print('-------------------------')
	print(f'T (C):\t{T}')
	print(f'RH (%):\t{RH}')
	print('-------------------------')

	# Return data
	data = {'T': T, 'RH': RH}
	return data

def data_mgmt():
	# Store adafruit sensor data locally and remotely
	timestamp = datetime.datetime.now()
	data_header = [
		'Timestamp',
		'T',
		'RH'
	]
	data = [{
		'Timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
		'T': sht_data_old['T'],
		'RH': sht_data_old['RH']
	}]
	key = 'trh'
	write_csv(
		key=key,
		date=timestamp,
		data_header=data_header,
		data=data
	)

def write_csv(key, date, data_header, data):
	'''
	Writes data to csv file. Key is used to decipher the filepath and style of the filename.
	Date filename is used to name & sort files chronologically. Creates a new file if none with
	filename exists or appends to the exsiting file. The data header specifies the field
	names and is a list of the dictionary keys. Data is a list of dictionaries.\n
	key: string\\
	date: datetime.datetime\\
	data_header: list\\
	data: list\\
	return: void
	'''
	filename = filename_writer[key](date=date)
	try:
		if not os.path.isfile(filename):
			# Now create new file locally
			with open(filename, mode='w+') as data_file:
				csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
				csv_dict_writer.writeheader()
				csv_dict_writer.writerows(data)
				if verbose:
					print('Wrote data for first time to:', filename)
		else:
			# Append to already existing file
			with open(filename, mode='a') as data_file:
				csv_dict_writer = csv.DictWriter(data_file, fieldnames=data_header)
				csv_dict_writer.writerows(data)
				if verbose:
					print('Appended data to:', filename)
	except Exception as e:
		traceback.format_exc()
		if verbose:
			print(type(e).__name__ + ': ' + str(e))

def main():
	'''
	Manages sensors and data storage on device.\n
	return: void
	'''
	print('Running Sensor\n')
	i2c = createSensor()
	# Setting up sgp30
	sht = adafruit_sht31d.SHT31D(i2c)

	global sht_data_old
	# Begin loop for sensor scans
	i = 1
	while True:
		print('*'*20 + ' LOOP %d '%i + '*'*20)
		sht_data_old = {'T': 0, 'RH': 0}
		sht_count = 0
		for j in range(5):
			#print('Running SGP30 scan...')
			sht_data_new = sht31d_scan(sht)
			if sht_data_new['T'] != -100 and math.isnan(sht_data_new['T']) == False:
				sht_count += 1
				for x in sht_data_old:
					sht_data_old[x] += sht_data_new[x]

		for x in sht_data_old:
			try:
				sht_data_old[x] /= sht_count
			except ZeroDivisionError:
				sht_data_old[x] = -100

		print("---------------------------------------")
		print("Average Values")
		print("---------------------------------------")
		print("T (C): {0:.3f}".format(sht_data_old['T']))
		print("RH (%): {0:.3f}".format(sht_data_old['RH']))
		print("---------------------------------------")

		# Data management
		print("Running data management...")
		data_mgmt()

		# Prepare for next loop
		delay = 52 #seconds
		print('Waiting', delay, 'seconds before rescanning...')
		#assert False
		time.sleep(delay)
		print('*'*20 + ' END ' + '*'*20)
		print('Rescanning...')
		i += 1

#********* EXECUTION START ************
main()
#************** END *******************
