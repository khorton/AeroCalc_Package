#! /usr/bin/env python

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

# version 0.2, 14 May 2006

# Version History:
# vers     date     Notes
#  0.1   14 May 06  First release.
#
#  0.2   16 May 06  Corrected errors in examples.  Added percent power functions
#                   pp, pp2mp and pp2rpm.  Changed pwr2mp and pwr2rpm functions 
#                   to round off results to two decimal places.


""" 
Calculate Lycoming IO-360-A series horsepower.

Replicates the power chart in the Lycoming Operators Manual.  The chart in
the operator's manual only goes down to 1800 rpm or manifold pressures down
to 12" HG, so powers for rpms less than 1800 or manifold pressures less than
12" HG are extrapolated.
"""

# TO DO:  1. Done
#
#         2. Done
#
#         3. Done
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
#         3. Validated to 15,000 ft, at various rpm, MP and temps.  Matches 
#            spreadsheet extremely closely.
#
#         4. Add function to determine the MP required to get a desired power,
#            given the other inputs.
#
#         5. Add function to determine the rpm required to get a desired power,
#            given the other inputs.
#
#         6. Does not work below 12".

# NOTES   1. Takes about 1.5e-5 sec per calculation on a 1.33 GHz PPC G4, so 
#            this should be suitable for every record in the FT data.

from __future__ import division
import math as M
import std_atm as SA
import unit_conversion as U


# def validate_rpm(rpm):
#   if rpm % 100 != 0:
#       raise ValueError, 'The rpm value in _pwr_sl must be a multiple of 100 rpm.'
#   
#   if rpm < 1800 or rpm > 2700:
#       raise ValueError, 'The rpm in _pwr_sl must be between 1800 and 2700.'


def _pwr_sl(N, MP):
    """ 
    Returns power at sea level, standard day.
    
    Validated against IO-360-A series spreadsheet.
    """
    
#   validate_rpm(N)
    
    if N == 2700:
        return 99.5 + (MP - 17) * (200 - 99.5) / (28.6 - 17)
        
    elif N >= 2600:
        return 94.1 + (MP - 17) * (193 - 94.1) / (28.65 - 17)
        
    elif N >= 2500:
        return 90. + (MP - 17) * (184 - 90.) / (28.7 - 17)
        
    elif N >= 2400:
        return 85. + (MP - 17) * (176 - 85.) / (28.75 - 17)

    elif N >= 2300:
        return 81. + (MP - 17) * (162 - 81.) / (28.1 - 17)

    elif N >= 2200:
        return 76. + (MP - 17) * (145.75 - 76) / (27.3 - 17)

    elif N >= 2100:
        return 72. + (MP - 17) * (136 - 72.) / (26.88 - 17)

    elif N >= 2000:
        return 67. + (MP - 17) * (121.8 - 67.) / (26.15 - 17)

    elif N >= 1900:
        return 61 + (MP - 17) * (109.5 - 61.) / (25.55 - 17)

    else:
        return 54 + (MP - 17) * (97.8 - 54) / (25. - 17)
    
