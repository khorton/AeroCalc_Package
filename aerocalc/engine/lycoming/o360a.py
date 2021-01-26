#! /usr/bin/env python3

# Copyright (c) 2006, Kevin Horton
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# *
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * The name of Kevin Horton may not be used to endorse or promote products
#       derived from this software without specific prior written permission.
# *
# THIS SOFTWARE IS PROVIDED BY KEVIN HORTON ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL KEVIN HORTON BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# version 0.3, 27 Feb 2020

# Version History:
# vers     date       Notes
#  0.1   14 May 2006  First release.
#
#  0.2   16 May 2006  Corrected errors in examples.  Added percent power functions
#                     pp, pp2mp and pp2rpm.  Changed pwr2mp and pwr2rpm functions 
#                     to round off results to two decimal places.
# 0.3    27 Feb 2020  Corrected errors in examples.  Confirmed compatibility with Python 3.7

""" 
Calculate Lycoming O-360-A series horsepower.

Replicates the power chart in the Lycoming Operators Manual.  The chart in
the operator's manual only goes down to 2000 rpm or manifold pressures down
to 12" HG, so powers for rpms less than 2000 or manifold pressures less than
12" HG are extrapolated.
"""

# TO DO:  1. Done
#
#         2. Done
#
#         3. Done.
#
#         4. Done.
#
#         5. Done.
#
#         6. Done.

# DONE:   1. add temperature correction
#
#         2. Something screwy with interpolation of pwr with rpm.  Fixed.
#
#         3. Validate.
#
#         4. Add function to determine the MP required to get a desired power,
#            given the other inputs.
#
#         5. Add function to determine the rpm required to get a desired power,
#            given the other inputs.
#
#         6. Does not work below 12".
#
#         7. Update the doc strings.
#

# NOTES   1. Takes about 1.5e-5 sec per calculation on a 1.33 GHz PPC G4, so 
#            this should be suitable for every record in the FT data.


import math as M
import std_atm as SA
import unit_conversion as U


# def validate_rpm(rpm):
# 	if rpm % 100 != 0:
# 		raise ValueError, 'The rpm value in _pwr_sl must be a multiple of 100 rpm.'
# 	
# 	if rpm < 1800 or rpm > 2700:
# 		raise ValueError, 'The rpm in _pwr_sl must be between 1800 and 2700.'


def _pwr_sl(N, MP):
	""" 
	Returns power at sea level, standard day.
	"""
	
# 	validate_rpm(N)
	
	if N == 2700:
		return 96+ (MP - 18) * (184.3 - 96) / (28.75 - 18)
		
	elif N >= 2600:
		return 93 + (MP - 18) * (180.5 - 93) / (28.65 - 18)
		
	elif N >= 2400:
		return 88.85 + (MP - 18) * (174.8 - 88.85) / (29 - 18)

	elif N >= 2200:
		return 81.8 + (MP - 18) * (165.1 - 81.8) / (29.13 - 18)

	elif N >= 2000:
		return 73.8 + (MP - 18) * (150 - 73.8) / (29.13 - 18)

# Density ratio at full throttle for MP and rpm

# retrieve data as:
# data_item = DR_FT_alt[2300][14]
# 
# rpm	   12       	14	       16	        18	        20	        22	        24	        26	       28	        30
DR_FT_alt = {2000 : {12 : 0.489059, 14 : 0.553907, 16 : 0.617007, 18 : 0.678913, 20 : 0.738824, 22 : 0.798255, 24 : 0.855159, 26 : 0.911022, 28 : 0.968206, 30 : 1.023620},
             2200 : {12 : 0.490754, 14 : 0.554839, 16 : 0.618019, 18 : 0.680001, 20 : 0.740217, 22 : 0.798994, 24 : 0.856458, 26 : 0.912385, 28 : 0.969634, 30 : 1.025111},
             2400 : {12 : 0.490754, 14 : 0.556706, 16 : 0.619032, 18 : 0.681091, 20 : 0.741962, 22 : 0.800721, 24 : 0.859060, 26 : 0.915116, 28 : 0.971064, 30 : 1.026603},
             2600 : {12 : 0.493305, 14 : 0.558577, 16 : 0.621062, 18 : 0.682183, 20 : 0.743128, 22 : 0.803192, 24 : 0.861668, 26 : 0.917853, 28 : 0.976799, 30 : 1.032587},
             2700 : {12 : 0.495012, 14 : 0.559515, 16 : 0.622079, 18 : 0.684369, 20 : 0.745462, 22 : 0.804430, 24 : 0.862975, 26 : 0.919224, 28 : 0.978237, 30 : 1.034087}}

