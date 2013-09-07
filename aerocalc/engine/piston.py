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
# version 0.02, 03 June 2010
#
# Version History:
# vers     date     Notes
# 0.01   14 Jul 09  First release.
# 0.02   03 Jun 10  Added BMEP and CR_corr functions
#
# #############################################################################
#
# To Do: 1. 
#
#
# Done:  1. 
#
# #############################################################################
"""Functions that are applicable to all piston engines.
"""

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

import unit_conversion as U

def power_drop_off(sigma, pwr0, C=0.12):
    """
    Returns power as a function of density ratio, sea level standard day power 
    and the Gagg-Farrar power drop-off parametre.
    
    sigma = density ratio
    pwr0  = power at sea level standard day conditions
    C     = Gagg-Farrar power drop-off parametre = ratio of friction power to 
            indicated power at sea level standard day conditions.  Typically
            about 0.12 for Lycoming and Continental horizontally opposed, 
            direct drive, non-supercharged engines.
    """
    
    return pwr0 * (sigma - C) / ( 1 - C)

def BMEP(bhp, rpm, disp, power_units=default_power_units, vol_units=default_vol_units, press_units=default_press_units):
    """
    Return brake mean effective pressure, given brake power, rpm and displacement.
    
    Rpm is revolutions per minute.
    """
    bhp = U.power_conv(bhp, power_units, 'hp')
    disp = U.vol_conv(disp, vol_units, 'in**3')
    bmep = 2 * bhp * 33000. * 12 / (rpm * disp)

    return bmep

def CR_corr(pwr1, CR1, CR2, K=1.27):
    """
    Returns engine power corrected for change in compression ratio.
    
    pwr1 = Engine power with CR1
    CR1  = Compression ratio for engine that produces pwr1
    CR2  = Compression ratio for which predicted power is returned
    K    = Ratio of specific heats of combustion gases
           K = 1.4 for pure air
           K = about 1.27 for typical combustion gases, from:
               http://courses.washington.edu/me341/oct22v2.htm
    """
    pwr2 = pwr1 * (1 - 1./(CR2**(K-1))) / (1 - 1./(CR1**(K-1)))
    
    return pwr2