DR_FT_alt = {1800 : {12 : 0.494158, 14 : 0.558577, 16 : 0.621062, 18 : 0.682183, 20 : 0.741962, 22 : 0.800721, 24 : 0.856458, 26 : 0.913750, 28 : 0.969634, 30 : 1.025111},
             1900 : {12 : 0.494909, 14 : 0.559403, 16 : 0.621957, 18 : 0.683035, 20 : 0.742871, 22 : 0.801684, 24 : 0.857914, 26 : 0.915116, 28 : 0.971064, 30 : 1.026603},
             2000 : {12 : 0.495679, 14 : 0.560247, 16 : 0.622873, 18 : 0.683888, 20 : 0.743781, 22 : 0.802648, 24 : 0.859347, 26 : 0.916484, 28 : 0.972495, 30 : 1.028096},
             2100 : {12 : 0.496432, 14 : 0.561074, 16 : 0.623770, 18 : 0.684741, 20 : 0.744691, 22 : 0.803613, 24 : 0.860807, 26 : 0.917853, 28 : 0.973928, 30 : 1.029591},
             2200 : {12 : 0.497203, 14 : 0.561921, 16 : 0.624688, 18 : 0.685596, 20 : 0.745602, 22 : 0.804579, 24 : 0.862243, 26 : 0.919224, 28 : 0.975363, 30 : 1.031088},
             2300 : {12 : 0.497957, 14 : 0.562750, 16 : 0.625587, 18 : 0.686429, 20 : 0.746491, 22 : 0.805521, 24 : 0.863707, 26 : 0.920597, 28 : 0.976799, 30 : 1.032587},
             2400 : {12 : 0.498730, 14 : 0.563599, 16 : 0.626507, 18 : 0.687286, 20 : 0.747404, 22 : 0.806489, 24 : 0.865147, 26 : 0.921971, 28 : 0.978237, 30 : 1.034087},
             2500 : {12 : 0.499487, 14 : 0.564429, 16 : 0.627408, 18 : 0.688143, 20 : 0.748318, 22 : 0.807457, 24 : 0.866614, 26 : 0.923347, 28 : 0.979676, 30 : 1.035589},
             2600 : {12 : 0.500262, 14 : 0.565280, 16 : 0.628330, 18 : 0.689000, 20 : 0.749232, 22 : 0.808427, 24 : 0.868058, 26 : 0.924724, 28 : 0.981118, 30 : 1.037093},
             2700 : {12 : 0.501020, 14 : 0.566113, 16 : 0.629233, 18 : 0.689859, 20 : 0.750148, 22 : 0.809397, 24 : 0.869529, 26 : 0.926103, 28 : 0.982560, 30 : 1.038598}}


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
# rpm at altitude   hp at sea level ALT2    density ratio at ALT2   hp at ALT2

HP_FT = {1800 : {'hp_sl' : 120.2, 'hp_23K' : 46},
         1900 : {'hp_sl' : 130,   'hp_23K' : 51.5},
         2000 : {'hp_sl' : 138.8, 'hp_23K' : 56},
         2100 : {'hp_sl' : 151,   'hp_23K' : 59.9},
         2200 : {'hp_sl' : 158,   'hp_23K' : 63.8},
         2300 : {'hp_sl' : 168,   'hp_23K' : 66.2},
         2400 : {'hp_sl' : 176,   'hp_23K' : 70.6},
         2500 : {'hp_sl' : 184,   'hp_23K' : 76},
         2600 : {'hp_sl' : 193,   'hp_23K' : 78.6},
         2700 : {'hp_sl' : 200,   'hp_23K' : 81.8}}

DR_23K = 0.480655 # density ratio at 23,000 ft

def _hp_at_FT(rpm, altitude):
    """ 
    Returns the horsepower at full throttle at a given rpm and altitude.
    """
    # get density ratio from the altitude
    DR = SA.alt2density_ratio(altitude)
    
    # get power at rpm
    hp_sl = HP_FT[rpm]['hp_sl']
    hp_23K = HP_FT[rpm]['hp_23K']
    hp_at_FT = hp_sl - (1 - DR) * (hp_sl - hp_23K) / (1 - DR_23K)
    
    return hp_at_FT


