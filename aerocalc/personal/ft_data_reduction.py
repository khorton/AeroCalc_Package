#!/usr/bin/env python

"""
Performs various flight test data reduction functions.

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
# version 0.21, 07 Sep 2013
#
# Version History:
# vers     date     Notes
# 0.21   07 Sep 13  Added climb performance data reduction functions
##############################################################################
#
# To Do:  1.  Add functions:
#                 cas2cl
#                 function to look for best gps2tas time slices, given a target 
#                 IAS
#         
#         2.  Test the following function:
#             climb_perf_alt_corr
#         4. Add examples to all functions.
#         
#         5. Add tests for all functions.
#         
#         6. Done
#
#         7. Add friction hp component to pwr_humid_corr
#         
# Done: 1. Add functions:
#         
#                 tas2cl
#                 ias2cas # apply PEC to IAS to get CAS
#                 dpp_over_qcic # calculate PEC
#                 cas_err2dpp_over_qcic # determine qc/dp from speed course data
#                 gps2tas # get tas from gps data
#
#         6. Validate pwr_humid_corr function - done against:
#            http://wahiduddin.net/calc/cf.htm

##############################################################################

from __future__ import division
import airspeed as A
import math as M
import std_atm as SA
import unit_conversion as U
from default_units import *
import data_file as DF
import piston as P
import numpy as N
import scipy.optimize as O
import constants

# import numpy.core.records as NR

Rho0 = constants.Rho0
"""
Density at sea level, kg/m**3
"""

# P0 = 101325.0
# """
# Pressure at sea level, pa
# """
# 
A0 = 340.294
"""
Speed of sound at sea level, std day, m/s

Speed of sound from:
  http://www.edwards.af.mil/sharing/tech_pubs/Handbook-10%20March02.pdf
"""
F = (1.25**2.5)*((2.4**2)**2.5)*1.2
"""
F is calculated by manipulating NASA RP 1046 pg 17.

F is used in some of the supersonic solution equations.
"""

g = constants.g
"""
acceleration due to gravity, m/s**s
"""


##############################################################################
#
# eas2cl
#
# calculate lift coefficient, given EAS
#
##############################################################################
def eas2cl(eas, weight, wing_area, load_factor = 1, speed_units = 'kt', 
           weight_units = 'lb', area_units = 'ft**2'):
    """
    Returns the coefficient of lift, given equivalent airspeed, weight, wing
    area, and load factor (defaults to 1 if not provided).
    """
    eas = U.speed_conv(eas, from_units = speed_units, to_units = 'm/s')
    weight = U.wt_conv(weight, from_units = weight_units, to_units = 'kg')
    wing_area = U.area_conv(wing_area, from_units = area_units, 
                            to_units = 'm**2')

    cl = 2 * weight * g * load_factor / (Rho0 * wing_area * eas ** 2)

    return cl


##############################################################################
#
# tas2cl
#
# calculate lift coefficient, given TAS
#
##############################################################################
def tas2cl(tas, altitude, weight, wing_area, temperature = 'std', 
           load_factor = 1, speed_units = 'kt', alt_units = 'ft', 
           temp_units = 'C', weight_units = 'lb', area_units = 'ft**2'):
    """
    Returns the coefficient of lift, given true airspeed, altitude, weight, 
    and wing area.  
    
    Temperature and load factor are optional inputs.  The temperature, if 
    not provided, defaults to the standard temperature for the altitude.  
    The load factor, if not provided, defaults to 1.
    """
    eas = A.tas2eas(tas, altitude, temperature, speed_units, 
                    alt_units, temp_units)

    cl = eas2cl(eas, weight, wing_area, load_factor, speed_units, 
                weight_units, area_units)

    return cl

##############################################################################
#
# Drag
#
# calculate drag coefficient, given lift coefficient and configuration
#
# calculate drag
#
##############################################################################
def cl2cd(cl, rv = '8', flap = 0, wheel_pants = 1):
    """
    Returns the drag coefficient, given the lift coefficient and flap extension.
    Flap = 0 for flaps retracted, and flap = 1 for flaps fully extended.

    RV-6 drag polar is based on the drag polar published by the CAFE 
    Foundation, with very minor adjustments to better match their data.

    RV-8 drag polar is based on the RV-6 drag polar, with a very minor 
    assumed increase in Oswald's span efficiency, due the narrow fuselage.
    The CD0 was derived by taking the RV-6 drag polar, determining the power
    required to achieve Van's published max speed  for an 180 hp  RV-6 
    (193 hp required with 74 inch dia Hartzell - Van's efficient airbox 
    recovers some ram rise, and the published data was with a 72 inch dia
    prop). The RV-8 CD0 was adjusted to obtain Van's published speed.

    The RV-8A CD0 was obtained in the same way was the RV-8 CD0.
    """
    if rv == '6':
        aspect_ratio = 23**2/110.
        oswald_eff = .851 # value from CAFE APR
        cd0 = 0.02118 # fudged to match min drag data from CAFE APR.  They published 0.021
    elif rv == '8':
        aspect_ratio = 23**2/110.
        oswald_eff = .86 # assumed to be slightly better than the RV-6, due to the narrower fuselage with the same wing span

#       cd0 = 0.0197 # selected to match the difference in Vans claimed perf from RV-6 to RV-8
        cd0 = 0.0209 # selected to match the difference in Vans claimed perf from RV-8 to RV-8A
    elif rv == '8a':
        aspect_ratio = 23**2/110.
        oswald_eff = .86 # assumed to be slightly better than the RV-6, due to the narrower fuselage with the same wing span

        cd0 = 0.0215 # selected to match the RV-8A CAFE APR Vmax at 600 ft
    elif rv == 'F1':
        aspect_ratio = (24 + 10./12)**2/102.
        oswald_eff = .9 # assumed to be slightly better than the RVs, due to tapered wing
        cd0 = 0.021
    elif rv == '3':
        aspect_ratio = (19+11./12)**2/90.
        oswald_eff = .86 #guess
        cd0 = 0.021 # guess
    else:
        raise ValueError, 'invalid RV model'

    if flap != 0:
        raise ValueError, 'This function does not yet have data for flap angle other than 0.'
    
    if wheel_pants == 0:
    	  cd0 += 0.00155

    K = 1 / (M.pi * oswald_eff * aspect_ratio)
    cd = cd0 + K * cl ** 2

    return cd

