#!/usr/bin/python

######################################################################
# (C) ALCHEMY POWER INC 2016,2017 etc. - ALL RIGHT RESERVED.
# CODE SUBJECT TO CHANGE AT ANY TIME.
# YOU CAN COPY/DISTRIBUTE THE CODE AS NEEDED AS LONG AS YOU MAINTAIN
# THE HEADERS (THIS PORTION) OF THE TEXT IN THE FILE.
######################################################################
# Last update 06/10/2019
# Compensated for V drop in R-C filter
# Adjusted temp measurement to reflect R.
# Update 11/8/2019
# Added two different lines for measuring temperature on PiZ-UpTime and Pi-UpTime as 
# they use different NTC's.
#
# PLEASE READ NOTES BELOW. THERE IS NO README FILE.


# NOTE - temperature measurement is + or - 2 C
#
# Please change the temperature calculation appropriately depending on produyct you are using.
#
# Search for TempV an you will find it documented.
#
# If you are running this script in the background, you may not need to capture all the data. You can comment out the print statements.
#
# Save a copy of this code if you comment out the print statements as you may need to run this interactively to see operating conditions. 
#
#
# Change the operating range alerts by changing values for Temp_min and Temp_max
# Operating range is assumed to be 5 C to 50 C. Note - this is the temp on the UpTime 
# board and has nothing to do with battery temperature. 
# 
#
# This script will print the instantenous voltages and temperature reading. 
# Disable (comment out) print statements to run the code in the background. 
# Enable print to run the code interactively.
#

import time
import smbus
import sys
import os
import subprocess

from smbus import SMBus
from sys import exit

# for older PI's (version 1) use bus = SMBus(0) in statement below.
bus = SMBus(1)
# One of the 3 possible addresses of the unit.
address = 0x48
# address = 0x49
# address = 0x4B
#
# address is the I2C address of the ADC chip.
# Use i2cdetect -y 1 to find the address. Use "y 0" for older Pi's.
#
# Depending on the jumper settings the address will change. Only 3 addresses are allowed. 
# Please make sure you use the proper address, else the script will give an error. 
#

#
# Chip used is TI TLA2024 - 4 channel, 12 bit ADC.
# See Page 18 and then Page 17 of data sheet for how to configure the bits.
# Bits set for specific channel, single shot conversion, PGA of 6.144V
# Error  or sensitivity is 3mV for settings below.
channel0        =     0b11000001   # Measure V-in
channel1        =     0b11010001   # Measure V-out
channel2        =     0b11100001   # Measure V-battery
channel3        =     0b11110001   # Measure V across NTC, to measure Temperature.
# Use these channel settings for vref = 2.048V
# channel0        =     0b11000101   # Measure V-in
# channel1        =     0b11010101   # Measure V-out
# channel2        =     0b11100101   # Measure V-battery
# channel3        =     0b11110101   # Measure V across NTC, to measure Temperature.
#
# Data Rate set to default of 128 SPS
#
#
#####################################################################################################################
# Determine the maximum voltage - see notes above or page 18 of datasheet.
#####################################################################################################################
vref = 6.144 # This is the max Vref - allows us to measure Vin up to Vin + 0.3V
# vref = 2.048 # This is the max Vref with second set of channel settings
# vref is determined by the bit setting specified in channel# above. See Table 7, PGA[2,0]
#####################################################################################################################


max_reading = 2097.0 # 2^11 - 1 = 12 bits of information, with MSB set to zero. See page 15 of data sheet.

# Now we determine the operating parameters.
# lange = number of bytes to read. 
# zeit (German for time) - tells how frequently you want the readings to be read from the ADC. Define the
# time to sleep between the readings.
# tiempo (Spanish - noun - for time) shows how frequently each channel is read in over the I2C bus. Best to use
# timepo between each successive readings.
#
# All the timeouts and other operational variables.
lange = 0x02 # number of bytes to read in the block. Need for Debug statements below.
zeit = 5     # number of seconds to sleep between each measurement group. This will read variables every zeit seconds.
tiempo = 0.1 # number of seconds to sleep between each channel reading.
# tiempo = 1/SPS (default is 128) + 1 ms - so tiempo can be as low as 0.002 seconds. We deliberately make it
# higher here for readings to settle down. Fast enough for us. In fact, in many cases this may not even be needed.
#####################################################################################################################
#####################################################################################################################
# Battery V
#=========================================================================================================
V_batt_min = 3.1 # Minimum V of battery at which time shutdown is triggered.
# Change that if you want the shutdown to initiate sooner. Note at 2.5V all electronics
# will be shut down.
#=========================================================================================================
# Min Voltage
#=========================================================================================================
V_in_min = 3.8 # Minimum input Voltage. Below this voltage level, it is not recommended to operate the
               # Pi. Called a brown-out condition. We display result as 0.