def _hp_at_MP_and_altitude(rpm, MP):
    """ 
    Returns the power and density ratio at a given rpm and MP at full throttle.
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
    
    Determine power at 2700 rpm, 28.6 inches HG manifold pressure and 
    0 ft altitude:
    >>> _pwr_std_temp(2700, 28.6, 0)
    200.0

    """
    # get the power at sea level (i.e. point B on the left side of the Lycoming power chart)
    
    # get pwr at two even hundreds of rpm, and then interpolate
    if rpm >= 2600:
        rpm1 = 2600
    elif rpm <= 1800:
        rpm1 = 1800
    else:
        rpm1 = rpm - rpm % 100

    rpm2 = rpm1 + 100
    
    pwr_SL1 = _pwr_sl(rpm1, MP)
    pwr_SL2 = _pwr_sl(rpm2, MP)
    # print "SL Pwr 1=", pwr_SL1
    # print "SL Pwr 2=", pwr_SL2
    
    # get power at full throttle at this rpm and MP at altitude (i.e. point A on the right side of the Lycoming power chart)
    # density ratio at point A on the right side of the Lycoming power chart)
    pwr_FT1, DR_FT1 = _hp_at_MP_and_altitude(rpm1, MP)
    pwr_FT2, DR_FT2 = _hp_at_MP_and_altitude(rpm2, MP)
    # print "FT pwr 1=", pwr_FT1
    # print "FT pwr 2=", pwr_FT2
    # print "DR FT 1=", DR_FT1
    # print "DR FT 2=", DR_FT2
    
    # density ratio at sea level
    DR_sl = 1
        
    # density ratio for the actual conditions (i.e. point D on the right side of the Lycoming power chart)
    DR_test = SA.alt2density_ratio(altitude)
    # print "DR_test=", DR_test
    
    # function is unstable if the DR at FT is close to 1.  This sends the slope off to unpredictable values.
    slope1=(pwr_FT1 - pwr_SL1) / (DR_FT1 - DR_sl)
    slope2=(pwr_FT2 - pwr_SL2) / (DR_FT2 - DR_sl)
    
    if MP > 28:
        if slope1 < -80:
            slope1=-62
        elif slope1> -60:
            slope1=-62
        if slope2< -80:
            slope2 = -62
        elif slope2> -60:
            slope2=-62
    
    # print "slope1=", slope1
    # print "slope2=", slope2
    
    pwr_std_temp1 = pwr_SL1 + (DR_test - DR_sl) * slope1
    pwr_std_temp2 = pwr_SL2 + (DR_test - DR_sl) * slope2
    # print "Pwr Std Temp 1=", pwr_std_temp1
    # print "Pwr Std Temp 2=", pwr_std_temp2
    pwr_std_temp = pwr_std_temp1 + (rpm - rpm1) * (pwr_std_temp2 - pwr_std_temp1) / (rpm2 - rpm1)

    return pwr_std_temp


def pwr(rpm, MP, altitude, temp  = 'std', alt_units = 'ft', temp_units = 'C'):
    """ 
    Returns horsepower for Lycoming IO-360-A series engines, given:
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
    
    Examples:
    
    Determine power at 2620 rpm, 28 inches HG manifold pressure, 0 ft, and 
    -10 deg C:
    >>> pwr(2620, 28, 0, -10)
    197.71751932574702
    
    Determine power at 2500 rpm, 25" MP, 5000 ft and 0 deg F:
    >>> pwr(2500, 25, 5000, 0, temp_units = 'F')
    171.87810350172663
    
    Determine power at 2200 rpm, 20" MP, 2000 metres and -5 deg C
    >>> pwr(2200, 20, 2000, -5, alt_units = 'm')
    108.60284092217333
    
    Determine power at 2200 rpm, 20" MP, 2000 metres and standard 
    temperature:
    >>> pwr(2200, 20, 2000, alt_units = 'm')
    107.2124765533882
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
    '98.86%'
    
    Determine power at 2500 rpm, 25" MP, 5000 ft and 0 deg F:
    >>> pp(2500, 25, 5000, 0, temp_units = 'F')
    '85.94%'
    
    Determine power at 2200 rpm, 20" MP, 2000 metres and -5 deg C
    >>> pp(2200, 20, 2000, -5, alt_units = 'm')
    '54.30%'
    
    Determine power at 2200 rpm, 20" MP, 2000 metres and standard 
    temperature:
    >>> pp(2200, 20, 2000, alt_units = 'm')
    '53.61%'
    
    """
    altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
    if temp == 'std':
        temp = SA.alt2temp(altitude, temp_units = temp_units)
    temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')

    pp = pwr(rpm, MP, altitude, temp) / 2
    