def cl2cd_test(cl, cd0 = 0.021, e = 0.86, flap = 0):
    """
    Returns the drag coefficient, given the lift coefficient and flap extension.
    Flap = 0 for flaps retracted, and flap = 1 for flaps fully extended.
    """
    aspect_ratio = 23**2/110.

    K = 1 / (M.pi * e * aspect_ratio)
    cd = cd0 + K * cl ** 2

    return cd

def cd2drag(cd, eas, wing_area, speed_units = 'kt', drag_units = 'lb', 
            area_units = 'ft**2'):
    """
    Returns drag, given the drag coefficient, etc.
    """
    eas = U.speed_conv(eas, from_units = speed_units, to_units = 'm/s')
    wing_area = U.area_conv(wing_area, from_units = area_units, to_units = 'm**2')
    drag = 0.5 * Rho0 * eas **2 * wing_area * cd
    drag = U.force_conv(drag, from_units = 'N', to_units = drag_units)

    return drag

def eas2drag(eas, weight, wing_area=110, rv = '8', flap = 0, speed_units = 'kt', 
             drag_units = 'lb', area_units = 'ft**2', load_factor = 1, wheel_pants=1):
    """ 
    Returns drag, given eas, etc.  
    Validated against the data in the RV-6 CAFE APR.  Matches within 0.4%
    """
    cl = eas2cl(eas, weight, wing_area, speed_units = speed_units, area_units = area_units, load_factor = load_factor)
    cd = cl2cd(cl, rv, flap, wheel_pants)
    drag = cd2drag(cd, eas, wing_area, speed_units = speed_units, drag_units = drag_units, area_units = area_units)
    
    return drag

def d(eas):
    """
    test function for RV-6 drag, to compare against CAFE foundation)
    """
    wt = 1650
    wa = 110
    drag = eas2drag(eas, wt, wa, speed_units = 'mph')
    return drag


##############################################################################
#
# dpp_over_qcic to corrected data
#
# calculate error in sensed static pressure as a function of speed, weight, etc
#
# calculate cas and altitude given ias, etc
#
##############################################################################
def _CL2dpp_over_qcic(CL, flap):
    """
    Returns the error in static pressure over the sensed delta P, given the
    lift coefficient and the flap angle.  The error in the static pressure
    over sensed delta P is normally a function of configuration, CL and/or
    Mach.  Mach is assumed to not be relevant in this speed range (to be
    confirmed by tests at high and low altitude).
    
    For internal use only.
    """
    # the following lines must provide a dpp_over_qcic as a function of CL.
    # 0.02, 0.03, etc are false values to have something to return for now.  
    # This must be replaced by a function when data is available.
    if flap == 0:
        dpp_over_qcic = -0.02
    elif flap <= 0.3:
        dpp_over_qcic = 0
    elif flap <= 0.5:
        dpp_over_qcic = 0.02
    else:
        dpp_over_qcic = 0.05

    return dpp_over_qcic


# def ias2dpp_over_qcic(IAS, W, N, flap, S, speed_units = 'kt', weight_units = 'lb', area_units = 'ft**2'):
#   """
#   Returns the error in static pressure over the sensed delta P, given IAS 
#   (corrected for instrument error), altitude, weight, load factor, flap 
#   angle and wing area.
    
#   W = weight
#   N = load factor
#   S = wing area
#   """
#   CL_approx = eas2cl(IAS, W, S, N, speed_units = speed_units, weight_units = weight_units, area_units = area_units)
        
#   return _CL2dpp_over_qcic(CL_approx, flap)


# def ias2static_press_error_orig(IAS, W, N, flap, S, speed_units = 'kt', weight_units = 'lb', area_units = 'ft**2', press_units = 'hpa'):
#   """
#   Returns the static pressure error, given IAS (corrected for instrument 
#   error), altitude, weight, load factor, flap angle and wing area.
    
#   This error is positive if the sensed static pressure is greater than
#   the ambient pressure.  This would lead to an altimeter and airspeed
#   indicator that read lower than the actual values.
    
#   W = weight
#   N = load factor
#   S = wing area
#   """
#   delta_P_sensed = A.cas2dp(IAS, press_units = press_units)
#   static_press_error = ias2dpp_over_qcic(IAS, W, N, flap, S, speed_units = speed_units, weight_units = weight_units, area_units = area_units) * delta_P_sensed
    
#   return static_press_error


def ias2static_press_error(IAS, W, N, flap, S, speed_units = 'kt', 
                           weight_units = 'lb', area_units = 'ft**2', 
                           press_units = 'hpa'):
    """
    Returns the static pressure error, given IAS (corrected for instrument 
    error), altitude, weight, load factor, flap angle and wing area.
    
    This error is positive if the sensed static pressure is greater than
    the ambient pressure.  This would lead to an altimeter and airspeed
    indicator that read lower than the actual values.
    
    W = weight
    N = load factor
    S = wing area
    """
    delta_P_sensed = A.cas2dp(IAS, press_units = press_units)
    CL_approx = eas2cl(IAS, W, S, N, speed_units = speed_units, weight_units = weight_units, area_units = area_units)
    static_press_error = _CL2dpp_over_qcic(CL_approx, flap) * delta_P_sensed
    
    return static_press_error

    
def ias2cas(IAS_raw, W, N, flap, S = 110, speed_units = 'kt', 
            weight_units = 'lb', area_units = 'ft**2'):
    """
    Returns the calibrated airspeed, given raw IAS (i.e. not corrected
    for instrument error), altitude, weight, load factor, flap angle and
    wing area.
    
    W = weight
    N = load factor
    S = wing area
    """
    IAS = asi_inst_error_corr(IAS_raw)
    delta_P_sensed = A.cas2dp(IAS)
    delta_P_corrected = delta_P_sensed + ias2static_press_error(IAS, W, N, flap, S, speed_units = speed_units, weight_units = weight_units, area_units = area_units)
    CAS = A.dp2cas(delta_P_corrected, speed_units = speed_units)
    
    return CAS
    

def ias2alt(IAS_raw, alt_ind, W, N, flap, S = 110, speed_units = 'kt', 
            weight_units = 'lb', area_units = 'ft**2', alt_units = 'ft'):
    """
    Returns the corrected altitude, given raw IAS (i.e. not corrected for 
    instrument error), altitude, weight, load factor, flap angle and wing
    area.
    
    W = weight
    N = load factor
    S = wing area
    """
    press_units = 'hpa'
    IAS = asi_inst_error_corr(IAS_raw)
    P_sensed = SA.alt2press(alt_ind, alt_units = alt_units, press_units = press_units)
    P_corrected = P_sensed - ias2static_press_error(IAS, W, N, flap, S, speed_units = speed_units, weight_units = weight_units, area_units = area_units, press_units = press_units)
    alt_corrected = SA.press2alt(P_corrected, alt_units = alt_units, press_units = press_units)
    
    return alt_corrected

    
