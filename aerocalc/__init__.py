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
# version 0.13, 30 Jun 2009
#
# Version History:
# vers     date      Notes
# 0.10   17 Mar 08   Initial version.
#
# 0.11   25 Apr 08   Added ssec module (mostly empty yet)
# 0.12   24 Nov 08   Added cd and cl modules.  Bug fixes in other modules.
# 0.13   30 Jun 09   * Python 3.0 compatibility.  
#                    * Added airspeed_p3k and val_input_p3k modules to address
#                      aspects that had no easy solution that was compatible 
#                      with both python 2.5 and python 3.0.
#                    * Removed "from __future__ import division" statements 
#                      from most files for python 3.0 compatibility (bug in
#                      python 3.0 causes doctest failures in presence of
#                      "from __future__ import division" statement).
#                   * Added some meat to SSEC module
#                   * Added interpolator module, with functions for linear
#                     interpolation in one, two or three dimensions
#
# #############################################################################
#
# Distribution Notes
#
# HTML docs are created with epydoc, via
# "epydoc --no-private -n AeroCalc -u 'http://www.kilohotel.com/python/aerocalc/' aerocalc"
#
# Generate distribution - "python setup.py sdist"
#
# #############################################################################

"""Various aeronautical engineering calculations

This package contains the following modules:

airspeed        - airspeed conversions and calculations.  Provides interactive
                  mode when run directly, e.g. 'python airspeed.py'
airspeed_p3k    - Python 3 compatible variant of airspeed module.
default_units   - defines default units to be used by all modules.  May be 
                  overridden by a user units file.
cd              - drag related calculations.
cl              - lift related calculations.
constants       - constants used by all modules.
interpolator    - linear interpolation in one, two or three dimensions
ssec            - static source error correction calculations.
std_atm         - standard atmosphere parametres and calculations.
unit_conversion - convert various aeronautical parametres between commonly
                  used units.
val_input       - validates user input when in interactive mode.
val_input_p3k   - Python 3 compatible variant of val_input module.

Author: Kevin Horton
E-mail: kevin01 -at- kilohotel.com
"""

VERSION = '0.13'

