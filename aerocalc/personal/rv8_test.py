#! /usr/bin/env python
"""
Various performance calculations for RV-8.

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
# To Do: 1. climb_data - add line for MSL.
#
#        2. fix speed bug - provides bogus answer if prop_eff is returned as 
#                           'nan'
##############################################################################

from __future__ import division
import ft_data_reduction as FT
import unit_conversion as U
import io360a as IO
import prop_map as PM
import airspeed as A
import math as M
import std_atm as SA
import string as S
import locale
try:
    locale.setlocale(locale.LC_ALL, 'en_CA')
except:
    pass
# level flight test cases
# tas, density altitude, weight, rpm, mp, weighted value
level_test_cases = [(218.9,   597.0, 1772, 2752, 30.2, 0.3333),
              (220.0,   690.1, 1739, 2741, 29.9, 0.3333),
              (219.1,   651.4, 1812, 2780, 29.7, 0.3333),
              (211.6,  5838.5, 1791, 2760, 25.2, 1),
              (206.8,  8013.6, 1772, 2594, 23.4, 0.5),
              (195.3,  8075.0, 1761, 2299, 23.2, 0.5),
              (204.0, 12113.4, 1743, 2588, 19.2, 1),
              (195.8, 11945.2, 1683, 2304, 19.9, 1)]
              
def p(tas, dalt, wt, rpm, mp, prop):
    """
    test function for RV-8A drag, to compare against CAFE foundation level
    flt data.
    
    prop is a prop_map.Prop instance.
    """
    

    eas = A.tas2eas(tas, dalt, speed_units = 'mph')
#   tas = A.cas2tas(cas, dalt, speed_units = 'mph')
    tas_fts = U.speed_conv(tas, from_units = 'mph', to_units = 'ft/s')
    drag = FT.eas2drag(eas, wt, 110, rv = '8a', speed_units = 'mph')
    drag_power = drag * tas_fts / 550.
    power = IO.pwr(rpm, mp, dalt)
    prop_eff = PM.prop_eff(prop, power, rpm, tas, dalt, speed_units = 'mph')
    thrust_power = power * prop_eff
    excess_power = thrust_power - drag_power
    return excess_power

def run_tests(cd0 = 0.0221, e = 0.825):
    """
    Run all test cases to compare drag polar model against CAFE results.
    """
    sum_sq = 0
    wt_value_tot = 0
    wing_area = 110
    prop = PM.Prop('7666-4RV')
    for n, test in enumerate(level_test_cases):
        tas = test[0]
        dalt = test[1]
        wt = test[2]
        rpm = test[3]
        mp = test[4]
        wt_value = test[5]
    
        eas = A.tas2eas(tas, dalt, speed_units = 'mph')
        tas_fts = U.speed_conv(tas, from_units = 'mph', to_units = 'ft/s')
        cl = FT.eas2cl(eas, wt, wing_area, speed_units = 'mph')
        cd = FT.cl2cd_test(cl, cd0, e, flap = 0)
        drag = FT.cd2drag(cd, eas, wing_area, speed_units = 'mph')
        
        drag_power = drag * tas_fts / 550.
        power = IO.pwr(rpm, mp, dalt)
        prop_eff = PM.prop_eff(prop, power, rpm, tas, dalt, speed_units = 'mph')
        thrust_power = power * prop_eff
        excess_power = thrust_power - drag_power
        
        print 'Case', n, 'Altitude =', dalt, 'TAS =', tas, 'EAS =', eas, 'Excess power =', excess_power
        
        sum_sq += wt_value * excess_power ** 2
        wt_value_tot += wt_value
        
    print 'Average sum of squares of excess power =', \
        (sum_sq / wt_value_tot) ** 0.5

def _pwr_error(prop, eas_guess, altitude, weight, power, rpm, temp = 'std', \
    temp_units = 'C', rv = '8', wing_area = 110, speed_units = 'kt', \
    flap = 0, wheel_pants = 1):
    tas_guess = A.eas2tas(eas_guess, altitude, temp = temp, \
        speed_units = speed_units, temp_units = temp_units)
    tas_guess_fts = U.speed_conv(tas_guess, from_units = speed_units, \
        to_units = 'ft/s')
    prop_eff = PM.prop_eff(prop, power, rpm, tas_guess, altitude, temp = temp,\
        temp_units = temp_units, speed_units = speed_units)
    power_avail = power * prop_eff

    drag = FT.eas2drag(eas_guess, weight, wing_area, rv = rv, flap = flap,\
        speed_units = speed_units, wheel_pants = wheel_pants)
    power_req = tas_guess_fts * drag / 550.
    

    error = power_avail - power_req
    return error, tas_guess

def speed(prop, altitude, weight, power, rpm, temp = 'std', temp_units = 'C', \
    rv = '8',  wing_area = 110, \
    speed_units = 'kt', flap = 0, wheel_pants = 1):
    """
    Returns predicted speed in level flight.
    """
    # PM.read_data_files_csv(prop)
#   if prop == '7666-4RV':
#       dia = 72
#   elif prop == '7666-2RV':
#       dia = 74
#   else:
#       raise ValueError, 'Invalid prop'

    eas_low = 70 # initial lower guess
    eas_high = 250 # initial upper guess
    

    error_low, tas_guess = _pwr_error(prop, eas_low, altitude, weight, power, rpm, \
        temp = temp, temp_units = temp_units, rv = rv, wing_area = wing_area, \
        speed_units = speed_units, flap = 0, wheel_pants = wheel_pants)
    if error_low < 0:
        raise ValueError, 'Initial low guess too high'
    error_high, tas_guess = _pwr_error(prop, eas_high, altitude, weight, power, rpm,\
        temp = temp, temp_units = temp_units, rv = rv, wing_area = wing_area, \
        speed_units = speed_units, flap = 0, wheel_pants = wheel_pants)
    if error_high > 0:
        raise ValueError, 'Initial high guess too low'
    eas_guess = (eas_low + eas_high) / 2.
    error_guess, tas_guess = _pwr_error(prop, eas_guess, altitude, weight, power, \
        rpm, temp = temp, temp_units = temp_units, rv = rv, wing_area = wing_area, \
        speed_units = speed_units, flap = 0, wheel_pants = wheel_pants)
    # keep iterating until power is within 0.1% of desired value
    while M.fabs(error_guess)  > 0.05:
        if error_guess > 0:
            eas_low = eas_guess
        else:
            eas_high = eas_guess

        eas_guess = (eas_low + eas_high) / 2.
        error_guess, tas_guess = _pwr_error(prop, eas_guess, altitude, weight, \
            power, rpm, temp = temp, temp_units = temp_units, rv = rv, \
            wing_area = wing_area, speed_units = speed_units, flap = 0, \
            wheel_pants = wheel_pants)
    
    return tas_guess

def WOT_speed_orig(prop, altitude, weight = 1800, rpm = 2700, temp = 'std', \
    temp_units = 'C', rv = '8', wing_area = 110, speed_units = 'kt' , \
    MP_loss = 1.322, ram = 0.5, pwr_factor=1, mixture='pwr', \
    wheel_pants=1):
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
    if mixture == 'econ':
        pwr_factor *= .86 # average power ratio to max power when at 50 deg LOP mixture
    elif mixture == 'pwr':
        pass
    else:
        raise ValueError, 'mixture must be one of "pwr" or "econ"'
    while error > 0.0001:
        dp = A.cas2dp(cas_guess, press_units = 'in HG')
#       print 'dp =', dp
        ram_press = ram * dp
#       print 'Ram rise =', ram_press
        MP = press - MP_loss + ram_press
        pwr = IO.pwr(rpm, MP, altitude, temp = temp, temp_units = temp_units) * pwr_factor
        # print 'MP =', MP, 'Power =', pwr
        tas = speed(prop, altitude, weight, pwr, rpm, temp = temp, \
            temp_units = temp_units, rv = rv, wing_area = wing_area, \
            speed_units = speed_units, wheel_pants = wheel_pants)
        cas = A.tas2cas(tas, altitude, temp = temp, temp_units = temp_units)
        error = M.fabs((cas - cas_guess) / cas)
        cas_guess = cas
#       print 'CAS =', cas, 'TAS =', tas
#    print "MP = %.3f" % MP
#    print "Pwr = %.2f" % pwr
    return tas

def WOT_speed(engine, prop, altitude, weight = 1800, rpm = 2700, temp = 'std', \
    temp_units = 'C', rv = '8', wing_area = 110, speed_units = 'kt' , \
    MP_loss = 1.322, ram = 0.5, pwr_factor=0.92, mixture='pwr', wheel_pants=1):
    """
    Returns the predicted speed at full throttle.
    
    The MP_loss is the MP lost in the induction tract at full throttle at 2700
    rpm at MSL.  The default value is from the Lycoming power charts.
    The ram is the percentage of available ram recovery pressure that is
    achieved in the MP.
    """
    tas_guess = 300
    error = 1
    if mixture == 'econ':
        pwr_factor *= .86 # average power ratio to max power when at 50 deg LOP mixture
    elif mixture == 'pwr':
        pass
    else:
        raise ValueError, 'mixture must be one of "pwr" or "econ"'
    while error > 0.0001:
        MP = MP_pred(tas_guess, altitude, rpm, rpm_base = 2700., MP_loss = 1.322, ram = 0.5, temp='std')
        pwr = engine.pwr(rpm, MP, altitude, temp = temp, temp_units = temp_units) * pwr_factor
        # print 'MP =', MP, 'Power =', pwr
        tas = speed(prop, altitude, weight, pwr, rpm, temp = temp, \
            temp_units = temp_units, rv = rv, wing_area = wing_area, \
            speed_units = speed_units, wheel_pants = wheel_pants)
        error = M.fabs((tas - tas_guess) / tas)
        tas_guess = tas
#       print 'CAS =', cas, 'TAS =', tas
#    print "MP = %.3f" % MP
#    print "Pwr = %.2f" % pwr
    return tas, pwr / pwr_factor

def MP_pred(tas, alt, rpm, rpm_base = 2700., MP_loss = 1.322, ram = 0.5, temp='std'):
    press = SA.alt2press(alt, press_units = 'in HG')
    if temp == 'std':
        temp = SA.alt2temp(alt)
    dp = A.tas2dp(tas, alt, temp, speed_units='kt', alt_units='ft', temp_units='C', press_units='in HG')
    ram_press = ram * dp
    MP_loss = MP_loss * (rpm / rpm_base) ** 1.85 # exponent from various online pressure drop calculators
#    MP_loss = MP_loss * (rpm / rpm_base)
    MP = press - MP_loss + ram_press

#    print "MP = %.3f" % MP
    return MP

def tas2rpm(tas, engine, prop, blade_angle, alt, temp='std', alt_units = 'ft', temp_units = 'C', speed_units = 'kt', rpm_base = 2700., MP_loss = 1.322, ram = 0.5, MP='WOT'):
    """
    Return rpm where engine power equals power absorbed by prop, at a specified MP or at wide open throttle.
    """
    rpm_low = 1500.
    rpm_high = 2900.
    pwr_threshold = .1
    rpm_threshold = .25
    while 1:
        rpm_guess = (rpm_low + rpm_high) / 2.
        prop_power = PM.blade_angle2bhp(prop, blade_angle, rpm_guess, tas, alt, temp=temp, power_units = 'hp', alt_units = alt_units, temp_units = temp_units, speed_units = speed_units)
        if MP == 'WOT':
            MP = MP_pred(tas, alt, rpm_guess, rpm_base = rpm_base, MP_loss = MP_loss, ram = ram, temp=temp)
        engine_power = engine.pwr(rpm_guess, MP, alt, temp=temp, alt_units=alt_units, temp_units=temp_units)
        if M.fabs(engine_power - prop_power) < pwr_threshold or rpm_high - rpm_low < rpm_threshold:
            return rpm_guess
        
        if engine_power > prop_power:
            rpm_low = rpm_guess
        else:
            rpm_high = rpm_guess

def alt2FP_speed(engine, prop, blade_angle, alt, weight = 1800, temp = 'std', \
    temp_units = 'C', rv = '8', wing_area = 110, alt_units='ft', speed_units = 'kt' , \
    MP_loss = 1.322, ram = 0.5, pwr_factor=1, mixture='pwr', MP='WOT', wheel_pants=1):
    """
    Returns the predicted speed at full throttle for aircraft with fixed pitch prop.
    
    The MP_loss is the MP lost in the induction tract at full throttle at 2700
    rpm at MSL.  The default value is from the Lycoming power charts.
    The ram is the percentage of available ram recovery pressure that is
    achieved in the MP.
    """
    
    tas_low = 80
    tas_high = 250
    pwr_tolerance = .1
    
    while 1:
        tas_guess = (tas_low + tas_high) / 2.
        tas_guess_fts = U.speed_conv(tas_guess, from_units = speed_units, to_units = 'ft/s')
        rpm = tas2rpm(tas_guess, engine, prop, blade_angle, alt, temp=temp, alt_units=alt_units, temp_units=temp_units, speed_units=speed_units, MP=MP)
        if MP == 'WOT':
            MP = MP_pred(tas_guess, alt, rpm, rpm_base = 2700., MP_loss = MP_loss, ram = ram, temp=temp)
        bhp = engine.pwr(rpm, MP, alt, temp=temp, alt_units=alt_units, temp_units=temp_units)
        prop_eff = PM.prop_eff(prop, bhp, rpm, tas_guess, alt, temp = temp, temp_units = temp_units, speed_units = speed_units)
        power_avail = bhp * prop_eff
        eas_guess = A.tas2eas(tas_guess, alt, temp)
        drag = FT.eas2drag(eas_guess, weight, wing_area, rv = rv, flap = 0, speed_units = speed_units, wheel_pants = wheel_pants)
        power_req = tas_guess_fts * drag / 550.
        
        if M.fabs(power_avail - power_req) < pwr_tolerance:
#            print "MP = %.3f" % MP
#            print "Pwr = %.2f"% bhp 
#            print "Prop Efficiency = %.3f, and power available = %.1f thp" % (prop_eff, power_avail)
            return tas_guess, rpm, bhp
        
        if power_req > power_avail:
            tas_high = tas_guess
        else:
            tas_low = tas_guess
    
def FP_pwr2speed(pwr, engine, prop, blade_angle, alt, weight = 1800, temp = 'std', \
    temp_units = 'C', rv = '8', wing_area = 110, alt_units='ft', speed_units = 'kt' , \
    pwr_factor=1, mixture='pwr', wheel_pants = 1):
    """
    Return TAS, rpm and MP for a given power for an aircraft with fixed pitch prop.
    """
    MP_low = 10
    MP_high = 31
    pwr_tolerance = 0.04

    while 1:
        WOT = False
        MP_guess = (MP_low + MP_high) / 2.
        tas, rpm, bhp = alt2FP_speed(engine, prop, blade_angle, alt, weight=weight, temp = temp, \
        temp_units = temp_units, rv = rv, wing_area = wing_area, alt_units=alt_units, speed_units = speed_units , \
        MP_loss = 1.322, ram = 0.5, pwr_factor=1, mixture='pwr', MP=MP_guess, wheel_pants = wheel_pants)
#        print "MP guess=%.2f, tas=%.1f, rpm=%.0f, pwr=%.2f" % (MP_guess, tas, rpm, bhp)
        if M.fabs(bhp - pwr) < pwr_tolerance:
            MP_max = MP_pred(tas, alt, rpm, rpm_base = 2700., MP_loss = 1.322, ram = 0.5, temp='std')
            if MP_guess > MP_max:
                WOT = True
                tas, rpm, bhp = alt2FP_speed(engine, prop, blade_angle, alt, weight = weight, temp = temp, \
                temp_units = temp_units, rv = rv, wing_area = wing_area, alt_units=alt_units, speed_units = speed_units , \
                MP_loss = 1.322, ram = 0.5, pwr_factor=1, mixture='pwr', MP='WOT', wheel_pants = wheel_pants)
                MP_guess = MP_max
            return tas, rpm, MP_guess, bhp, WOT
    
        if bhp > pwr:
            MP_high = MP_guess
        else:
            MP_low = MP_guess
        
    
def cafe_speed():
    """
    Check the calculated speeds against the data from the CAFE tests for the RV-8A
    """
    prop = PM.Prop('7666-4RV')
    for n, test in enumerate(level_test_cases):
        tas = test[0]
        dalt = test[1]
        wt = test[2]
        rpm = test[3]
        mp = test[4]
        wt_value = test[5]
    
        eas = A.tas2eas(tas, dalt, speed_units = 'mph')
        calc_tas = speed(prop, dalt, wt, IO.pwr(rpm, mp, dalt), rpm, \
            speed_units = 'mph')
        print 'Actual TAS =', tas, 'Calc TAS =', calc_tas

def prop_test_cases():
    speed_units = 'mph'
    rvs = ['6', '8a', '8']
    props = [PM.Prop('7666-4RV'), PM.Prop('7666-2RV'), PM.Prop('MTV-12-B-183-59B')]
    level_tests = [(0, 2700, 210),
                    (8000, 2700, 160),
                    (8000, 2600, 150),
                    (8000, 2400, 130),
                    (8000, 2300, 110)]
                    
    for prop in props:
        print 'Prop =', prop.model
#       if prop == '7666-4RV':
#           dia = 72
#       elif prop == '7666-2RV':
#           dia = 74
#       else:
#           raise ValueError, 'Invalid prop'
        # PM.read_data_files_csv(base_name = prop)
        for rv in rvs:
            print 'RV model =', rv
            for test in level_tests:
                alt = test[0]
                rpm = test[1]
                power = test[2]
                tas = speed(prop, alt, 1800, power, rpm, prop = prop, rv = rv, \
                    speed_units = speed_units)
                print 'Alt =', alt, 'Power =', power, 'Speed =', tas, \
                    speed_units, 'TAS'

def roc(prop, altitude, eas, weight, power, rpm, temp = 'std', temp_units = 'C', \
    rv = '8',  wing_area = 110, speed_units = 'kt', flap = 0, \
    load_factor = 1, wheel_pants = 1, prop_factor=1):
    """
    Returns the rate of climb or descent.
    """ 
    # PM.read_data_files_csv(base_name = prop)
    tas = A.eas2tas(eas, altitude, temp = temp, speed_units = speed_units)
    tas_fts = U.speed_conv(tas, from_units = speed_units, to_units = 'ft/s')
    prop_eff = PM.prop_eff(prop, power, rpm, tas, altitude, temp = temp, \
        temp_units = 'C', speed_units = speed_units) * prop_factor
    power_avail = power * prop_eff

    drag = FT.eas2drag(eas, weight, wing_area, rv = rv, flap = flap, \
        speed_units = speed_units, load_factor = load_factor, wheel_pants = wheel_pants)
    power_req = tas_fts * drag / 550.
    
    excess_power = power_avail - power_req
    roc = excess_power * 33000 / weight

    return roc

def roca(prop, altitude, weight = 1800, press_drop = 1.2, temp = 'std', \
    load_factor =1, prop_factor=1):
    """
    Returns speed for best rate of climb and the rate of climb at that speed.
    """
    MP = SA.alt2press(altitude) - press_drop
    pwr = IO.pwr(2700, MP, altitude, temp = temp)
    roc_max = -100000
    eass = range(600, 1500, 1)
    rocs = []
    for eas in eass:
        rocs.append((roc(prop, altitude, eas/10., weight, pwr, 2700, temp = temp, \
            load_factor = load_factor, prop_factor=prop_factor),eas/10.))
    mroc, meas = max(rocs)
    return meas, mroc

def aoc(prop, altitude, eas, weight, power, rpm, temp = 'std', temp_units = 'C', \
    rv = '8', wing_area = 110, speed_units = 'kt', flap = 0):
    """
    Returns the climb or descent gradient.

    Runs with zero power at 1800 lb show best glide speed for RV-8 of:
    98 kt at 1800 lb
    86 kt at 1400 lb
    
    best angle of climb:
    66 kt at 1800 lb
    """ 
    tas = A.eas2tas(eas, altitude, temp = temp, speed_units = speed_units)
    tas_fts = U.speed_conv(tas, from_units = speed_units, to_units = 'ft/s')
    prop_eff = PM.prop_eff(prop, power, rpm, tas, altitude, temp = temp, \
        temp_units = 'C', speed_units = speed_units)
    power_avail = power * prop_eff

    drag = FT.eas2drag(eas, weight, wing_area, rv = rv, flap = flap, \
        speed_units = speed_units)
    power_req = tas_fts * drag / 550.
    
    excess_power = power_avail - power_req
    roc = excess_power * 550 / weight
    gradient = roc / tas_fts
    return gradient

def aoca(prop, altitude, weight = 1800, press_drop = 1.2, temp = 'std', \
    climb = True):
    """
    Returns speed for best climb or descent gradient and the gradient at 
    that speed.
    """
    MP = SA.alt2press(altitude) - press_drop
    pwr = IO.pwr(2700, MP, altitude, temp = temp)

    if climb == True:
        eass = range(550, 800, 1)
    else:
        eass = range(700, 1200, 1)
    aocs = []
    if climb == True:
        for eas in eass:
            aocs.append((aoc(prop, altitude, eas/10., weight, pwr, 2700, temp = temp),eas))
    else:
        for eas in eass:
            aocs.append((aoc(prop, altitude, eas/10., weight, 0, 2700, temp = temp),eas))
    maoc, meas = max(aocs)
    return meas/10., maoc

def roc_sweep(prop, start, end, interval, altitude, weight, power, rpm, \
    temp = 'std', temp_units = 'C', rv = '8', wing_area = 110, \
    speed_units = 'kt', flap = 0, load_factor=1):
    """
    Calculates rate of climb over a range of speeds
    """
    for eas in range(start, end, interval):
        ROC = roc(prop, altitude, eas, weight, power, rpm, temp = temp, \
            temp_units = temp_units, rv = rv, wing_area = 110, \
            speed_units = speed_units, flap = 0, load_factor = load_factor)
        # print 'eas =', eas, speed_units, 'Rate of climb =', ROC, 'ft/mn'
        print 'eas = %.0f %s Rate of climb = %.0f ft/mn' % (eas, speed_units, ROC)
    
def pwr_vs_alt_temp(temps):
    """
    Returns a series of powers at full throttle and 2700 rpm at various temps
    
