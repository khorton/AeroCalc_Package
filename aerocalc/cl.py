#!/usr/bin/env python
# -*- coding: utf-8 -*-

# #############################################################################
# Copyright (c) 2008, Kevin Horton
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
# #############################################################################
#
# version 0.11, 30 Jun 2009
#
# Version History:
# vers     date     Notes
# 0.10   04 May 08  First public release.
# 0.11   30 Jun 09  Python 3.0 compatibility.  Removed from __future__ 
#                   import division
# #############################################################################
#
# To Do:  1. Add doctests or unit tests for all functions.
#
# #############################################################################


"""
Various functions related to lift coefficients.
"""

import airspeed as A
import std_atm as S
import unit_conversion as U
import constants

try:
    from default_units import *
except ImportError:
    default_area_units = 'ft**2'
    default_power_units = 'hp'
    default_speed_units = 'kt'
    default_temp_units = 'C'
    default_weight_units = 'lb'
    default_press_units = 'in HG'
    default_density_units = 'lb/ft**3'
    default_length_units = 'ft'
    default_alt_units = default_length_units
    default_avgas_units = 'lb'

Rho0 = constants.Rho0  # Density at sea level, kg/m**3
A0 = constants.A0  # speed of sound at sea level, std day, m/s
g = constants.g

# #############################################################################
#
# eas2cl
#
# calculate lift coefficient, given EAS
#
# #############################################################################


def eas2cl(
    eas,
    weight,
    wing_area,
    load_factor=1,
    speed_units=default_speed_units,
    weight_units=default_weight_units,
    area_units=default_area_units,
    ):
    """
    Returns the coefficient of lift, given equivalent airspeed, weight, and 
    wing area.
    
    Load factor is an optional input.  The load factor, if not provided, 
    defaults to 1.
    
    Example:
    if the wing area is 110 square feet,
    and the weight is 1800 lb,
    and the eas is 55 kt,
    in straight and level flight (so the load factor = 1),
    
    then:
    >>> S = 110
    >>> W = 1800
    >>> EAS = 55
    >>> eas2cl(EAS, W, S, speed_units='kt', weight_units='lb', area_units='ft**2')
    1.597820083228606
    """

    eas = U.speed_conv(eas, from_units=speed_units, to_units='m/s')
    weight = U.wt_conv(weight, from_units=weight_units, to_units='kg')
    wing_area = U.area_conv(wing_area, from_units=area_units,
                            to_units='m**2')

    Cl = (((2. * weight) * g) * load_factor) / ((Rho0 * wing_area) * eas
             ** 2.)

    return Cl


# #############################################################################
#
# cas2cl
#
# calculate lift coefficient, given CAS
#
# #############################################################################


def cas2cl(
    cas,
    altitude,
    weight,
    wing_area,
    load_factor=1,
    speed_units=default_speed_units,
    alt_units=default_alt_units,
    weight_units=default_weight_units,
    area_units=default_area_units,
    ):
    """
    Returns the coefficient of lift, given calibrated airspeed, altitude, 
    weight, and wing area.  
    
    Load factor is an optional input.  The load factor, if not provided, 
    defaults to 1.

    Example:
    if the wing area is 15 square meters,
    and the weight is 1500 kg,
    and the cas is 200 km/h,
    at 3,000 meter altitude
    in a stabilized 45 degree bank turn (so the load factor = 2**0.5),

    >>> S = 15
    >>> W = 1500
    >>> CAS = 200
    >>> Alt = 3000
    >>> cas2cl(CAS, Alt, W, S, load_factor = 2**0.5, speed_units='km/h',\
    alt_units='m', weight_units='kg', area_units='m**2') 
    0.73578131117130885
    
    """

    eas = A.cas2eas(cas, altitude, speed_units, alt_units)

    Cl = eas2cl(
        eas,
        weight,
        wing_area,
        load_factor,
        speed_units,
        weight_units,
        area_units,
        )

    return Cl


# ############################################################################
#
# mach2cl
#
# calculate lift coefficient, given mach
#
# ############################################################################

def mach2cl(
    mach,
    altitude,
    weight,
    wing_area,
    load_factor=1,
    alt_units=default_alt_units,
    weight_units=default_weight_units,
    area_units=default_area_units,
    ):
    """
    """
    
    P = S.alt2press(altitude, alt_units=alt_units, press_units="pa")
    wing_area=U.area_conv(wing_area, from_units=area_units, to_units="m**2")
    weight=U.wt_conv(weight, from_units=weight_units, to_units="kg")
    
    Cl  = (weight * g * load_factor) / (0.7 * P * wing_area * mach**2)
    
    return Cl
    
# #############################################################################
#
# tas2cl
#
# calculate lift coefficient, given TAS
#
# #############################################################################


