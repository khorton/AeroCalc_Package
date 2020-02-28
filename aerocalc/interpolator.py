#!/usr/bin/env python3
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
# version 0.20, 26 Feb 2019
#
# Version History:
# vers     date     Notes
# 0.10   30 Jun 09  First public release.
# 0.20   26 Feb 19  Python 3.7 compatibility tweaks
# #############################################################################

"""
Provides functions to perform linear interpolation in one, two or three
dimensions.
"""

def interpolate(x, y, x1):
	"""
	Returns y1 that is the interpolated y value for x1, given two lists of
	x and y values.

    Example:

    if the x values are:
	x = [13000, 13500]
    and the corresponding y values are:

	y = [2000, 25O0]
	and we want to know the interpolated y value for x = 13100: 
    >>> x = [13000, 13500]
    >>> y = [2000, 2500]
    >>> x1 = 13100
    >>> interpolate(x, y, x1)
    2100.0
	"""
	for item in x:
		item = float(item)
	for item in y:
		item = float(item)
	x1 = float(x1)
	  
	y1 = y[0] + (x1 - x[0]) / (x[1] - x[0]) * (y[1] - y[0])
	
	return y1


def interpolate2(x, y, z, x1, y1):
	"""
	Two-dimensional interpolation.
	
	Returns z1 value that is the interpolated z value for x1 and y1, given
	three lists of x, y, and z values.
	
	The z list has two items, with each being a list of two items.  E.g.:
	
	z = [[1, 2], [3, 4]]
	

    Example:

    if the x and y values are:
	x = [13000, 13500]
	y = [10, 20]
	
	and, the z value for x, y of 13000, 10 = 2000, 
	the z value for x, y of 13500, 10 = 2500, 
	the z value for x, y of 13000, 20 = 2200, and
	the z value for x, y of 13500, 20 = 2700, then
	
	z = [[2000, 2500],[2200, 2700]]
	
	if we want to find the z value for x, y = 1310, 12:
	
    >>> x = [13000, 13500]
    >>> y = [10, 20]
    >>> z = [[2000, 2500],[2200, 2700]]
    >>> x1 = 13100
    >>> y1 = 12
    >>> interpolate2(x, y, z, x1, y1)
    2140.0
	"""
	y11 = interpolate(x, z[0], x1)
	y22 = interpolate(x, z[1], x1)
	
	z1 = interpolate(y, [y11, y22], y1)
	
	return z1

def interpolate3(x, y, z, v, x1, y1, z1):
	"""
	Three-dimensional interpolation.
	
	Returns v1 value that is the interpolated v value for x1, y1 and z1, 
	given four lists of x, y, and z values and the corresponding v values.
	
	The v list has two items, with each being a list of two lists.  E.g.:
	
	v = [[[1, 2], [3, 4]], [[5, 6], [7, 8]]]
	
    Example:

	if the x, y and z values are:
	x = [13000, 13500]
	y = [10, 20]
	z = [90, 95]
	
	and, the v value for x, y, z of 13000, 10, 90 = 2000, 
	the v value for x, y, z of 13500, 10, 90 = 2500, 
	the v value for x, y, z of 13000, 20, 90 = 2200, 
	the v value for x, y, z of 13500, 20, 90 = 2700,
	the v value for x, y, z of 13000, 10, 95 = 3000, 
	the v value for x, y, z of 13500, 10, 95 = 3500, 
	the v value for x, y, z of 13000, 20, 95 = 3200, 
	the v value for x, y, z of 13500, 20, 95 = 3700, then
	
	v = [[[2000, 2500],[2200, 2700]], [[3000, 3500],[3200, 3700]]]

	if we want to find the v value for x, y, z = 13250, 15, 92.5:

    >>> x = [13000, 13500]
    >>> y = [10, 20]
    >>> z = [90, 95]
    >>> v = [[[2000, 2500],[2200, 2700]], [[3000, 3500],[3200, 3700]]]
    >>> x1 = 13100
    >>> y1 = 12
    >>> z1 = 91
    >>> interpolate3(x, y, z, v, x1, y1, z1)
    2340.0

	"""
	z11 = interpolate2(x, y, v[0], x1, y1)
	z22 = interpolate2(x, y, v[1], x1, y1)
	
	v1 = interpolate(z, [z11, z22], z1)
	
	return v1


if __name__ == '__main__':  # pragma: no cover

    # run doctest to check the validity of the examples in the doc strings.

    import doctest
    import sys
    doctest.testmod(sys.modules[__name__])