def _DR_FT_from_MP(rpm, MP):
	""" 
	Returns the density ratio at which a given rpm produces a given 
	manifold pressure at full throttle.
	"""
	if MP >= 28:
		mp1 = 28
	elif MP <= 12:
		mp1 = 12
	else:
		mp1 = MP - MP % 2
	
	mp2 = mp1 + 2

	DR1 = DR_FT_alt[rpm][mp1]
	DR2 = DR_FT_alt[rpm][mp2]

	DR_rpm = DR1 + (MP - mp1) * (DR2 - DR1) / (mp2 - mp1)
	
	return DR_rpm


# definition of lines at altitude
# rpm at altitude	hp at sea level	ALT2	density ratio at ALT2	hp at ALT2

HP_FT = {2000 : {'hp_sl' : 150, 'hp_25K' : 56.7},
         2200 : {'hp_sl' : 165.1,   'hp_25K' : 61.8},
         2400 : {'hp_sl' : 174.8,   'hp_25K' : 65.7},
         2600 : {'hp_sl' : 180.5,   'hp_25K' : 68},
         2700 : {'hp_sl' : 184.3,   'hp_25K' : 69.5}}

DR_25K = 0.44811924767834066 # density ratio at 25,000 ft

def _hp_at_FT(rpm, altitude):
	""" 
	Returns the horsepower at full throttle at a given rpm and altitude.
	"""
	# get density ratio from the altitude
	DR = SA.alt2density_ratio(altitude)
	
	# get power at rpm
	hp_sl = HP_FT[rpm]['hp_sl']
	hp_25K = HP_FT[rpm]['hp_25K']
	hp_at_FT = hp_sl - (1 - DR) * (hp_sl - hp_25K) / (1 - DR_25K)
# 	print 'hp =:', hp_rpm
	
	return hp_at_FT


def _hp_at_MP_and_altitude(rpm, MP):
	""" 
	Returns the power at a given rpm and MP at full throttle.
	"""
	# get density ratio for this MP and altitude, at full throttle
	DR = _DR_FT_from_MP(rpm, MP)
	
	# get power at this condition
	altitude = SA.density_ratio2alt(DR)
	hp = _hp_at_FT(rpm, altitude)
	
	return hp, DR
	

def _pwr_std_temp(rpm, MP, altitude):
	""" 
	Returns the power at a given rpm, MP and altitude, assuming 
	standard temperature.
	
	Units are n/mn, inches HG and feet.
	
	Example:
	
	Determine power at 2700 rpm, 28.6 inches HG manifold pressure 
	and 0 ft altitude:
	>>> _pwr_std_temp(2700, 28.2, 0)
	179.78232558139536

	"""
	# get the power at sea level (i.e. point B on the left side of the Lycoming power chart)
	
	# get pwr at two even hundreds of rpm, and then interpolate
	if rpm >= 2600:
		rpm1 = 2600
		rpm2 = 2700
	elif rpm >= 2400:
		rpm1 = 2400
		rpm2 = 2600
	elif rpm >= 2200:
		rpm1 = 2200
		rpm2 = 2400
	else:
		rpm1 = 2000
		rpm2 = 2400
	
	pwr_SL1 = _pwr_sl(rpm1, MP)
	pwr_SL2 = _pwr_sl(rpm2, MP)
	
	# get power at full throttle at this rpm and MP at altitude (i.e. point A on the right side of the Lycoming power chart)
	# density ratio at point A on the right side of the Lycoming power chart)
	pwr_FT1, DR_FT1 = _hp_at_MP_and_altitude(rpm1, MP)
	pwr_FT2, DR_FT2 = _hp_at_MP_and_altitude(rpm2, MP)
	
	# density ratio at sea level
	DR_sl = 1
		
	# density ratio for the actual conditions (i.e. point D on the right side of the Lycoming power chart)
	DR_test = SA.alt2density_ratio(altitude)
	
	pwr_std_temp1 = pwr_SL1 + (DR_test - DR_sl) * (pwr_FT1 - pwr_SL1) / (DR_FT1 - DR_sl)
	pwr_std_temp2 = pwr_SL2 + (DR_test - DR_sl) * (pwr_FT2 - pwr_SL2) / (DR_FT2 - DR_sl)
	
	pwr_std_temp = pwr_std_temp1 + (rpm - rpm1) * (pwr_std_temp2 - pwr_std_temp1) / (rpm2 - rpm1)

	return pwr_std_temp