def tas2cl(
    tas,
    altitude,
    weight,
    wing_area,
    temperature='std',
    load_factor=1,
    speed_units=default_speed_units,
    alt_units=default_alt_units,
    temp_units=default_temp_units,
    weight_units=default_weight_units,
    area_units=default_area_units,
    ):
    """
    Returns the coefficient of lift, given true airspeed, altitude, weight, 
    and wing area.  
    
    Temperature and load factor are optional inputs.  The temperature, if 
    not provided, defaults to the standard temperature for the altitude.  
    The load factor, if not provided, defaults to 1.
    """

    eas = A.tas2eas(
        tas,
        altitude,
        temperature,
        speed_units,
        alt_units,
        temp_units,
        )

    Cl = eas2cl(
        eas,
        weight,
        wing_area,
        load_factor,
        speed_units,
        weight_units,
        area_units,
        )

    return Cl


# #############################################################################
#
# cl2eas
#
# calculate EAS, given lift coefficient
#
# #############################################################################


def cl2eas(
    Cl,
    weight,
    wing_area,
    load_factor=1,
    speed_units=default_speed_units,
    weight_units=default_weight_units,
    area_units=default_area_units,
    ):
    """
    Returns the equivalent airspeed, given coefficient of lift, weight, and 
    wing area.

    Load factor is an optional input.  The load factor, if not provided, 
    defaults to 1.
    """

    weight = U.wt_conv(weight, from_units=weight_units, to_units='kg')
    wing_area = U.area_conv(wing_area, from_units=area_units,
                            to_units='m**2')

    eas = ((((2. * weight) * g) * load_factor) / ((Rho0 * wing_area)
            * Cl)) ** 0.5
    eas = U.speed_conv(eas, from_units='m/s', to_units=speed_units)
    return eas


# #############################################################################
#
# cl2cas
#
# calculate CAS, given lift coefficient
#
# #############################################################################


def cl2cas(
    Cl,
    altitude,
    weight,
    wing_area,
    load_factor=1,
    speed_units=default_speed_units,
    alt_units=default_alt_units,
    weight_units=default_weight_units,
    area_units=default_area_units,
    ):
    """
    Returns the calibrated airspeed, given coefficient of lift, altitude, 
    weight, and wing area.

    Load factor is an optional input.  The load factor, if not provided, 
    defaults to 1.
    """

    weight = U.wt_conv(weight, from_units=weight_units, to_units='kg')
    wing_area = U.area_conv(wing_area, from_units=area_units,
                            to_units='m**2')

    eas = ((((2. * weight) * g) * load_factor) / ((Rho0 * wing_area)
            * Cl)) ** 0.5
    eas = U.speed_conv(eas, from_units='m/s', to_units=speed_units)
    cas = A.eas2cas(eas, altitude, speed_units, alt_units)

    return cas


# #############################################################################
#
# cl2tas
#
# calculate TAS, given lift coefficient
#
# #############################################################################


def cl2tas(
    Cl,
    altitude,
    weight,
    wing_area,
    temperature='std',
    load_factor=1,
    speed_units=default_speed_units,
    alt_units=default_alt_units,
    weight_units=default_weight_units,
    area_units=default_area_units,
    temp_units=default_temp_units,
    ):
    """
    Returns the true airspeed, given coefficient of lift, altitude, weight,
    and wing area.
    
    Temperature and load factor are optional inputs.  The temperature, if 
    not provided, defaults to the standard temperature for the altitude.  
    The load factor, if not provided, defaults to 1.
    """

    weight = U.wt_conv(weight, from_units=weight_units, to_units='kg')
    wing_area = U.area_conv(wing_area, from_units=area_units,
                            to_units='m**2')

    eas = ((((2. * weight) * g) * load_factor) / ((Rho0 * wing_area)
            * Cl)) ** 0.5
    eas = U.speed_conv(eas, from_units='m/s', to_units=speed_units)
    tas = A.eas2tas(
        eas,
        altitude,
        temperature,
        speed_units,
        alt_units,
        temp_units=temp_units,
        )

    return tas


# #############################################################################
#
# cl2lift
#
# calculate lift, given drag coefficient, eas and weight
#
# #############################################################################


def cl2lift(
    Cl,
    eas,
    wing_area,
    speed_units=default_speed_units,
    lift_units=default_weight_units,
    area_units=default_area_units,
    ):
    """
    Returns the lift, given coefficient of lift, equivalent airspeed, and wing
    area.
    """

    eas = U.speed_conv(eas, from_units=speed_units, to_units='m/s')
    wing_area = U.area_conv(wing_area, from_units=area_units,
                            to_units='m**2')

    lift = (((0.5 * Rho0) * eas ** 2.) * wing_area) * Cl
    if lift_units == 'kg':
        lift = U.force_conv(lift, 'N', 'lb')
        lift = U.mass_conv(lift, 'lb', 'kg')
    else:
        lift = U.force_conv(lift, 'N', lift_units)

    return lift

if __name__ == '__main__':  # pragma: no cover

    # run doctest to check the validity of the examples in the doc strings.

    import doctest
    import sys
    doctest.testmod(sys.modules[__name__])