##############################################################################
#
# speed error to dpp_over_qcic
#
##############################################################################
def cas_err2dpp_over_qcic(ias, cas_err, speed_units = 'kt'):
  """
  Returns the error in static pressure over the sensed delta P, given IAS
  (corrected for instrument error), the difference between IAS and CAS and
  altitude.
  
  cas_err is positive if the IAS is higher than the CAS.
  """
  qcic = A.cas2dp(ias) # dynamic pressure, based on sensed values
  qc = A.cas2dp(ias - cas_err) # actual dynamic pressure
  dpp = qc - qcic
  dpp_over_qcic = dpp / qcic
  
  return dpp_over_qcic

##############################################################################
#
# Field performance calculations
#
##############################################################################
def ground_dist_wind_corr(Vc, Vw, Hp=0, T=15, speed_units=default_speed_units, 
                        alt_units=default_alt_units, 
                        temp_units=default_temp_units):
    """
    Returns ratio of take-off or landing ground roll with zero wind to distance 
    with wind
    
    Vc = CAS
    Vw = wind speed.  Positive for head wind.  Negative for tail wind.
    Hp = pressure altitude
    T = ambient air temperature
    
    returns (distance with wind)/(distance with zero wind)
    """
    Vt = A.cas2tas(Vc, Hp, T, speed_units, alt_units, temp_units,)
    Vg = Vt - Vw
    dist_ratio = (Vt/Vg)**1.85
    
    return dist_ratio

def air_dist_wind_corr(Vw, T_air, length_units=default_length_units, 
                       speed_units=default_speed_units):
    """
    Returns take-off or landing air distance with zero wind - air distance with 
    wind
    
    Vw = wind speed.  Positive for head wind.  Negative for tail wind.
    T_air = air time over which the wind has an effect
    """
    dist_corr_ft = U.speed_conv(Vw, speed_units, 'ft/s') * T_air
    dist_corr = U.length_conv(dist_corr_ft, 'ft', length_units)
    
    return dist_corr

def ldg_ground_dist_density_corr(Hp, T='std', alt_units=default_alt_units, 
                                 temp_units=default_temp_units):
    """
    Returns the ratio of zero wind landing distance at sea level, std day to 
    zero wind landing distance at test conditions.
    
    Hp = pressure altitude at test conditions
    T  = ambient air temperature (optional).  Assumed to be standard temperature 
         if not provided
    """
    sigma = SA.alt_temp2density_ratio(Hp, T, alt_units, temp_units)
    
    return sigma
    
def take_off_ground_distance_corr_fp(Wt_ratio, Hp, T='std', alt_units=default_alt_units, temp_units=default_temp_units):
    """
    Returns the ratio of zero wind take-off ground roll at sea level, std day to 
    zero wind take-off ground roll at test conditions.  For aircraft with 
    fixed-pitch prop, using full throttle for take-off.
    
    Wt_ratio = (test weight)/(standard weight)
    Hp       = pressure altitude at test conditions
    T        = ambient air temperature (optional).  Assumed to be standard 
               temperature if not provided
    """
    sigma = SA.alt_temp2density_ratio(Hp, T, alt_units, temp_units)
    if T == 'std':
        theta = SA.alt2temp_ratio(Hp, alt_units)
    else:
        theta = SA.temp2temp_ratio(T, temp_units)
    
    dist_ratio = Wt_ratio**-2.4*sigma**2.4*theta**-0.5
    
    return dist_ratio
    
def take_off_air_distance_corr_fp(Wt_ratio, Hp, T='std', 
                                  alt_units=default_alt_units, 
                                  temp_units=default_temp_units):
    """
    Returns the ratio of zero wind take-off air distance at sea level, std day 
    to zero wind take-off air distance at test conditions.  For aircraft with 
    fixed-pitch prop, using full throttle for take-off.
    
    Wt_ratio = (test weight)/(standard weight)
    Hp       = pressure altitude at test conditions
    T        = ambient air temperature (optional).  Assumed to be standard 
               temperature if not provided
    """
    sigma = SA.alt_temp2density_ratio(Hp, T, alt_units, temp_units)
    if T == 'std':
        theta = SA.alt2temp_ratio(Hp, alt_units)
    else:
        theta = SA.temp2temp_ratio(T, temp_units)
    
    dist_ratio = Wt_ratio**-2.2*sigma**2.2*theta**-0.6
    
    return dist_ratio
    
def take_off_ground_distance_corr_cs(Wt_ratio, Hp, N_ratio, T='std', alt_units=default_alt_units, temp_units=default_temp_units):
    """
    Returns the ratio of zero wind take-off ground roll at sea level, std day to zero wind take-off ground roll at test conditions.  For aircraft with constant-speed prop.
    
    Wt_ratio = (test weight)/(standard weight)
    Hp = pressure altitude at test conditions
    T = ambient air temperature (optional).  Assumed to be standard temperature if not provided.
    N_ratio = ratio of engine rpm at lift-off to rpm at rated power
    """
    sigma = SA.alt_temp2density_ratio(Hp, T, alt_units, temp_units)
    delta = SA.alt2press_ratio(Hp, alt_units)
    
    dist_ratio = Wt_ratio**-2.6*sigma**1.7*N_ratio**0.7*delta**0.9
    
    return dist_ratio

def take_off_air_distance_corr_cs(Wt_ratio, Hp, N_ratio, T='std', alt_units=default_alt_units, temp_units=default_temp_units):
    """
    Returns the ratio of zero wind take-off air distance at sea level, std day to zero wind take-off air distance at test conditions.  For aircraft with constant-speed prop.
    
    Wt_ratio = (test weight)/(standard weight)
    Hp = pressure altitude at test conditions
    T = ambient air temperature (optional).  Assumed to be standard temperature if not provided.
    N_ratio = ratio of engine rpm at lift-off to rpm at rated power
    """
    sigma = SA.alt_temp2density_ratio(Hp, T, alt_units, temp_units)
    delta = SA.alt2press_ratio(Hp, alt_units)
    
    dist_ratio = Wt_ratio**-2.3*sigma**1.2*N_ratio**0.8*delta**1.1
    
    return dist_ratio