#   return pp
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
    >>> pwr2mp(125, 2550, 8000, 10)
    '19.45'
    
    Determine manifold pressure required for 75% power at 2500 rpm at 
    7500 ft at 10 deg F:
    >>> pwr2mp(.75 * 200, 2500, 7500, 10, temp_units = 'F')
    '22.25'
    
    
    Determine manifold pressure required for 55% power at 2400 rpm at 
    9,500 ft at standard temperature:
    >>> pwr2mp(.55 * 200, 2400, 9500)
    '18.18'
    """
    if pwr_seek <= 0:
        raise ValueError, 'Power input must be positive.'
    
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
        raise ValueError, 'Initial low guess too high.'
    
    pwr_high = pwr(rpm, high, altitude, temp)
    if pwr_high < pwr_seek:
        raise ValueError, 'Initial high guess too low.'
    
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

#   result = int(guess) + round(guess % 1, 2))
#   return guess
#   return result
    return '%.2f' % (guess)



def pwr2rpm(pwr_seek, mp, altitude, temp = 'std', alt_units = 'ft', temp_units = 'C'):
    """ 
    Returns rpm for a given power, manifold pressure in inches of mercury,
    altitude and temperature (temperature input is optional - standard 
    temperature is used if no temperature is input).

    Note: the output is rounded off to the nearest rpm.
    
    Examples:
    
    Determine rpm required for 125 hp at 20 inches HG manifold pressure at 
    8000 ft and 10 deg C:
    >>> pwr2rpm(125, 20, 8000, 10)
    2477
    
    Determine rpm required for 75% power at 22 inches HG manifold pressure 
    at 6500 ft and 10 deg F:
    >>> pwr2rpm(.75 * 200, 22, 6500, 10, temp_units = 'F')
    2547
    
    Determine rpm required for 55% power at at 18 inches HG manifold 
    pressure at 9,500 ft at standard temperature:
    >>> pwr2rpm(.55 * 200, 18, 9500)
    2423
    """
    if pwr_seek <= 0:
        raise ValueError, 'Power input must be positive.'
    
    low = 1000 # initial lower guess
    high = 3500 # initial upper guess
    
    # convert units
    altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
    if temp == 'std':
        temp = SA.alt2temp(altitude, temp_units = temp_units)
    temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')
    
    # confirm initial low and high are OK:
    pwr_low = pwr(low, mp, altitude, temp)
    # print "pwr_low=", pwr_low
    if pwr_low > pwr_seek:
        raise ValueError, 'Initial low guess too high.'
    
    pwr_high = pwr(high, mp, altitude, temp)
    # print "pwr_high=", pwr_high
    if pwr_high < pwr_seek:
        # print "pwr_high=", pwr_high
        print "Function called was IO.pwr(%f, %f, %f, %f)" % (high, mp, altitude, temp)
        raise ValueError, 'Initial high guess too low.'
    
    guess = (low + high) / 2.
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
    '19.45'
    
    Determine manifold pressure required for 75% power at 2500 rpm at 
    7500 ft at 10 deg F:
    >>> pp2mp(75, 2500, 7500, 10, temp_units = 'F')
    '22.25'
    
    
    Determine manifold pressure required for 55% power at 2400 rpm at 
    9,500 ft at standard temperature:
    >>> pp2mp(55, 2400, 9500)
    '18.18'
    """
    if percent_power <= 0:
        raise ValueError, 'Power input must be positive.'
    
    # convert units
    altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
    if temp == 'std':
        temp = SA.alt2temp(altitude, temp_units = temp_units)
    temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')

    pwr_seek = percent_power * 2
    
    mp = pwr2mp(pwr_seek, rpm, altitude, temp)
    
    return mp


def pp2rpm(percent_power, mp, altitude, temp = 'std', alt_units = 'ft', temp_units = 'C'):
    """
    Returns rpm for a given percent power, manifold pressure in inches of 
    mercury, altitude and temperature (temperature input is optional - 
    standard temperature is used if no temperature is input).
    
    Examples:
    
    Determine rpm required for 125 hp at 20 inches HG manifold pressure at 
    8000 ft and 10 deg C:
    >>> pp2rpm(62.5, 20, 8000, 10)
    2477
    
    Determine rpm required for 75% power at 22 inches HG manifold pressure 
    at 6500 ft and 10 deg F:
    >>> pp2rpm(75, 22, 6500, 10, temp_units = 'F')
    2547
    
    Determine rpm required for 55% power at at 18 inches HG manifold 
    pressure at 9,500 ft at standard temperature:
    >>> pp2rpm(55, 18, 9500)
    2423
    """
    if percent_power <= 0:
        raise ValueError, 'Power input must be positive.'
    
    # convert units
    altitude = U.length_conv(altitude, from_units = alt_units, to_units = 'ft')
    if temp == 'std':
        temp = SA.alt2temp(altitude, temp_units = temp_units)
    temp = U.temp_conv(temp, from_units = temp_units, to_units = 'C')

    pwr_seek = percent_power * 2
    
    rpm = pwr2rpm(pwr_seek, mp, altitude, temp)
    
    return rpm


