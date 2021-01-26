#!/usr/bin/env python3

# #############################################################################
# Copyright (c) 2014, Kevin Horton
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
# version 0.20, 28 Feb 2020
#
# Version History:
# vers   date         Notes
# 0.10   11 Nov 2014  First public release.
# 0.20   28 Feb 2020  Python 3 compatibility
#
# #############################################################################
#
# To Do: 
#
# Done:  1. 
#
# #############################################################################

import airspeed as A
import ssec as SSEC
import unit_conversion as U

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


def gps2stall(GS, TK, Hp, T, temp_units='C', alt_units=default_alt_units, speed_units=default_speed_units, GPS_units=default_speed_units):
    """
    Return the CAS at the stall, given four GPS ground speeds, GPS tracks, 
    altitude and temperature.
    
    speed_units = CAS units.  May be 'kt', 'mph', 'km/h', 'm/s' and 'ft/s'.
    GS_units = GPS ground speed units.  'kt', 'mph', 'km/h', 'm/s' and 'ft/s'.
    HP = pressure altitude.  May be feet ('ft'), metres ('m'), kilometres ('km'), 
    statute miles, ('sm') or nautical miles ('nm').

    The temperature may be in deg C, F, K or R. 

    If the units are not specified, the units in default_units.py are used.
    
    Conduct four stalls, in a four sided box pattern, with all stalls at the same
    pressure altitude.  The data reduction algorithm calculates the TAS using Doug
    Gray's GPS to TAS method, using four different combinations of three legs.  If
    the data quality is high, all four TAS values will be similar, with a low standard
    deviation.
    
    The TAS at the stall is converted to CAS, using pressure altitude and 
    temperature.
    
    Returns CAS and standard deviation of the CAS value.
    
    Examples:
    
    >>> gps2stall([44, 104, 157, 131], [258, 29, 91, 150], 7000, 14, temp_units='F', GPS_units='km/h')
    (50.322235245211225, 0.6583323098888626)

    """


    tas, std_dev = SSEC.gps2tas(GS, TK, verbose=1)
    tas = U.speed_conv(tas, from_units=GPS_units, to_units=speed_units)
    std_dev = U.speed_conv(std_dev, from_units=GPS_units, to_units=speed_units)
    cas = A.tas2cas(tas, Hp, T, temp_units=temp_units, alt_units=alt_units, speed_units=speed_units)
    std_dev = std_dev * cas / tas # factor standard deviation to reference CAS vs TAS

    return cas, std_dev