##############################################################################
#
# climb perf speed variation correction
#
##############################################################################
def climb_perf_alt_corr(CAS, altitude, CAS_target, alt_units = 'ft', speed_units = 'kt',):
    """
    Returns a barometric altitude correction for climb performance test
    points.  Accounts for small CAS variations from the target CAS by
    trading kinetic energy for potential energy.  The altitude correction
    is corrected for non-standard altitudes.
    
    Interestingly enough, although temperature appears in the equations,
    it seems to fall out. I.e. the change in baro altitude does not depend
    on the OAT.
    """
    CAS = U.speed_conv(CAS, from_units = speed_units, to_units = 'm/s')
    CAS_target = U.speed_conv(CAS_target, from_units = speed_units, to_units = 'm/s')
    
    sigma = SA.alt2density_ratio(altitude, alt_units = alt_units)

    
    delta_h = (1/(2 * g * sigma)) * (CAS ** 2 - CAS_target ** 2)

    delta_h = U.length_conv(delta_h, from_units = 'm', to_units = alt_units)

    
    return delta_h


##############################################################################
#
# climb perf speed variation correction - alternate
#
# gets same answer as first version.
#
##############################################################################
# def climb_perf_alt_corr2(CAS, altitude, CAS_target, alt_units = 'ft', speed_units = 'kt',):
#   """
#   Returns a barometric altitude correction for climb performance test
#   points.  Accounts for small CAS variations from the target CAS by
#   trading kinetic energy for potential energy.  The altitude correction
#   is corrected for non-standard altitudes.
#   
#   Interestingly enough, although temperature appears in the equations,
#   it seems to fall out. I.e. the change in baro altitude does not depend
#   on the OAT.
#   """
#   CAS = U.speed_conv(CAS, from_units = speed_units, to_units = 'm/s')
#   CAS_target = U.speed_conv(CAS_target, from_units = speed_units, to_units = 'm/s')
#   
#   sigma = SA.alt2density_ratio(altitude, alt_units = alt_units)
#
#   delta_CAS = CAS - CAS_target
#   delta_h = (delta_CAS * CAS_target + delta_CAS ** 2) / (g * sigma)
#   delta_h = U.length_conv(delta_h, from_units = 'm', to_units = alt_units)
# 
#   return delta_h

##############################################################################
#
# climb or descent rate vs excess power
#
##############################################################################
def roc_vs_Pexcess(W, excess_power, wt_units='lb', power_units='hp'):
    """
    Return rate of climb as function of weight and excess power.
    """
    
    W = U.mass_conv(W, wt_units, 'lb')
    excess_power = U.power_conv(excess_power, power_units, 'ft-lb/mn')
    roc = excess_power / W
    
    return roc


##############################################################################
#
# excess power vs climb or descent rate
#
##############################################################################
def Pexcess_vs_roc(W, roc, wt_units='lb', power_units='hp'):
    """
    Return excess power as function of weight and rate of climb.
    """
    
    W = U.mass_conv(W, wt_units, 'lb')
    
    excess_power = roc * W
    excess_power = U.power_conv(excess_power, 'ft-lb/mn', power_units)
    
    return excess_power



##############################################################################
#
# TAS from GPS data.
#
##############################################################################
def gps2tas(GS, TK, verbose = 0):
    """
    Returns true airspeed, given GPS groundspeed and track on at least
    three legs (four legs preferred).  Uses the method developed by Doug
    Gray - http://www.kilohotel.com/rv8/rvlinks/doug_gray/TAS_FNL4.pdf
    
    GS and TK are lists of ground speed and track data.
    
    Three legs:
        If verbose = 0, then only TAS is returned.
        If verbose = 1, then TAS, wind speed and direction are returned.
        If verbose = 2, then TAS, wind speed and direction and the heading
        for each leg are returned.  The wind speed and direction is 
        returned as a tuple, and the headings are returned as a tuple

        
    Four legs:
        Data from only three legs is sufficient to calculate TAS.  If data
        four legs is entered, four different calculations are conducted,
        using a different mix of three data points for each calculation.
        If the data quality is high, the TAS and wind for all four 
        calculations will be similar.  The standard deviation on the TAS is
        calculated - good quality data will have a standard deviation of
        less than 1 kt.
        
        If verbose = 0, then only TAS is returned.
        If verbose = 1, then TAS and its standard deviation are returned.
        If verbose = 2, then TAS, its standard deviation and the four wind
        speeds and directions are returned (the winds are returned as a list
        of four tuples)
    
    Validated against sample data in four leg tab of NTPS GPS PEC spreadsheet:
    http://www.ntps.edu/Files/GPS%20PEC.XLS
    
    Examples:
        
        Data for all examples:
            >>> gs = [178, 185, 188, 184]
            >>> tk = [178, 82, 355, 265]
            
            Determine the TAS, given the above data from four runs:
            >>> gps2tas(gs, tk)
            183.7266955711462
            
            Determine the TAS and standard deviation from the four calculations:
            >>> gps2tas(gs, tk, verbose = 1)
            (183.7266955711462, 0.8270963470592844)
            
            Determine the TAS, standard deviation, and wind speed and direction
            for each calculation:
            >>> gps2tas(gs, tk, verbose = 2)
            (183.7266955711462, 0.8270963470592844, ((5.260836927084306, 194.51673740323213), (3.5823966532035922, 181.52174627838372), (5.1495218164839995, 162.69803415599802), (6.4436728241320145, 177.94783081049718)))
    """
    # confirm GS and TK are valid lengths:
    if 2 < len(GS) < 5:
        pass
    else:
        raise ValueError, 'GS must be a list of three or four items'
        
    if 2 < len(TK) < 5:
        pass
    else:
        raise ValueError, 'TK must be a list of three or four items'
    
    if len(GS) != len(TK):
        raise ValueError, 'The ground speed and track arrays must have the same number of elements.'
        
    if len(GS) == 3:
        result = gps2tas3(GS, TK, verbose)
        return result
    else:
        gs_data_sets, tk_data_sets, results = [], [], []
        
        gs_data_sets.append([GS[0], GS[1], GS[2]])
        gs_data_sets.append([GS[1], GS[2], GS[3]])
        gs_data_sets.append([GS[2], GS[3], GS[0]])      
        gs_data_sets.append([GS[3], GS[0], GS[1]])

        tk_data_sets.append([TK[0], TK[1], TK[2]])
        tk_data_sets.append([TK[1], TK[2], TK[3]])
        tk_data_sets.append([TK[2], TK[3], TK[0]])      
        tk_data_sets.append([TK[3], TK[0], TK[1]])
        
        for (gs, tk) in zip (gs_data_sets, tk_data_sets):
            results.append(gps2tas3(gs, tk, 2))
        
        ave_TAS = 0
        ave_wind_x = 0
        ave_wind_y = 0
        sum2_TAS = 0
        
        for item in results:
            ave_TAS +=item[0]
            sum2_TAS += item[0] ** 2
            ave_wind_x += item[1][0] * M.sin(M.pi * item[1][1] / 180.)
            ave_wind_y += item[1][0] * M.cos(M.pi * item[1][1] / 180.)

        ave_TAS /= 4.
        std_dev_TAS = M.sqrt((sum2_TAS - 4 * ave_TAS ** 2) / 3)
        ave_wind_x /= 4
        ave_wind_y /= 4.
        ave_wind_speed = M.sqrt(ave_wind_x ** 2 + ave_wind_y ** 2)
        ave_wind_dir = (720. - (180. / M.pi * M.atan2(ave_wind_x, ave_wind_y))) % 360
        # return results
        
        if verbose == 0:
            return ave_TAS
        elif verbose == 1:
            return ave_TAS, std_dev_TAS
        elif verbose == 2:
            return ave_TAS, std_dev_TAS, ((results[0][1][0], results[0][1][1]),(results[1][1][0], results[1][1][1]),(results[2][1][0], results[2][1][1]),(results[3][1][0], results[3][1][1]))
        else:
            raise ValueError, 'The value of verbose must be equal to 0, 1 or 2'


