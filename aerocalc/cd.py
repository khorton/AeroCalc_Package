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
# 0.10   09 May 08  First public release.
# 0.11   30 Jun 09  Python 3.0 compatibility.  Removed "from __future__ 
#                   import division"
# #############################################################################

"""
Various functions related to drag coefficients.
"""

# import airspeed as A
import cl
import math as M
# import std_atm as SA
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
# cl2cd
#
# calculate drag coefficient, given lift coefficient and drag polar
#
# #############################################################################


def cl2cd(Cl, Cd0, AR, e):
    """
    Returns drag coefficient, given lift coefficient, profile drag coefficient
    aspect ratio and span efficiency.
    
    Cl  = lift coefficient
    Cd0 = profile drag coefficient (the drag coefficient at zero lift)
    AR  = aspect ratio (the square of wing span / wing area, which for a
          rectangular wing is equivalent to wing span / wing chord).
    e   = span efficiency
    
    This representation of drag does not account for wave drag, so it is not 
    valid at high speed.  It also is only valid in the range of angle of 
    attack where lift changes linearly with angle of attack.  It does not 
    account for the effect of trim drag, so the predicted drag takes no
    account for aircraft centre of gravity.
    
    Example:
    >>> cl2cd(1.2, 0.0221, 4.8, 0.825)
    0.13784904952137844
    """

    Cd = Cd0 + Cl ** 2 / ((M.pi * e) * AR)

    return Cd


# #############################################################################
#
# cd2drag
#
# calculate drag, given drag coefficient, eas and weight
#
# #############################################################################


def cd2drag(
    Cd,
    eas,
    wing_area,
    speed_units=default_speed_units,
    area_units=default_area_units,
    drag_units=default_weight_units,
    ):
    """
    Returns the drag, given coefficient of drag, equivalent airspeed, and wing
    area.
    
    Example:
    >>> cd2drag(.138, 100, 10, speed_units='km/h', area_units='m**2',\
    drag_units='N')
    652.19907407407425
    """

    eas = U.speed_conv(eas, from_units=speed_units, to_units='m/s')
    wing_area = U.area_conv(wing_area, from_units=area_units,
                            to_units='m**2')

    drag = (((0.5 * Rho0) * eas ** 2) * wing_area) * Cd
    drag = U.force_conv(drag, from_units='N', to_units=drag_units)

    return drag


# #############################################################################
#
# eas2drag
#
# calculate drag, given eas, weight, wing area, Cd0, aspect ratio, span efficiency and load factor
#
# #############################################################################


def eas2drag(
    eas,
    weight,
    wing_area,
    Cd0,
    AR,
    e,
    load_factor=1,
    speed_units=default_speed_units,
    weight_units=default_weight_units,
    area_units=default_area_units,
    drag_units=default_weight_units,
    ):

    """
    Returns drag, given EAS, weight, wing area, profile drag coefficient, 
    aspect ratio, span efficiency and load factor.
    
    Cl  = lift coefficient
    Cd0 = profile drag coefficient (the drag coefficient at zero lift)
    AR  = aspect ratio (the square of wing span / wing area, which for a
          rectangular wing is equivalent to wing span / wing chord).
    e   = span efficiency

    This representation of drag does not account for wave drag, so it is not 
    valid at high speed.  It also is only valid in the range of angle of 
    attack where lift changes linearly with angle of attack.  It does not 
    account for the effect of trim drag, so the predicted drag takes no
    account for aircraft centre of gravity.
    
    Example:
    >>> eas2drag(120, 700, 110, 0.0221, 4.8, 0.825, speed_units='mph', \
    weight_units='kg', area_units='ft**2', drag_units='lb')
    136.76711702310882
    """

    Cl = cl.eas2cl(
        eas,
        weight,
        wing_area,
        load_factor,
        speed_units,
        weight_units,
        area_units,
        )
    Cd = cl2cd(Cl, Cd0, AR, e)
    drag = cd2drag(
        Cd,
        eas,
        wing_area,
        speed_units,
        area_units,
        drag_units,
        )

    return drag

def drag2drag_area(drag, eas, drag_units=default_weight_units, speed_units=default_speed_units):
    """
    Returns equivalent flat plate area given drag and EAS.
    """

    return

if __name__ == '__main__':  # pragma: no cover

    # run doctest to check the validity of the examples in the doc strings.

    import doctest
    import sys
    doctest.testmod(sys.modules[__name__])