def _pwr_ff_best_power(N, pwr):
    """ 
    Returns fuel flow at best power, in lb/h
    
    From Curve No. 12699B in Lycoming Operator's Manual
    """
    
#   validate_rpm(N)
    
    if N == 2700:
        return 53.3 + (pwr - 90) * (93.6 - 53.3) / (200. - 90.)
    elif N == 2600:
        return 51.2 + (pwr - 90) * (90. - 51.2) / (193.3 - 90.)
    elif N == 2400:
        return 49.7 + (pwr - 90) * (81.7 - 49.7) / (176.7 - 90.)
    elif N == 2200:
        return 47.6 + (pwr - 90) * (68.4 - 47.6) / (147.0 - 90.)
    elif N == 2000:
        return 45.9 + (pwr - 90) * (56.9 - 45.9) / (121.2 - 90)

def _pwr_ff_econ(N, pwr):
    """ 
    Returns fuel flow with mixture set for economy, in lb/h
    
    From Curve No. 12699B in Lycoming Operator's Manual
    """
    
#   validate_rpm(N)
    
    if N == 2700:
        return 44.9 + (pwr - 90) * (64.3 - 44.9) / (150 - 90.)
    elif N == 2600:
        return 43.7 + (pwr - 90) * (62.5 - 43.7) / (150 - 90.)
    elif N == 2400:
        return 41.8 + (pwr - 90) * (58.8 - 41.8) / (143 - 90.)
    elif N == 2200:
        return 40 + (pwr - 90) * (52.4 - 40) / (130 - 90.)
    elif N == 2000:
        return 38.6 + (pwr - 90) * (48.2 - 38.6) / (121.2 - 90)
    elif N == 1800:
        return 37.2 + (pwr - 90) * (40 - 37.2) / (98.2 - 90)

def pwr2ff(pwr, rpm, mixture = 'pwr', ff_units = 'gph'):
    """
    Returns fuel flow.  Defaults to mixture for best power ("pwr"), but may
    also be used with mixture for best economy ("econ").  Fuel flow units
    default to USG/hr, but pounds per hour ("lb/hr") and litres per hour 
    ("l/hr") may also be selected.
    """
    if mixture == 'pwr':
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
            rpm2 = 2200
        
        ff1 = _pwr_ff_best_power(rpm1, pwr)
        ff2 = _pwr_ff_best_power(rpm2, pwr)
    elif mixture == 'econ':
        if rpm >= 2600:
            rpm1 = 2600
            rpm2 = 2700
        elif rpm >= 2400:
            rpm1 = 2400
            rpm2 = 2600
        elif rpm >= 2200:
            rpm1 = 2200
            rpm2 = 2400
        elif rpm >= 2000:
            rpm1 = 2000
            rpm2 = 2200
        else:
            rpm1 = 1800
            rpm2 = 2000
        ff1 = _pwr_ff_econ(rpm1, pwr)
        ff2 = _pwr_ff_econ(rpm2, pwr)
    else:
        raise ValueError, 'mixture must be one of "econ" or "pwr"' 
        
#    else:
#        raise ValueError, 'Invalid value for mixture.'
        
    ff = ff1 + (ff2 - ff1) * (rpm - rpm1) / (rpm2 - rpm1)
    if ff_units == 'lb/hr':
        pass
    elif ff_units == 'gph':
        ff = U.avgas_conv(ff, to_units = 'USG')
    elif ff_units == 'l/hr':
        ff = U.avgas_conv(ff, to_units = 'l')
    else:
        raise ValueError, 'Invalid fuel flow units'
    
    return ff

    
if __name__=='__main__':
#     from timeit import Timer
#     t1 = Timer("pwr(2555, 23.1, 4592, 5, temp_units = 'F')", "from __main__ import pwr")
#     print "pwr(2555, 23.1, 4592, 5):", t1.timeit(10000)

    # run doctest to check the validity of the examples in the doc strings.
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