def pwr(rpm, MP, altitude, temp  = 'std', alt_units = 'ft', temp_units = 'C'):
	""" 
	Returns horsepower for Lycoming O-360-A series engines, given:
	rpm - engine speed in revolutions per minute
	MP - manifold pressure (" HG)
	altitude - pressure altitude
	temp - ambient temperature  (optional - std temperature is used if no 
	       temperature is input).
	alt_units - (optional) - units for altitude, ft, m, or km 
	                             (default is ft)
	temp_units - (optional) - units for temperature, C, F, K or R 
	                          (default is deg C)
	
	The function replicates Lycoming curve ??????? and is valid at mixture 
	for maximum power.
	
	Examples:
	
	Determine power at 2620 rpm, 28 inches HG manifold pressure, 0 ft, 
	and -10 deg C:
	>>> pwr(2620, 28, 0, -10)
	183.9148564247889
	
	Determine power at 2500 rpm, 25" MP, 5000 ft and 0 deg F:
	>>> pwr(2500, 25, 5000, 0, temp_units = 'F')
	164.10572738791328
	
	Determine power at 2200 rpm, 20" MP, 2000 metres and -5 deg C
	>>> pwr(2200, 20, 2000, -5, alt_units = 'm')
	111.72954664842844
	
	Determine power at 2200 rpm, 20" MP, 2000 metres and standard 
	temperature:
	>>> pwr(2200, 20, 2000, alt_units = 'm')
	110.29915330621547
	"""
	# convert units
	altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
	if temp == 'std':
		temp = SA.alt2temp(altitude, temp_units = temp_units)
	temp = U.temp_conv(temp, from_units = temp_units, to_units = 'K')
	
	# get standard temperature
	temp_std = SA.alt2temp(altitude, temp_units = 'K')
	
	# get power at standard temperature
	pwr_std = _pwr_std_temp(rpm, MP, altitude)
	
	# correct power for non-standard temperature
	pwr = pwr_std * M.sqrt(temp_std / temp)
	
	return pwr


def pp(rpm, MP, altitude, temp  = 'std', alt_units = 'ft', temp_units = 'C'):
	"""
	Returns percent power for Lycoming IO-360-A series engines, given:
	rpm - engine speed in revolutions per minute
	MP - manifold pressure (" HG)
	altitude - pressure altitude
	temp - ambient temperature  (optional - std temperature is used if no 
	       temperature is input).
	alt_units - (optional) - units for altitude, ft, m, or km 
	                             (default is ft)
	temp_units - (optional) - units for temperature, C, F, K or R 
	                          (default is deg C)
	
	The function replicates Lycoming curve 12700-A, and is valid at mixture 
	for maximum power.
	
	Note: the output is rounded off to two decimal places.
	
	Examples:
	
	Determine power at 2620 rpm, 28 inches HG manifold pressure, 0 ft, and 
	-10 deg C:
	>>> pp(2620, 28, 0, -10)
	'102.17%'
	
	Determine power at 2500 rpm, 25" MP, 5000 ft and 0 deg F:
	>>> pp(2500, 25, 5000, 0, temp_units = 'F')
	'91.17%'
	
	Determine power at 2200 rpm, 20" MP, 2000 metres and -5 deg C
	>>> pp(2200, 20, 2000, -5, alt_units = 'm')
	'62.07%'
	
	Determine power at 2200 rpm, 20" MP, 2000 metres and standard 
	temperature:
	>>> pp(2200, 20, 2000, alt_units = 'm')
	'61.28%'
	
	"""
	altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
	if temp == 'std':
		temp = SA.alt2temp(altitude, temp_units = temp_units)
	temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')

	pp = pwr(rpm, MP, altitude, temp) / 1.8
	