def gps2tas3(GS, TK, verbose=0):
    """
    Returns true airspeed, given GPS groundspeed and track on three legs.
    Uses the method developed by Doug Gray:
    http://www.kilohotel.com/rv8/rvlinks/doug_gray/TAS_FNL4.pdf
    
    GS and TK are arrays of ground speed and track data.
    
    If verbose = 0, then only TAS is returned.
    If verbose = 1, then TAS, wind speed and wind direction are returned.
    If verbose = 2, then TAS, wind speed and direction and the heading for
    each leg are returned.  The wind speed and direction is returned as a 
    tuple, and the headings are returned as a tuple

    Validated against sample in Doug Gray's paper.
    
    Examples:
    
    """
    x, y, b, m, hdg = [], [], [], [], []

    for (gs, tk) in zip(GS, TK):
        x.append(gs * M.sin(M.pi * (360. - tk) / 180.))
        y.append(gs * M.cos(M.pi * (360. - tk) / 180.))
    
    m.append(-1 * (x[1] - x[0]) / (y[1] - y[0]))
    m.append(-1 * (x[2] - x[0]) / (y[2] - y[0]))
    
    b.append((y[0] + y[1]) / 2 - m[0] * (x[0] + x[1]) / 2)
    b.append((y[0] + y[2]) / 2 - m[1] * (x[0] + x[2]) / 2)
    
    wind_x = (b[0] - b[1]) / (m[1] - m[0]) 
    wind_y = m[0] * wind_x + b[0]
    
    wind_speed = M.sqrt(wind_x ** 2 + wind_y ** 2)
    wind_dir = (540. - (180. / M.pi * M.atan2(wind_x, wind_y))) % 360.
    
    TAS = M.sqrt((x[0] - wind_x) ** 2 + (y[0] - wind_y) ** 2)
    
    if verbose >= 2:
        hdg.append((540. - (180. / M.pi * M.atan2(wind_x - x[0], wind_y - y[0]))) % 360.)
        hdg.append((540. - (180. / M.pi * M.atan2(wind_x - x[1], wind_y - y[1]))) % 360.)
        hdg.append((540. - (180. / M.pi * M.atan2(wind_x - x[2], wind_y - y[2]))) % 360.)
        
        return TAS, (wind_speed, wind_dir), (hdg[0], hdg[1], hdg[2])

    elif verbose == 1:
        return TAS, (wind_speed, wind_dir)
    elif verbose == 0:
        return TAS
    else:
        raise ValueError, 'The value of verbose must be equal to 0, 1 or 2'


def gps_data_file2tas(data_file, header_rows, timeslices, gs_column_name, tk_column_name, sep = '\t', verbose = 0):
    """
    Returns true airspeed, given a data_file, list of three or four time
    slices (one time slice for each leg) and the ground speed and track 
    column numbers in the data file.
    
    data_file -      the path to the file with the GPS data
    header_rows -    the number of header rows before the first data row
    timeslices -     a list of tuples, with each tuple containing the start and 
                     end times for each time slice.  The time slices must be in
                     same format as the times in the data_file.  The time slices
                     must be in chronological order, earliest to latest.
    gs_column_name - the name of the column that contains the ground speed data.
    tk_column_name - the name of the column that contains the track data.
    sep -            column delimiter.  Default is a tab
    
    Three legs:
        If verbose = 0, then only TAS is returned.
        If verbose = 1, then TAS, wind speed and direction are returned.
        If verbose = 2, then TAS, wind speed and direction and the heading
        for each leg are returned.  The wind speed and direction is 
        returned as a tuple, and the headings are returned as a tuple

        
    Four legs:
        Data from only three legs is sufficient to calculate TAS.  If data
        four legs is entered, four different calculations are conducted,
        using a different mix of three data points for each calculation.
        If the data quality is high, the TAS and wind for all four 
        calculations will be similar.  The standard deviation on the TAS is
        calculated - good quality data will have a standard deviation of
        less than 1 kt.
        
        If verbose = 0, then only TAS is returned.
        If verbose = 1, then TAS and its standard deviation are returned.
        If verbose = 2, then TAS, its standard deviation and the four wind
        speeds and directions are returned (the winds are returned as a list
        of four tuples)
    
    """
    gs_column = DF.col_index(data_file, gs_column_name)
    tk_column = DF.col_index(data_file, tk_column_name)
    DATA = open(data_file)
    
    for i in range(header_rows):
        # advance past header lines
        DATA.readline()
        
    data_items = DATA.readline().split(sep)

    gs, tk = [], []
    
    for timeslice in timeslices:
        tk_buffer = []
#         print timeslice[0], timeslice[1]
        count, gs_sum, tk_sum = 0, 0, 0
        while data_items[0] < timeslice[0]:
            data_items = DATA.readline().split(sep)
            
        while data_items[0] <= timeslice[1]:
            # cover cases where there is not GPS data on every line
            try:
#                 print data_items[0]
                gs_sum += float(data_items[gs_column])
                tk_temp = float(data_items[tk_column])
                tk_buffer.append(tk_temp)
                count += 1
            except ValueError:
                pass
            data_items = DATA.readline().split(sep)
        if max(tk_buffer) - min(tk_buffer) > 180:
            # must have tracks on either side of 360, which will screw up averaging
            tk_buffer2 = []
            for trk in  tk_buffer:
                if trk > 180:
                    tk_buffer2.append(trk-360)
                else:
                    tk_buffer2.append(trk)
        else:
            tk_buffer2 = tk_buffer
        
        gs_ave = gs_sum / count
        # tk_ave = tk_sum / count
        tk_buffer = N.array(tk_buffer2, dtype=float)
        tk_ave = N.average(tk_buffer)

        if tk_ave < 0:
            tk_ave += 360
        
        gs.append(gs_ave)
        tk.append(tk_ave)
        
    # print gs, tk
    # tas_data = gps2tas(gs, tk, verbose = verbose)
    # print tas_data
    
    return gps2tas(gs, tk, verbose = verbose)

def _gt(verbose):
    """
    Test function to exercise pulling data from a file. The function serves
    no practical purpose.
    """
    data_file = 'C:\Documents and Settings\hortonk\Desktop\Python\gps2tas\gps2tas_data_test.txt'
    header_rows = 4
    # timeslices = [('08:41:05', '08:41:19'),  ('08:42:00', '08:42:11'), ('08:42:15', '08:42:23'), ('08:42:30', '08:42:35')]
    timeslices = [('08:41:05', '08:41:19'),  ('08:42:00', '08:42:11'), ('08:42:15', '08:42:23'), ]
    gs_column = 43
    tk_column = 44
    
    print gps_data_file2tas(data_file, header_rows, timeslices, gs_column, tk_column, verbose = verbose)
    




##############################################################################
#
# Distance between points.
#
##############################################################################
def _dist1(lat1, long1, lat2, long2):
    """
    Returns distance in radian between two points given latitudes and 
    longitudes in radians.
    """
    d_rad = 2. * M.asin(M.sqrt((M.sin((lat1 - lat2) /  2.)) ** 2. +   
            M.cos(lat1) * M.cos(lat2) * (M.sin((long1 -  long2) / 2.))  ** 2.))
      
    return d_rad
    
def _dist2(lat1, long1, lat2, long2):
    """
    Returns distance in nm between two points given latitudes and 
    longitudes in degrees.
    """
    lat1 = lat1 * M.pi / 180.
    long1 = long1 * M.pi / 180.
    lat2 = lat2 * M.pi / 180.
    long2 = long2 * M.pi / 180.
    
    d = _dist1(lat1, long1, lat2, long2)
    
    return d * 180. / M.pi * 60.
    
def _parse_ll(value):
    """
    Parses lat or long, and returns value in radians
    
    Legal input formats:
    
    dd:mm:ss
    dd:mm:ss.sss
    dd:mm.mmm
    dd.dddd
    """
    try:
        parts = value.split(':')
        if len(parts) == 3:
            deg, min, sec = parts
            deg = float(deg) + (float(min) + float(sec) / 60) / 60
        elif len(parts) == 2:
            deg, min = parts
            deg = float(deg) + float(min)  / 60
        elif len(parts) == 1:
            deg = float(parts)
    except AttributeError:
        deg = float(value)
#       
#   
#   if len(parts) == 3:
#       deg, min, sec = parts
#       deg = float(deg) + (float(min) + float(sec) / 60) / 60
#   elif len(parts) == 2:
#       deg, min = parts
#       deg = float(deg) + float(min)  / 60
#   elif len(parts) == 1:
#       deg = float(parts)
    
    lat = deg * M.pi / 180.
    
    return lat

def dist(lat1, long1, lat2, long2):
    """
    Returns distance in nm between two points given latitudes and 
    longitudes in degrees:minutes:seconds, or degrees:minutes.
    """
    lat1 = _parse_ll(lat1)
    long1 = _parse_ll(long1)
    lat2 = _parse_ll(lat2)
    long2 = _parse_ll(long2)    
    
    d = _dist1(lat1, long1, lat2, long2)
    
    return d * 180. / M.pi * 60.


##############################################################################
#
# Engine power correction for humidity
#
##############################################################################
def pwr_humid_corr(H, T, DP='FALSE', RH=0.0, alt_units="ft", temp_units='C',
                   base = 'FAR23'):
    """
    Return a power correction factor to account for the effect of humidity.\
    
    power_correction = actual_power / std_day_power, or
    actual_power = std_day_power * power_correction
    
    Note: The temperature input is only used to convert relative humidity to 
    water vapour pressure.the power correction only accounts for the effect 
    of humidity.  It does not account for the effect of non-standard
    temperature on power.  

    If base == 'dry', the correction is with respect to the power that would
    be produced in dry air.  
    
    If base =='FAR23', the correction is with respect to the standard 
    humidity values called for in FAR 23 (80% relative humidity at ISA std 
    temp or colder.  34% relative humidity at ISA + 50 deg F, with linear 
    change in between those values).
    
    The methodology is based on the results reported in NACA Report 426, "The
    Effect of Humidity on Engine Power at Altitude", D.B. Brooks and E.A.
    Garlock, October 1931.  NACA found that the effect of humidity on 
    indicated power (brake hp + friction hp losses) correlated extremely well
    with (air pressure - water vapour pressure)/(air pressure).
    """
    if base == 'dry':
        base_dry_press = SA.alt2press(H, alt_units = alt_units)
    elif base == 'FAR23':
        std_temp = SA.alt2temp(H, alt_units = alt_units, temp_units = 'F')
        T_f = U.temp_conv(T, from_units = temp_units, to_units = 'F')
        if T_f <= std_temp:
            base_RH = 0.8
        elif T_f >= std_temp + 50:
            base_RH = 0.34
        else:
            base_RH = 0.8 + (0.34 - 0.8) * (T_f - std_temp)/50.

        base_water_press = SA.sat_press(T=T, RH = base_RH, 
                                        temp_units = temp_units)
        base_dry_press = SA.dry_press(H, base_water_press, 
                                      alt_units = alt_units)
    else:
        raise ValueError, 'base must be either "FAR23" or "dry".'

    water_press = SA.sat_press(T=T, DP = DP, RH = RH, temp_units = temp_units)
    dry_press = SA.dry_press(H, water_press, alt_units = alt_units)

    power_corr = dry_press / base_dry_press
    
    return power_corr