#=========================================================================================================
# Temperature
#=========================================================================================================
# Temp min/max is the min and max temperature for which battery can charge.
# This can be changed to suite your needs.
# Note the hardware does not allow charging for Temp_min of 0C
# and a maximum of 50C.

Temp_min = 5.0 # Min temperature at which battery charging enclose should be warmed up.
Temp_max = 60.0 # Max temperature after which battery charging should be discontinued.
                # Best to provide cooling e.g. a fan.
# This range is lower/higher by about 10 degrees to allow corrective action.

#=========================================================================================================


# This is a subroutine which is called from the main routine. 
# The variables passed are:
# adc_address - I2C address for the device. 
# adc_channel - the analog channel you want to read in.
#####################################################################################################################
#####################################################################################################################

def getreading(adc_address,adc_channel):
#Debug
#	print "ADC Address and channel is ", adc_address, adc_channel, "Sleeping for ", tiempo, " seconds."

# Reset the registers (address and data) and then read the data.
	bus.write_i2c_block_data(adc_address, 0x01, [0x85, 0x83]) #Reset config register
	bus.write_i2c_block_data(adc_address, 0x00, [0x00, 0x00]) #Reset data register
# Wait till the reading stabilize.
	time.sleep(tiempo) # Wait for conversion to finish
# Trigger the ADC for a one-shot reading on the channel.
	bus.write_i2c_block_data(adc_address, 0x01, [adc_channel, 0x43]) # Initialize channel we want to read.
	time.sleep(tiempo) # Wait for conversion to finish
#
# Debug
# Print the Config Register
#	readread = bus.read_i2c_block_data(adc_address, 0x01, lange)
#	print "Config Reg is ", readread[1], readread[0]

# Read the data register.
	reading  = bus.read_word_data(adc_address, 0) # Read data register
#Debug - print the data read
#	print "Data register read as 16 but word is ", reading

# Do the proper bit movements. Refer to data sheet for how the bits are read in.
 	valor = ((((reading) & 0xFF) <<8) | ((int(reading) & 0xFFF0)>>8))
	valor = valor >> 4 # 4 LSB bits are ignored.

# Debug print the bit movement value...
#	print("Valor is 0x%x" % valor)

	volts = valor/max_reading*vref

	return volts

# End of sub routine
#####################################################################################################################
#####################################################################################################################

# Main routine. 

ch0_mult = 1 # Multiplier is used to offset any values and for calibration adjustments. Vin
ch1_mult = 1 # Multiplier for Channel 1 - Vout
ch2_mult = 1 # Multiplier for Channel 2 - Vbattery
ch3_mult = 1 # Multiplier for Channel 3 - V for Temperature at the NTC (thermistor).

# Main routine - shows an endless loop. If used with a cron script or a 
# trigger via GPIO, an endless loop is not recommended.
#
#

while (True):
	Vin = ch0_mult*getreading(address,channel0) + 0.08
#	time.sleep(tiempo)
	Vbattery = ch1_mult*getreading(address, channel1) + 0.08
	Vout = ch1_mult*getreading(address, channel2) + 0.08
	TempV = ch3_mult*getreading(address, channel3) + 0.08
# For Pi-Z-UpTime 2.0 use the value below.
	TempC = (3.95 - TempV) / 0.0432 # Temperature in C calculated.
# Use the line below for Pi-UpTime UPS 2.0
#	TempC = (4.236 - TempV) / 0.0408 # Temperature in C calculated.
# Convert C to F
	TempF = TempC * 1.8 + 32.0  # Temperature in F
#====================================================================================
# Check to see if all operating conditions are OK. 
#
#====================================================================================
	# If input V is low and battery V is low initiate the shutdown process.
	if ( Vin < V_in_min ): # Vin has failed or is a brownout
		if (Vbattery < V_batt_min ): # Battery is low, time to shutdown.
#			print("Shutdown initiated at %s " % (time.ctime()))
                	#
			sys.stdout.flush()
			subprocess.call("shutdown -h 2 &", shell=True)
                	#
                	# Sleep for a second or so for the shutdown process to fork and then exit
                	# Print the values out if needed - ok for debug.
			time.sleep(2)
                	# Flush any stdout messages before exiting..
			exit() # Exit out of the code - no further print etc. is printed.

#====================================================================================
# End of check statements. At end of the while statement.
#====================================================================================
	sys.stdout.flush()
# Sleep till next reading.
	time.sleep(zeit)
# End of main loop.