# 	return pp
	return '%.2f' % (pp) + '%'

def pwr2mp(pwr_seek, rpm, altitude, temp = 'std', alt_units = 'ft', temp_units = 'C'):
	""" 
	Returns manifold pressure in inches of mercury for a given power, rpm,
	altitude and temperature (temperature input is optional - standard 
	temperature is used if no temperature is input).
	
	Note: the output is rounded off to two decimal places.
	
	Examples:
	
	Determine manifold pressure required for 125 hp at 2550 rpm at 8000 ft 
	and 10 deg C:
	>>> pwr2mp(120, 2550, 8000, 10)
	'19.82'
	
	Determine manifold pressure required for 75% power at 2500 rpm at 
	7500 ft at 10 deg F:
	>>> pwr2mp(.75 * 180, 2500, 7500, 10, temp_units = 'F')
	'21.23'
	
	Determine manifold pressure required for 55% power at 2400 rpm at 
	9,500 ft at standard temperature:
	>>> pwr2mp(.55 * 180, 2400, 9500)
	'17.06'
	"""
	if pwr_seek <= 0:
		raise ValueError('Power input must be positive.')
	
	low = 0 # initial lower guess
	high = 35 # initial upper guess
	
	# convert units
	altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
	if temp == 'std':
		temp = SA.alt2temp(altitude, temp_units = temp_units)
	temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')
	
	# confirm initial low and high are OK:
	pwr_low = pwr(rpm, low, altitude, temp)
	if pwr_low > pwr_seek:
		raise ValueError('Initial low guess too high.')
	
	pwr_high = pwr(rpm, high, altitude, temp)
	if pwr_high < pwr_seek:
		raise ValueError('Initial high guess too low.')
	
	guess = (low + high) / 2.
	pwr_guess = pwr(rpm, guess, altitude, temp)
	
	# keep iterating until power is within 0.1% of desired value
	while M.fabs(pwr_guess - pwr_seek) / pwr_seek > 1e-3:
		if pwr_guess > pwr_seek:
			high = guess
		else:
			low = guess

		guess = (low + high) / 2.
		pwr_guess = pwr(rpm, guess, altitude, temp)

# 	result = int(guess) + round(guess % 1, 2))
# 	return guess
# 	return result
	return '%.2f' % (guess)



def pwr2rpm(pwr_seek, mp, altitude, temp = 'std', alt_units = 'ft', temp_units = 'C'):
	""" 
	Returns manifold pressure in inches of mercury for a given power, rpm,
	altitude and temperature (temperature input is optional - standard 
	temperature is used if no temperature is input).

	Note: the output is rounded off to the nearest rpm.
	
	Examples:
	
	Determine rpm required for 125 hp at 20 inches HG manifold pressure at 
	8000 ft and 10 deg C:
	>>> pwr2rpm(125, 20, 8000, 10)
	2674
	
	Determine rpm required for 75% power at 22 inches HG manifold pressure 
	at 6500 ft and 10 deg F:
	>>> pwr2rpm(.75 * 180, 22, 6500, 10, temp_units = 'F')
	2345
	
	Determine rpm required for 55% power at at 18 inches HG manifold 
	pressure at 9,500 ft at standard temperature:
	>>> pwr2rpm(.55 * 180, 18, 8500)
	2219
	"""
	if pwr_seek <= 0:
		raise ValueError('Power input must be positive.')
	
	low = 1000 # initial lower guess
	high = 3500 # initial upper guess
	
	# convert units
	altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
	if temp == 'std':
		temp = SA.alt2temp(altitude, temp_units = temp_units)
	temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')