##############################################################################
#
# Level flight speed vs power corrections to and from standard conditions
#
##############################################################################
def cruise_reduction(cas, pwr, Hp, oat, wt, wt_std, temp_units=default_temp_units, speed_units=default_speed_units, alt_units=default_alt_units):
    """Reduce level flight cas and power to sea level standard day at a standard weight
    
    Return VIW, PIW
    
    cas = the calibrated airspeed at the flight test condition
    pwr = the thrust power required at the flight test condition
    Hp  = the pressure altitude at the flight test condition
    oat = the ambient air temperature at the flight test condition
    wt  = the actual weight at the flight test condition
    wt_std = the standard weight to which the data is to be corrected
    temp_units = temperature units ('F', 'C', 'K', or 'R')
    PIW = power required at sea level, standard day, at standard weight, at 
          the same angle of attack as the flight test point
    VIW = the speed at sea level, standard day, at standard weight, at the 
          same angle of attack as the flight test point.  Note that at sea 
          level, standard day, CAS = EAS = TAS.
    """
    VIW = A.cas2eas(cas, Hp, speed_units=speed_units, alt_units=alt_units) / ((wt / wt_std)**0.5)
    PIW = pwr * (SA.alt_temp2density_ratio(Hp, oat, temp_units=temp_units, alt_units=alt_units)**0.5) / ((wt / wt_std)**1.5)

    return VIW, PIW

#def cruise_fit(CASs, BHPs, Hps, OATs, Wts, wt_std, wt_std, temp_units=default_temp_units, speed_units=default_speed_units, alt_units=default_alt_units):
#    """Reduce a series of raw cruise data points to sea level, std day, std weight conditions and return curve fit.
#    
#    CASs = an array of CASs for each test point
#    BHPs = an array of engine powers for each test point
#    Hps  = an array of pressure altitudes for each test point
#    OATs = an array of OATs for each test point
#    Wts  = an array of aircraft weights for each test point
#    wt_std = the standard weight to which the data is to be corrected
#    temp_units = temperature units ('F', 'C', 'K', or 'R')
#    """
#    V0s = []
#    P0s = []
#    for i, CAS in enumerate(CASs):
#        V0, P0 = cruise_reduction(CAS, BHPs[i], Hps[i], OATs[i], Wts[i], wt_std, temp_units=temp_units, speed_units=speed_units, alt_units=alt_units)
#    V0s = N.array(V0s, dtype=float)
#    P0s = N.array(P0s, dtype=float)
#    X = V0s**4
#    Y = V0s * P0s

def cruise_expansion(VIW, PIW, Hp, oat, wt, wt_std, temp_units=default_temp_units, speed_units=default_speed_units, alt_units=default_alt_units):
    """Expand level flight cas and power from sea level standard day at a standard weight
    
    Return tas, pwr
    
    PIW = power required at sea level, standard day, at standard weight, at 
          the same angle of attack as the desired condition
    VIW = the speed at sea level, standard day, at standard weight, at the 
          same angle of attack as the desired condition. 
    Hp  = the pressure altitude at the desired condition
    oat = the ambient air temperature at the desired condition
    wt  = the actual weight at the desired condition
    wt_std = the standard weight from which the data is to be corrected
    temp_units = temperature units ('F', 'C', 'K', or 'R')
    cas = the calibrated airspeed at the desired condition
    pwr = the thrust power required at the desired condition
    
    """
    sigma = (SA.alt_temp2density_ratio(Hp, oat, temp_units=temp_units, alt_units=alt_units))
    tas = A.eas2tas(VIW * ((wt / wt_std)**0.5), Hp, temp=oat, speed_units=speed_units, alt_units=alt_units, temp_units=temp_units)
    pwr = PIW * (((wt / wt_std)**1.5) / sigma**0.5)
    
    return tas, pwr

##############################################################################
#
# Climb performance data reduction and expansion
#
##############################################################################

def climb_temp_corr(RoC, T, Ts, temp_units="C", expansion=0):
    """Correct observed barometric rate of climb to geometric rate of climb or
    convert geometric rate of climb to barometric rate of climb.
    
    RoC = rate of climb
    T = ambient temperature
    Ts = standard temperature at altitude
    expansion = if 0, this is data reduction.  Convert from barometric rate of climb to geometric rate of climb.
                if 1, whis is data expansion.  Convert from geometric rate of climb to barometric rate of climb.
                
    >>> climb_temp_corr(780, 17, 7.4352)
    806.589228512409
    
    >>> climb_temp_corr(806.589228512409, 17, 7.4352, expansion=1)
    780.0
    """

    T = U.temp_conv(T, temp_units, "K")
    Ts = U.temp_conv(Ts, temp_units, "K")
    
    if expansion == 0:
        return RoC * T/Ts
    else:
        return RoC * Ts/T

def climb_wt_corr(RoC, W, Ws, Ve, sigma, b, e=0.8, RoC_units="ft/mn", weight_units="lb", speed_units="kt", span_units="ft"):
    """Correct rate of climb for change in weight.
    
    RoC = rate of climb
    sigma = density ratio
    W = actual weight
    Ws = standard weight for which rate of climb is desired
    Ve = equivalent airspeed
    b = wing span
    e = Oswald span efficiency
    
    >>> climb_wt_corr(807.6, 2800, 3000, 77.022, .8577, 36, e=.85)
    706.9079451449876
    """

    RoC = U.speed_conv(RoC, RoC_units, "ft/mn")
    W = U.mass_conv(W, weight_units, "lb")
    Ws = U.mass_conv(Ws, weight_units, "lb")
    Ve = U.speed_conv(Ve, speed_units, "ft/s")
    b = U.length_conv(b, span_units, "ft")
    
    RoC_work_corrected = RoC * W/Ws
    Drag_corr1 = 0.5 * 0.0023768924 * M.pi * b**2 * e
    Drag_corr2 = Ws / (Drag_corr1 * Ve * sigma**0.5)
    RoC_drag_corr = (1 - (W / Ws)**2) * Drag_corr2 * 60
    
    RoC_wt_corrected = RoC_work_corrected - RoC_drag_corr

    return RoC_wt_corrected
    
    return RoC_work_corrected - RoC_drag_corr
    
