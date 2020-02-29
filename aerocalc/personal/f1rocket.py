#! /usr/bin/env python3
"""
Various performance calculations for F-1 Rocket with EVO wing.

Based on the configuration of Tom Martin's aircraft, which has a
parallel valve O-540, with 10:1 compression ratio, and estimated
275 hp.

"""

##############################################################################
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
##############################################################################
#
# To Do: 1. tweak to match actual TAS data, when received from Tom Martin.
#
##############################################################################

import ft_data_reduction as F
import unit_conversion as U
import o360a as O
# import prop_map as PM
import airspeed as A
import math as M
import std_atm as SA
import string as S
import locale
locale.setlocale(locale.LC_ALL, 'en_CA')

def _pwr_error(eas_guess, altitude, weight, power, rpm, temp = 'std', \
    temp_units = 'C', rv = 'F1', wing_area = 102, speed_units = 'kt', \
    flap = 0, prop_eff=0.78):
    tas_guess = A.eas2tas(eas_guess, altitude, temp = temp, \
        speed_units = speed_units)
    tas_guess_fts = U.speed_conv(tas_guess, from_units = speed_units, \
        to_units = 'ft/s')
    power_avail = power * prop_eff

    drag = F.eas2drag(eas_guess, weight, wing_area, rv = rv, flap = flap,\
        speed_units = speed_units)
    power_req = tas_guess_fts * drag / 550.
    

    error = power_avail - power_req
    return error, tas_guess

def speed(altitude, weight, power, rpm, temp = 'std', temp_units = 'C', \
    rv = 'F1',  wing_area = 102, \
    speed_units = 'kt', flap = 0, prop_eff = 0.78):
    """
    Returns predicted speed in level flight.
    """

    eas_low = 60 # initial lower guess
    eas_high = 250 # initial upper guess
    

    error_low, tas_guess = _pwr_error(eas_low, altitude, weight, power, rpm, \
        temp = temp, temp_units = temp_units, rv = rv, wing_area = wing_area, \
        speed_units = speed_units, flap = 0)
    if error_low < 0:
        raise ValueError('Initial low quess too high')
    error_high, tas_guess = _pwr_error(eas_high, altitude, weight, power, rpm,\
        temp = temp, temp_units = temp_units, rv = rv, wing_area = 110, \
        speed_units = speed_units, flap = 0)
    if error_high > 0:
        raise ValueError('Initial high guess too low')
    eas_guess = (eas_low + eas_high) / 2.
    error_guess, tas_guess = _pwr_error(eas_guess, altitude, weight, power, \
        rpm, temp = temp, temp_units = temp_units, rv = rv, wing_area = 110, \
        speed_units = speed_units, flap = 0)
    # keep iterating until power is within 0.1% of desired value
    while M.fabs(error_guess)  > 0.1:
        if error_guess > 0:
            eas_low = eas_guess
        else:
            eas_high = eas_guess

        eas_guess = (eas_low + eas_high) / 2.
        error_guess, tas_guess = _pwr_error(eas_guess, altitude, weight, \
            power, rpm, temp = temp, temp_units = temp_units, rv = rv, \
            wing_area = 110, speed_units = speed_units, flap = 0)
    
    return tas_guess

def WOT_speed(altitude, weight = 2100, rpm = 2700, temp = 'std', \
    temp_units = 'C', rv = 'F1', wing_area = 102, speed_units = 'kt', \
    prop_eff = 0.78, MP_loss = 1.322, ram = 0.5, rated_power=275):
    """
    Returns the predicted speed at full throttle.
    
    The MP_loss is the MP lost in the induction tract at full throttle at 2700
    rpm at MSL.  The default value is from the Lycoming power charts.
    The ram is the percentage of available ram recovery pressure that is
    achieved in the MP.
    """
    press = SA.alt2press(altitude, press_units = 'in HG')
    MP_loss = MP_loss * (rpm / 2700.) ** 2
    cas_guess = 300
    error = 1
    while error > 0.0001:
        dp = A.cas2dp(cas_guess, press_units = 'in HG')
#       print 'dp =', dp
        ram_press = ram * dp
#       print 'Ram rise =', ram_press
        MP = press - MP_loss + ram_press
        pwr = O.pwr(rpm, MP, altitude, temp = temp, temp_units = temp_units) * rated_power/180
        print('MP =', MP, 'Power =', pwr)
        tas = speed(altitude, weight, pwr, rpm, temp = temp, \
            temp_units = temp_units, rv = rv, wing_area = wing_area, \
            speed_units = speed_units, prop_eff = prop_eff)
        cas = A.tas2cas(tas, altitude, temp = temp, temp_units = temp_units)
        error = M.fabs((cas - cas_guess) / cas)
        cas_guess = cas
#       print 'CAS =', cas, 'TAS =', tas
    return tas

def roc(altitude, eas, weight, power, rpm, temp = 'std', temp_units = 'C', \
    rv = 'F1',  wing_area = 102, speed_units = 'kt', flap = 0, \
    prop_eff = 0.7, load_factor = 1):
    """
    Returns the rate of climb or descent.
    """ 
    # PM.read_data_files_csv(base_name = prop)
    tas = A.eas2tas(eas, altitude, temp = temp, speed_units = speed_units)
    tas_fts = U.speed_conv(tas, from_units = speed_units, to_units = 'ft/s')
    # prop_eff = PM.prop_eff(power, rpm, tas, altitude, temp = temp, \
    #     temp_units = 'C', speed_units = speed_units)
    power_avail = power * prop_eff

    drag = F.eas2drag(eas, weight, wing_area, rv = rv, flap = flap, \
        speed_units = speed_units, load_factor = load_factor)
    power_req = tas_fts * drag / 550.

    excess_power = power_avail - power_req
    roc = excess_power * 33000 / weight

    return roc

def roca(altitude, weight = 2100, press_drop = 1.2, temp = 'std', \
    temp_units='C', prop_eff = 0.7, load_factor =1, rated_power=275, \
    rpm=2700):
    """
    Returns speed for best rate of climb and the rate of climb at that speed.
    """
    MP = SA.alt2press(altitude) - press_drop
    pwr = O.pwr(rpm, MP, altitude, temp = temp, temp_units = temp_units) * rated_power/180
    roc_max = -100000
    eass = list(range(60, 150, 1))
    rocs = []
    for eas in eass:
        rocs.append((roc(altitude, eas, weight, pwr, 2700, temp = temp, \
            prop_eff = prop_eff, load_factor = load_factor),eas))
    mroc, meas = max(rocs)
    return meas, mroc

def roc_sweep(start, end, interval, altitude, weight, power, rpm, \
    temp = 'std', temp_units = 'C', rv = 'F1', wing_area = 102, \
    speed_units = 'kt', flap = 0, prop_eff = 0.7, load_factor=1):
    """
    Calculates rate of climb over a range of speeds
    """
    for eas in range(start, end, interval):
        ROC = roc(altitude, eas, weight, power, rpm, temp = temp, \
            temp_units = temp_units, rv = rv, wing_area = wing_area, \
            speed_units = speed_units, flap = flap, prop_eff = prop_eff, \
            load_factor = load_factor)
        print('eas =', eas, speed_units, 'Rate of climb =', ROC, 'ft/mn')
    