0 ft
-20     0       20      40      ISA
213.4   205.4   198.3   191.9   200.0 

2000 ft
-20     0       20      40      ISA
197.3   189.9   183.3   177.4   186.2 

4000 ft
-20     0       20      40      ISA
182.4   175.6   169.5   164.0   173.4 

6000 ft
-20     0       20      40      ISA
167.8   161.5   155.9   150.9   160.6 

8000 ft
-20     0       20      40      ISA
154.1   148.3   143.2   138.6   148.6 

10000 ft
-20     0       20      40      ISA
141.3   136.1   131.3   127.1   137.3 

12000 ft
-20     0       20      40      ISA
129.3   124.5   120.2   116.3   126.6 

14000 ft
-20     0       20      40      ISA
118.2   113.8   109.8   106.2   116.5 

16000 ft
-20     0       20      40      ISA
107.4   103.4   99.8    96.6    106.7 

18000 ft
-20     0       20      40      ISA
97.3    93.7    90.4    87.5    97.4 

20000 ft
-20     0       20      40      ISA
87.7    84.4    81.5    78.9    88.5 

    """
    alts = range(0,22000, 2000)
    for alt in alts:
        print alt, 'ft'
        for temp in temps:
            print temp, '\t',
        print 'ISA'
        for temp in temps:
            power = alt2pwr(alt, temp = temp)
            print '%.1f' % (power), '\t',
        press = SA.alt2press(alt)
        MP = press - (29.9213 - 28.6)
        isa_pwr = IO.pwr(2700, MP, alt)
        print '%.1f' % (isa_pwr), '\n'

def alt2pwr(alt, rpm = 2700, MP_max = 30, temp  = 'std', alt_units = 'ft', \
    temp_units = 'C'):
    """
    Returns power at a given altitude.  Default rpm is 2700.
    The maximum MP may be specified, if for example, one 
    wanted to use 25 inches MP until full throttle was reached.
    """
    # MP loss at full throttle at 2700 rpm at sea level.  
    # From Lycoming power chart
    MP_loss_base = 29.9213 - 28.6
    press = SA.alt2press(alt, alt_units = alt_units)
    # assume pressure drop is proportional to square of velocity
    MP_loss = MP_loss_base * (rpm / 2700.) ** 2
    MP = min(press - MP_loss, MP_max)
    # from climb testing, get MP of 0.5 above ambient
    # get 2650 rpm during climb
    MP = SA.alt2press(alt) + 0.5 * (2650./rpm) ** 2
    pwr = IO.pwr(rpm, MP, alt, temp = temp, alt_units = alt_units, \
        temp_units = temp_units)
    # decrement power as a function of altitude to make predicted climb perf match flight test resutls
    # this decrement is optimized for the MT prop
    pwr = pwr * (0.8525  - 4.35E-10 * alt**2)
    return pwr

def roc_vs_temp(prop, alt_max = 20000, alt_interval=2000, weight=1800, temps=[-20,0,20,40], pwr='max', \
    pwr_factor=1.0, climb_speed='max', output='raw'):
    """
    Returns the rates of climb at various temperatures
    """
    if pwr == 'max':
        rpm = 2650
        MP_max = 30
    elif pwr == 'cc':
        rpm = 2500
        MP_max = 25
    elif pwr == 2500:
        rpm = 2500
        MP_max = 30
    else:
        raise ValueError, "pwr must be on of 'max', 'cc', or 2500"

    alt = 0
    while alt<alt_max:
        press = SA.alt2press(alt)
        MP = press - (29.9213 - 28.6)

        cas = alt2roc_speed(alt, climb_speed = climb_speed)
        eas = A.cas2eas(cas, alt)

#        for temp  in temps:
#            print temp, '\t\t\t',
#        print '\n',
        print '%.0f\t%.0f\t%.0f\t' % (weight, alt, cas),
        for temp in temps:
            # power = IO.pwr(rpm, MP, alt, temp) * pwr_factor
            power = alt2pwr(alt, rpm = rpm, MP_max = MP_max, temp = temp)
            ROC = roc(prop, alt, eas, weight, power, rpm, temp) /10
            ROC = int('%.0f' % (ROC)) * 10
            print '%.0f\t' % (ROC), 
        print '\n'
        alt += alt_interval

def aoc_sweep(prop, start, end, interval, altitude, weight, power, rpm, \
    temp = 'std', temp_units = 'C', rv = '8', wing_area = 110, \
    speed_units = 'kt', flap = 0):
    
    """
    Calculates climb gradient over a range of speeds
    """
    for eas in range(start, end, interval):
        AOC = aoc(prop, altitude, eas, weight, power, rpm, temp = temp, \
            temp_units = temp_units, rv = rv,  wing_area = 110, \
            speed_units = speed_units, flap = 0)
        print 'eas =', eas, 'Climb gradient', AOC

def plot_roc_vs_speed(prop, start, end, interval, altitude, weight, power, rpm, \
    temp = 'std', temp_units = 'C', rv = '8',  wing_area = 110, \
    speed_units = 'kt', flap = 0):
    
    """
    Creates matplotlib plot of rate of climb vs speed.
    """
    import matplotlib
    import pylab
    EAS = pylab.arange(start, end, interval)
    ROC = []
    for speed in EAS:
        ROC.append(R.roc(prop, altitude, speed, weight, power, rpm, temp, \
            temp_units, rv, wing_area, speed_units, flap))
    p = matplotlib.plot(EAS, ROC)
    p.show()

def alt2roc_speed(alt, climb_speed = 'max'):
    """
    Returns a climb speed (KCAS) as a function of altitude, and 
    climb profile.  The default climb profile is the one that gives
    the approximately the best rate of climb at 1800 lb under ISA conditions.
    A climb speed of 100 kt at sea level, reducing by one kt per thousand feet
    gives an ROC within 1% of the max all the way to 20,000 ft.
    
    There is an alternative cruise-climb profile.
    """
    if climb_speed == 'max':
        roc_speed = 102 - (alt/1000.)
    elif climb_speed == 'cc':
        if alt < 10000:
            roc_speed = 120
        else:
            roc_speed = 120 - ((alt - 10000)/250.)
    elif climb_speed == 'norm':
        if alt < 10000:
            roc_speed = 100
        else:
            roc_speed = 100 - ((alt - 10000)/500.)
    else:
        raise ValueError, 'Invalid climb profile'
        
    return roc_speed
    
def climb_data(prop, weight = 1800., alt_max = 20000., TO_fuel = 0, TO_dist = 0, \
    fuel_units = 'USG', alt_interval = 500., isa_dev = 0, temp_units = 'C', \
    rv = '8', wing_area = 110., pwr = 'max', pwr_factor=1.0, \
    climb_speed = 'max', output = 'raw'):
    """
    Returns a table of climb performance vs altitude.

    The items in each row of the table are altitude, time, fuel burned and distance.
    Time is in units of minutes, rounded to the nearest half minute.
    Fuel units are selectable, with a default of USG.
    Distances are in nm.
    
    The output may be specified as raw, latex (a LaTeX table for the POH), or array.
    
    pwr may be 'max', 'cc' (cruise climb = 2500 rpm and 25") or 2500 (2500 rpm and full throttle)
    climb_speed may be 'max' (Vy), 'cc' (120 kt to 10,000 ft, then reducing by 4 kt/1000 ft) or
                'norm' (100 kt to 10,000 ft, then reducing by 2 kt/1000 ft)
                
    Note: compared cruise range for all climb speed and power.  The predicted results are all 
          within 1.5 nm of range.  Thus there is no advantage to using anything but Vy and max
          power.
    """
    def _alt2ROC(prop, alt):
        """
        calculate ROC for an altitude
        """
        temp = SA.isa2temp(isa_dev, alt)
        calc_pwr = alt2pwr(alt, rpm = rpm, MP_max = MP_max, temp = temp) * pwr_factor
        cas = alt2roc_speed(alt, climb_speed = climb_speed)
        eas = A.cas2eas(cas, alt)
        ROC = roc(prop, alt, eas, weight, calc_pwr, rpm, rv = rv, \
            wing_area = wing_area)
        
        return ROC
    
    alt = 0
    time = 0
    fuel_used = U.avgas_conv(TO_fuel, from_units = fuel_units, to_units = 'lb')
    weight = weight - fuel_used
    dist = TO_dist
    if pwr == 'max':
        # rpm = 2700
        rpm = 2650
        MP_max = 30
    elif pwr == 'cc':
        rpm = 2500
        MP_max = 25
    elif pwr == 2500:
        rpm = 2500
        MP_max = 30
    else:
        raise ValueError, "pwr must be one of 'max', 'cc', or 2500"
    

    if output == 'raw':
        print S.center('Altitude', 10),
        print S.center('ROC', 10),
        print S.center('Time', 10),
        print S.center('Fuel Used', 10),
        print S.center('Dist', 10),
        print S.center('Speed', 10)
        
        print S.center('(ft)', 10),
        print S.center('(ft/mn)', 10),
        print S.center('(mn)', 10),
        f_units = '(' + fuel_units + ')'
        print S.center(f_units, 10),
        print S.center('(nm)', 10),
        print S.center('(KCAS)', 10)
        
        # data for MSL
        print S.rjust(locale.format('%.0f', 0, True), 7),
        # calculate ROC at MSL
        print S.rjust(locale.format('%.0f', round(_alt2ROC(prop, 0) / 10.) * 10, \
            True), 10),
        print S.rjust('%.1f' % (0), 10),
        print S.rjust('%.1f' % (TO_fuel), 10),
        print S.rjust('%.1f' % (TO_dist), 10),
        print S.rjust('%3d' % (alt2roc_speed(0, climb_speed = climb_speed)), 10)

    elif output == 'latex':
        temp = 15 + isa_dev
        MSL_line = []
        MSL_line.append(str(locale.format('%.0f', weight, True)))
        MSL_line.append('0')
        MSL_line.append(str(locale.format('%.0f', temp)))
        MSL_line.append(str(locale.format('%.0f', alt2roc_speed(0, \
            climb_speed = climb_speed))))
        MSL_line.append(str(locale.format('%.0f', round(_alt2ROC(prop, 0) / 10.)\
          * 10, True)))
        MSL_line.append('0')
        MSL_line.append(str(TO_fuel))
        MSL_line.append(str(TO_dist))
        
        print '&'.join(MSL_line) + '\\\\'
        print '\\hline'
    elif output == 'array':
        # no header rows, but make blank array
        array = [[0,0,TO_fuel,0]]
        
    calc_alt = alt_interval / 2.
    while calc_alt < alt_max:
        temp = SA.isa2temp(isa_dev, calc_alt)
        pwr = alt2pwr(calc_alt, rpm = rpm, MP_max = MP_max, temp = temp)
        calc_pwr = pwr * pwr_factor
        cas = alt2roc_speed(calc_alt, climb_speed = climb_speed)
        eas = A.cas2eas(cas, calc_alt)
        tas = A.cas2tas(cas, calc_alt, temp = temp, temp_units = temp_units)
        tas_fts = U.speed_conv(tas, from_units = 'kt', to_units = 'ft/s')
        ROC = roc(prop, calc_alt, eas, weight, calc_pwr, rpm, rv = rv, \
            wing_area = wing_area)
        roc_fts = ROC / 60
        fuel_flow = IO.pwr2ff(pwr, rpm, ff_units = 'lb/hr')
        slice_time = alt_interval / roc_fts
        slice_dist = tas_fts * slice_time
        slice_fuel = fuel_flow * slice_time / 3600
        fuel_used += slice_fuel
        fuel_out = (U.avgas_conv(fuel_used, from_units = 'lb', \
            to_units = fuel_units))
        weight -= slice_fuel
        alt += alt_interval
        cas_out = alt2roc_speed(alt, climb_speed = climb_speed)
        temp_out = SA.isa2temp(isa_dev, alt)
        ROC = _alt2ROC(prop, alt)
        time += slice_time / 60
        dist += slice_dist / 6076.115

        if output == 'raw':
            print S.rjust(locale.format('%.0f', alt, True), 7),
            # calculate ROC at the displayed altitude
            print S.rjust(locale.format('%.0f', ROC, True), 10),
            print S.rjust('%.1f' % (time), 10),
            print S.rjust('%.1f' % (fuel_out), 10),
            print S.rjust('%.1f' % (dist), 10),
            print S.rjust('%3d' % (int(cas_out)), 10)
        elif output == 'latex':
            line = []
            line.append(str(locale.format('%.0f', alt, True)))
            line.append(str(locale.format('%.0f', round(temp_out))))
            line.append(str(locale.format('%.0f', cas_out)))
            line.append(str(locale.format('%.0f', round(ROC / 10.) * 10, True)))
            line.append(str(locale.format('%.0f', time)))
            line.append(str(locale.format('%.1f', fuel_out)))
            line.append(str(locale.format('%.0f', dist)))
            print '&' + '&'.join(line) + '\\\\'
            print '\\hline'
        elif output == 'array':
            array.append([alt, time, fuel_out, dist])
        calc_alt += alt_interval
    if output == 'array':
        return array

def descent_data(prop, weight=1600., alt_max=20000., fuel_units='USG', \
    alt_interval=500., isa_dev=0, temp_units='C', rv='8',  wing_area=110., \
    tas=180., ROD=-500., angle='', speed_units='kt', rpm=2100., sfc=0.45, output='raw'):
    """
    Returns a table of descent performance vs altitude.

    The items in each row of the table are altitude, time, fuel burned and distance.
    Time is in units of minutes, rounded to the nearest half minute.
    Fuel units are selectable, with a default of USG.
    Distances are in nm.
    
    The output may be specified as raw, latex (a LaTeX table for the POH), or array.
    
    tas is the TAS in descent (overridden by the angle, if the angle is provided).
    angle is the flight path angle in degrees.
    """
    tas_fts = U.speed_conv(tas, speed_units, 'ft/s')

    if angle:
        ROD = tas_fts * 60 * M.sin(angle * M.pi / 180)
        
    rod_fts = ROD / 60

    tas = U.speed_conv(tas, speed_units, 'kt')
    
    alt = alt_max + alt_interval
    temp = SA.isa2temp(isa_dev, alt, temp_units=temp_units)
    time = 0
    fuel_used = 0
    dist = 0
    
    if output == 'raw':
        print S.center('Altitude', 10),
        print S.center('ROD', 10),
        print S.center('Time', 10),
        print S.center('Fuel Used', 10),
        print S.center('Dist', 10),
        print S.center('Speed', 10)
        
        print S.center('(ft)', 10),
        print S.center('(ft/mn)', 10),
        print S.center('(mn)', 10),
        f_units = '(' + fuel_units + ')'
        print S.center(f_units, 10),
        print S.center('(nm)', 10),
        print S.center('(KCAS)', 10)
        
        # # data for max altitude
        # print S.rjust(locale.format('%.0f', alt_max, True), 7),
        # print S.rjust(locale.format('%.0f', round(ROD / 10.) * 10, True), 10),
        # print S.rjust('%.1f' % (0), 10),
        # print S.rjust('%.1f' % (fuel_used), 10),
        # print S.rjust('%.1f' % (dist), 10),
        # print S.rjust('%3d' % (A.tas2cas(tas, alt_max, temp, temp_units=temp_units)), 10)

    # elif output == 'latex':
    #     # temp = 15 + isa_dev
    #     MSL_line = []
    #     MSL_line.append(str(locale.format('%.0f', weight, True)))
    #     MSL_line.append('0')
    #     MSL_line.append(str(locale.format('%.0f', temp)))
    #     MSL_line.append(str(locale.format('%.0f', A.tas2cas(tas, alt, temp, temp_units=temp_units))))
    #     MSL_line.append(str(locale.format('%.0f', round(ROD / 10.) * 10, True)))
    #     MSL_line.append('0')
    #     MSL_line.append(str(fuel_used))
    #     MSL_line.append(str(dist))
    #     
    #     print '&'.join(MSL_line) + '\\\\'
    #     print '\\hline'
    # elif output == 'array':
    #     # no header rows, but make blank array
    #     array = [[alt_max,0,0,0]]
        

    alts = []
    RODs = []
    times_temp = []
    CASs = []
    dists_temp = []
    fuel_useds_temp = []
    temps = []

    calc_alt = alt_max - alt_interval / 2.
    while alt > 0:
        temp = SA.isa2temp(isa_dev, alt, temp_units = temp_units)
        eas = A.tas2eas(tas, alt)
        drag = FT.eas2drag(eas, weight)
        pwr_level_flt = tas_fts * drag / 550
        thrust_power = pwr_level_flt + FT.Pexcess_vs_roc(weight, ROD)
        prop_eff = PM.prop_eff(prop, thrust_power, rpm, tas, alt, temp, temp_units=temp_units)
        calc_pwr = thrust_power / prop_eff        
        #fuel_flow = IO.pwr2ff(calc_pwr, rpm, ff_units = 'lb/hr')
        fuel_flow = calc_pwr * sfc 
        # print "Level flt pwr = %.1f, thrust power = %.1f, prop eff = %.3f, fuel flow = %.3f" % (pwr_level_flt, thrust_power, prop_eff, fuel_flow)
        slice_time = alt_interval / rod_fts * -1.
        slice_dist = tas_fts * slice_time
        slice_fuel = fuel_flow * slice_time / 3600
        fuel_used += slice_fuel
        fuel_out = (U.avgas_conv(fuel_used, from_units = 'lb', \
            to_units = fuel_units))
        weight -= slice_fuel
        alt -= alt_interval
        cas_out = A.tas2cas(tas, alt, temp, temp_units=temp_units)
        temp_out = SA.isa2temp(isa_dev, alt)
        time += slice_time / 60.
        dist += slice_dist / 6076.115

        alts.append(alt)
        CASs.append(cas_out)
        RODs.append(ROD)
        times_temp.append(time)
        fuel_useds_temp.append(fuel_out)
        dists_temp.append(dist)
        temps.append(temp_out)
        
        calc_alt += alt_interval
        
    alts.reverse()
    CASs.reverse()
    RODs.reverse()
    temps.reverse()
    
    times = []
    fuel_useds = []
    dists = []
    
    for n, time in enumerate(times_temp):
        times.append(times_temp[-1] - time)
        fuel_useds.append(fuel_useds_temp[-1] - fuel_useds_temp[n])
        dists.append(dists_temp[-1] - dists_temp[n])
        
    times.reverse()
    fuel_useds.reverse()
    dists.reverse()
    
    if output == 'raw':
        for n, alt in enumerate(alts):            
            print S.rjust(locale.format('%.0f', alt, True), 7),
            # calculate ROC at the displayed altitude
            print S.rjust(locale.format('%.0f', RODs[n], True), 10),
            print S.rjust('%.1f' % (times[n]), 10),
            print S.rjust('%.1f' % (fuel_useds[n]), 10),
            print S.rjust('%.1f' % (dists[n]), 10),
            print S.rjust('%3d' % (int(CASs[n])), 10)
    elif output == 'latex':
        for n, alt in enumerate(alts):                    
            line = []
            line.append(str(locale.format('%.0f', alt, True)))
            line.append(str(locale.format('%.0f', round(temps[n]))))
            line.append(str(locale.format('%.0f', CASs[n])))
            line.append(str(locale.format('%.0f', round(RODs[n] / 10.) * 10, True)))
            line.append(str(locale.format('%.0f', times[n])))
            line.append(str(locale.format('%.1f', fuel_useds[n])))
            line.append(str(locale.format('%.0f', dists[n])))
            print '&' + '&'.join(line) + '\\\\'
            print '\\hline'
    elif output == 'array':
        array = []
        for n, alt in enumerate(alts):
            array.append([alt, times[n], fuel_useds[n], dists[n]])
        return array

def cruise_data(prop, cruise_A=821.27884302, cruise_B=3.8201670757e-05,\
    cruise_power = 130, mixture = 'econ', cruise_rpm=2400, climb_weight=1800., \
    descent_weight=1600., alt_max=20000., fuel_units='USG', alt_interval=500., \
    isa_dev=0, temp_units='C', rv='8', wing_area=110., TO_fuel = 1.5, TO_dist = 0, \
    climb_pwr = 'max', climb_pwr_factor=0.9, \
    climb_speed = 'norm',  \
    descent_tas=180, descent_ROD=-500., descent_angle='', speed_units='kt', \
    descent_rpm=2100., descent_sfc=0.45, fuel_reserve=8, output='raw'):
    """
    Returns a table of cruise performance vs altitude.

    The items in each row of the table are altitude, time, fuel burned and distance.
    Time is in units of minutes, rounded to the nearest half minute.
    Fuel units are selectable, with a default of USG.
    Distances are in nm.
    
    The output may be specified as raw, latex (a LaTeX table for the POH), data 
    (suitable for graphing with gnuplot) or array.
    
    descent_angle is the flight path angle in degrees.  It overrides the rate of 
    descent (ROD) if provided.
    """
    Wt_std = 1800.
    Wt_ratio = climb_weight/Wt_std
    climb_data_a = climb_data(prop, weight = climb_weight, alt_max = alt_max, TO_fuel = TO_fuel, TO_dist = TO_dist,  fuel_units = fuel_units, alt_interval = alt_interval, isa_dev = isa_dev, temp_units = temp_units, rv = rv, wing_area = wing_area, pwr = climb_pwr, pwr_factor=climb_pwr_factor, climb_speed = climb_speed, output = 'array')
    descent_data_a = descent_data(prop, weight=descent_weight, alt_max=alt_max, fuel_units=fuel_units,  alt_interval=alt_interval, isa_dev=isa_dev, temp_units=temp_units, rv=rv,  wing_area=wing_area, tas=descent_tas, ROD=descent_ROD, angle=descent_angle, speed_units=speed_units, rpm=descent_rpm, sfc=descent_sfc, output='array')
    cruise_ff = IO.pwr2ff(cruise_power, cruise_rpm, mixture=mixture)
    
    if output == 'raw':
        print "Climb speed = %s and climb power = %s" % (climb_speed, climb_pwr)
        print "Cruise power = %.0f and cruise fuel flow = %.2f" % (cruise_power, cruise_ff)
        print S.center('Altitude', 10),
        print S.center('TAS', 10),
        print S.center('Range', 10),
        print S.center('Fuel Flow', 10)
        
        
        print S.center('(ft)', 10),
        print S.center('(kt)', 10),
        print S.center('(nm)', 10),
        print S.center('(USG/h)', 10)
    elif output == 'array':
        array = []
    elif output == 'data':
        if descent_angle:
            angle_text = 'a descent angle of %s degrees' % descent_angle
        else:
            angle_text = 'a descent rate of %i ft/mn' % descent_ROD
        print '# RV-8 Cruise Range Chart - Wheel Pants OFF'
        print '# descent at %.0f KTAS and %s' % (descent_tas, angle_text)
        print '# %i%% power with fuel flow of %.1f USG/hr' % (cruise_power / 2., cruise_ff)
        print '# altitude  range'
        print '# ft KTAS'
        
    elif output == 'latex':
        line.append(str(locale.format('%.0f', calt, True)))
        line.append(str(locale.format('%.1f', cruise_tas)))
        line.append(str(locale.format('%.0f', total_dist)))
        # print line
        pass
    for item in zip(climb_data_a, descent_data_a):
        ([calt, ctime, cfuel, cdist], [dalt, dtime, dfuel, ddist]) = item
        cruise_fuel = 42 - (cfuel + dfuel + fuel_reserve)
        sigma = SA.alt2density_ratio(calt)
        cruise_tas = 1/12.*((8*cruise_A*cruise_B*Wt_ratio**2 + (3.*M.sqrt(3.)*cruise_power**2*sigma + M.sqrt(-256*cruise_A**3.*cruise_B*Wt_ratio**6 + 27.*cruise_power**4*sigma**2))**(2/3.)*2**(1/3.)*cruise_B**(2/3.))**(3./4)*3.**(3./4)*sigma**(1/4.) + M.sqrt(12.*M.sqrt(3.*M.sqrt(3.)*cruise_power**2*sigma + M.sqrt(-256*cruise_A**3.*cruise_B*Wt_ratio**6 + 27.*cruise_power**4*sigma**2))*cruise_B**(1/3.)*cruise_power*sigma - M.sqrt(8*cruise_A*cruise_B*Wt_ratio**2 + (3.*M.sqrt(3.)*cruise_power**2*sigma + M.sqrt(-256*cruise_A**3.*cruise_B*Wt_ratio**6 + 27.*cruise_power**4*sigma**2))**(2/3.)*2**(1/3.)*cruise_B**(2/3.))*(8*3.**(1/4.)*cruise_A*cruise_B**(1/3.)*Wt_ratio**2*M.sqrt(sigma) + (3.*M.sqrt(3.)*cruise_power**2*sigma + M.sqrt(-256*cruise_A**3.*cruise_B*Wt_ratio**6 + 27.*cruise_power**4*sigma**2))**(2/3.)*2**(1/3.)*3.**(1/4.)*M.sqrt(sigma)))*3.**(5/8)*abs(cruise_B)**(1/3.))*2**(2/3.)/((3.*M.sqrt(3.)*cruise_power**2*sigma + M.sqrt(-256*cruise_A**3.*cruise_B*Wt_ratio**6 + 27.*cruise_power**4*sigma**2))**(1/6.)*(8*cruise_A*cruise_B*Wt_ratio**2 + (3.*M.sqrt(3.)*cruise_power**2*sigma + M.sqrt(-256*cruise_A**3.*cruise_B*Wt_ratio**6 + 27.*cruise_power**4*sigma**2))**(2/3.)*2**(1/3.)*cruise_B**(2/3.))**(1/4.)*cruise_B**(2/3.)*sigma**(3./4))
        cruise_dist = cruise_fuel * cruise_tas / cruise_ff
        cruise_time = cruise_dist / cruise_tas * 60
        total_dist = cdist + cruise_dist + ddist
        total_time = ctime + cruise_time + dtime
#        print "%5.0f %.1f %.1f %.1f %5.1f" %  (calt, cruise_tas, cruise_fuel, cruise_dist, total_dist)
        if output == 'raw':
            print S.rjust(locale.format('%.0f', calt, True), 7),
            print S.rjust('%.1f' % (cruise_tas), 10),
            print S.rjust('%.1f' % (total_dist), 10),
            print S.rjust('%.1f' % (cruise_ff), 10)
        elif output == 'data':
            print '%.1f\t%.0f' % (total_dist, calt)
        
            