def climb_density_altitude_reduction(Hp, T, RoC_observed, W, Ws, Ve, b, BHP_Hp, BHP_Hd, n, e=0.8, altitude_units="ft", temp_units="C", RoC_units="ft/mn", weight_units="lb", speed_units="kt", span_units="ft"):
    """Reduce rate of climb to standard conditions using density altitude method, as described in FAA AC 23-8B. 
    Return rate of climb and density altitude.
    
    Hp = pressure altitude
    T = ambient temperature
    RoC_observed = observed barometric rate of climb
    W = actual weight
    Ws = standard weight
    Ve = equivalent airspeed
    b = wing span
    BHP_Hp = brake horsepower at test pressure altitude and standard temperature
    BHP_Hd = brake horsepower at test density altitude and standard temperature
    n = assumed propellor efficiency
    e = Oswald span efficiency
    
    >>> climb_density_altitude_reduction(4000, 17, 780, 2800, 3000, 77.022, 36, 203.51, 195, 0.8, e=0.85)
    (662.939768009002, 5151.994046260421)
    """
    Hp = U.length_conv(Hp, altitude_units, "ft")
    T = U.temp_conv(T, temp_units, "K")
    RoC_observed = U.speed_conv(RoC_observed, RoC_units, "ft/mn")
    W = U.mass_conv(W, weight_units, "lb")
    Ws = U.mass_conv(Ws, weight_units, "lb")
    Ve = U.speed_conv(Ve, speed_units, "ft/s")
    b = U.length_conv(b, span_units, "ft")
    
    Ts = SA.alt2temp(Hp, temp_units="K")
    RoC_temp_corrected = climb_temp_corr(RoC_observed, T, Ts, "K")
    sigma = SA.alt_temp2density_ratio(Hp, T, temp_units='K')
    RoC_wt_corrected = climb_wt_corr(RoC_temp_corrected, W, Ws, Ve, sigma, b, e=e, speed_units="ft/s")

    BHP = BHP_Hp * (Ts / T)**0.5
    RoC_pwr_corr = n * (BHP_Hd - BHP) * 33000 / Ws
    Hd = SA.density_ratio2alt(sigma)
    
    return RoC_wt_corrected + RoC_pwr_corr, Hd

def pwr_installed(BHP_rated, MP_observed, Hp_observed, MP_rated = 28.5, MP_off=29.9216, Hp_off=0):
    """Returns predicted installed power at sea level, standard temperature.
    
    BHP_rated = rated horsepower at sea level, standard temperature, from engine power chart
    MP_observed = manifold pressure observed at climb airspeed at full throttle at low altitude
    Hp_observed = pressure altitude at which MP_observed was observed
    MP_rated = manifold pressure at rated power at sea level, from engine power chart.
    MP_off = manifold pressure indication with engine off
    Hp_off = pressure altitude at which MP_off was observed.
    
    **** NOTE: function not yet validated as correct ****
    """
    
    MP_error = MP_off - SA.alt2press(Hp_off)
    MP_observed = MP_observed - MP_error
    MP_loss = SA.alt2press(Hp_observed) - MP_observed
    BHP_installed = BHP_rated * (SA.alt2press(0) - MP_loss) / MP_rated
    
    return BHP_installed

def climb_density_altitude_reduction_simplified(Hp, T, RoC_observed, W, Ws, Ve, b, BHP_Installed, n, e=0.8, C=0.2, altitude_units="ft", temp_units="C", RoC_units="ft/mn", weight_units="lb", speed_units="kt", span_units="ft"):
    """Reduce rate of climb to standard conditions using density altitude 
    method, as described in FAA AC 23-8B, with simplified power calculation. 
    Return rate of climb and density altitude.
    
    Engine power calculation uses Gagg-Farrar power drop-off parametre to 
    predict power at altitude.  Observed low altitude difference between 
    manifold pressure and ambient pressure is used to adjust engine rated 
    power for installation effects.
    
    Hp = pressure altitude
    T = ambient temperature
    RoC_observed = observed barometric rate of climb
    W = actual weight
    Ws = standard weight
    Ve = equivalent airspeed
    b = wing span
    BHP_Installed = installed brake horsepower at sea level and standard temperature
    BHP_Hd = brake horsepower at test density altitude and standard temperature
    n = assumed propellor efficiency
    e = Oswald span efficiency
    
    >>> climb_density_altitude_reduction_simplified(3720, -6.4, 469, 3136.25, 3200, 73, 36, 222, 0.7, e=0.8)
    (468.4277793789483, 2002.725619006603)
    
    
    """
    sigma_Hp = SA.alt2density_ratio(Hp)
    sigma = SA.alt_temp2density_ratio(Hp, T, temp_units=temp_units)
    
    BHP_Hp = P.power_drop_off(sigma_Hp, BHP_Installed, C=C)
    BHP_Hd = P.power_drop_off(sigma, BHP_Installed, C=C)
    
    return climb_density_altitude_reduction(Hp, T, RoC_observed, W, Ws, Ve, b, BHP_Hp, BHP_Hd, n, e=e, altitude_units=altitude_units, temp_units=temp_units, RoC_units=RoC_units, weight_units=weight_units, speed_units=speed_units, span_units=span_units)

def climb_equivalent_altitude_reduction(Hp, T, RoC_observed, W, Ws, Ve, b, e=0.8, altitude_units="ft", temp_units="C", RoC_units="ft/mn", weight_units="lb", speed_units="kt", span_units="ft"):
    """Reduce rate of climb to standard conditions using equivalent altitude method, as described in FAA AC 23-8B. 
    Return rate of climb and density altitude.
    
    Hp = pressure altitude
    T = ambient temperature
    RoC_observed = observed barometric rate of climb
    W = actual weight
    Ws = standard weight
    Ve = equivalent airspeed
    b = wing span
    e = Oswald span efficiency
    
    >>> climb_equivalent_altitude_reduction(4000, 17, 780, 2800, 3000, 77.022, 36,  e=0.85)
    (706.931926638537, 4414.717856653751)
    """
    Hp = U.length_conv(Hp, altitude_units, "ft")
    T = U.temp_conv(T, temp_units, "K")
    RoC_observed = U.speed_conv(RoC_observed, RoC_units, "ft/mn")
    W = U.mass_conv(W, weight_units, "lb")
    Ws = U.mass_conv(Ws, weight_units, "lb")
    Ve = U.speed_conv(Ve, speed_units, "ft/s")
    b = U.length_conv(b, span_units, "ft")

    Ts = SA.alt2temp(Hp, temp_units="K")
    RoC_temp_corrected = climb_temp_corr(RoC_observed, T, Ts, "K")
    sigma = SA.alt_temp2density_ratio(Hp, T, temp_units='K')
    RoC_wt_corrected = climb_wt_corr(RoC_temp_corrected, W, Ws, Ve, sigma, b, e=e, speed_units="ft/s")
    Hd = SA.density_ratio2alt(sigma)
    
    He = Hp - 0.36 * (Hp - Hd)
    
    return RoC_wt_corrected, He
    
##############################################################################
#
# Fixed pitch prop TAS correction for temperature
#
##############################################################################
# Add someday

if __name__ == "__main__":
    # run doctest to check the validity of the examples in the doc strings.
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