# 	print 'Temp:',  temp
	
	# confirm initial low and high are OK:
	pwr_low = pwr(low, mp, altitude, temp)
	if pwr_low > pwr_seek:
		raise ValueError('Initial low guess too high.')
	
	pwr_high = pwr(high, mp, altitude, temp)
	if pwr_high < pwr_seek:
		raise ValueError('Initial high guess too low.')
	
	guess = (low + high) / 2.
# 	print 'Guess is:', guess
	pwr_guess = pwr(guess, mp, altitude, temp)
	
	# keep iterating until power is within 0.1% of desired value
	while M.fabs(pwr_guess - pwr_seek) / pwr_seek > 1e-4:
		if pwr_guess > pwr_seek:
			high = guess
		else:
			low = guess

		guess = (low + high) / 2.
		pwr_guess = pwr(guess, mp, altitude, temp)

	return int(round(guess,0))	


def pp2mp(percent_power, rpm, altitude, temp = 'std', alt_units = 'ft', temp_units = 'C'):
	"""
	Returns manifold pressure in inches of mercury for a given percent 
	power, rpm, altitude and temperature (temperature input is optional
	- standard temperature is used if no temperature is input).

	Note: the output is rounded off to two decimal places.
	
	Examples:
	
	Determine manifold pressure required for 62.5% power at 2550 rpm 
	at 8000 ft and 10 deg C:
	>>> pp2mp(62.5, 2550, 8000, 10)
	'18.90'
	
	Determine manifold pressure required for 75% power at 2500 rpm at 
	7500 ft at 10 deg F:
	>>> pp2mp(75, 2500, 7500, 10, temp_units = 'F')
	'21.23'
	
	
	Determine manifold pressure required for 55% power at 2400 rpm at 
	8,500 ft at standard temperature:
	>>> pp2mp(55, 2400, 8500)
	'17.26'
	"""
	if percent_power <= 0:
		raise ValueError('Power input must be positive.')
	
	# convert units
	altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
	if temp == 'std':
		temp = SA.alt2temp(altitude, temp_units = temp_units)
	temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')

	pwr_seek = percent_power * 1.8
	
	mp = pwr2mp(pwr_seek, rpm, altitude, temp)
	
	return mp


def pp2rpm(percent_power, mp, altitude, temp = 'std', alt_units = 'ft', temp_units = 'C'):
	"""
	Returns manifold pressure in inches of mercury for a given percent 
	power, rpm, altitude and temperature (temperature input is optional - 
	standard temperature is used if no temperature is input).
	
	Examples:
	
	Determine rpm required for 125 hp at 20 inches HG manifold pressure at 
	8000 ft and 10 deg C:
	>>> pp2rpm(62.5, 20, 8000, 10)
	2246
	
	Determine rpm required for 75% power at 22 inches HG manifold pressure 
	at 6500 ft and 10 deg F:
	>>> pp2rpm(75, 22, 6500, 10, temp_units = 'F')
	2345
	
	Determine rpm required for 55% power at at 18 inches HG manifold 
	pressure at 9,500 ft at standard temperature:
	>>> pp2rpm(55, 18, 8500)
	2219
	"""
	if percent_power <= 0:
		raise ValueError('Power input must be positive.')
	
	# convert units
	altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
	if temp == 'std':
		temp = SA.alt2temp(altitude, temp_units = temp_units)
	temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')

	pwr_seek = percent_power * 1.8
# 	print 'Temp:', temp
#	print('Power seeked:', pwr_seek)
	rpm = pwr2rpm(pwr_seek, mp, altitude, temp)
	
	return rpm


if __name__=='__main__':
#     from timeit import Timer
#     t1 = Timer("pwr(2555, 23.1, 4592, 5, temp_units = 'F')", "from __main__ import pwr")
#     print "pwr(2555, 23.1, 4592, 5):", t1.timeit(10000)

	# run doctest to check the validity of the examples in the doc strings.
	import doctest, sys
	doctest.testmod(sys.modules[__name__])
