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
# version 0.24, 02 Mar 2012
#
# Version History:
# vers     date     Notes
#  0.1   27 Nov 08  First release.
#
# 0.11   01 May 09  Cleaned up documentation.
#
# 0.2    24 May 09  Added fixed pitch prop variant of power from fuel flow
#
# 0.21   24 Oct 10  Added data for 10:1 CR
#
# 0.22   31 Oct 10  Added approximate friction hp data for 290, 340, 375, 390 and 400 in**3 engines
#
# 0.23   11 Mar 11  Corrected notes by removing reference to temperature
#
# 0.24   02 Mar 12  Add pwr2ff
# #############################################################################
#
# To Do: 1. Done
#
#        2. Add tests.
#
#        3. Implement alternate method described in Lycoming doc
#
#        4. Done
#
#        5. Implement approximation for arbitrary compression ratios
#
# Done:  1. Implement 10.0 CR
#        4. Implement approximation for 390 cubic inches
#
# #############################################################################
"""Calculate Lycoming engine power, based on fuel flow data.

This module implements a power determination method described in an old
internal Lycoming document, intended for use during flight testing.  It
calculates engine power from inputs of fuel flow, fuel flow at peak EGT,
rpm, compression ratio, engine displacement, and geared vs ungeared engine.
"""


from __future__ import division

import piston as P
import std_atm as SA
import unit_conversion as U
import math as M
# import numpy as N # only needed in solve_pwr_vs_ff(), which was used during 
                    # development.  this function has been commented out.


def power(ff, ff_at_pk_EGT, rpm, CR=8.7, displacement=360, ff_units='USG/h', fric_power_factor=1):
    """
    Returns engine power, based on fuel flow data.  Based on an internal 
    Lycoming document, apparently for use during flight test programs.
    
    ff           = fuel flow
    ff_at_pk_EGT = fuel flow at peak EGT
    rpm          = engine speed
    CR           = compression ratio.  Allowable values are 6.75, 7, 7.2, 
                   7.3, 8, 8.5, 8.7 or 9 (10 to be implemented later).
    displacement = engine displacement in cubic inches.  Allowable values are
                   235, 320, 360, 480, 480S, 540, 540S, 541 or 720.  
                   The suffix S denotes GSO or IGSO engines.
    # type         = type of fuel delivery system.  Allowable values are 
    #                'port_injection', 'carb', and 'single_point' (i.e fuel 
    #                injected at a single point, prior to the intake tubes). 
    #                This input is not yet implemented, as it is only needed
    #                for an alternate method, for high power conditions where
    #                it is not safe to lean to peak EGT.
    ff_units     = fuel flow units.  Allowable values are 'USG/h', 'ImpGal/h', 
                   'l/h', 'lb/h', and 'kg/h'
    """
    ff_units = ff_units[:-2]
    ff = U.avgas_conv(ff, from_units=ff_units, to_units='lb')
    ff_at_pk_EGT = U.avgas_conv(ff_at_pk_EGT, from_units=ff_units, to_units='lb')
    ff_best_mixture = ff_at_pk_EGT / .849
    SFC_best_mixture = iSFC(CR)
    best_mixture_pwr = ff_best_mixture / SFC_best_mixture
    ihp = best_mixture_pwr * pwr_ratio_vs_ff_ratio(ff / ff_best_mixture)
    try:
        imep = P.BMEP(best_mixture_pwr, rpm, displacement, power_units='hp', vol_units='in**3')
        disp_numeric = displacement
    except TypeError:
        disp_numeric = int(displacement[:3])
        imep = P.BMEP(best_mixture_pwr, rpm, disp_numeric, power_units='hp', vol_units='in**3')

    if imep < 140:
        imep_best_pwr = imep
        for n in range(10):
            SFC_best_mixture = iSFC(CR, imep_best_pwr)
            best_mixture_pwr = ff_best_mixture / SFC_best_mixture
            imep_best_pwr = P.BMEP(best_mixture_pwr, rpm, disp_numeric, power_units='hp', vol_units='in**3')
            # print 'iSFC = %.4f' % SFC_best_mixture
        ihp = best_mixture_pwr * pwr_ratio_vs_ff_ratio(ff / ff_best_mixture)

    bhp = ihp - friction_hp(displacement, rpm) * fric_power_factor

    return bhp

def power_fp(
    ff,
    ff_at_pk_EGT,
    rpm,
    rpm_at_pk_EGT,
    # intake_temp = 288.15,
    CR=8.7,
    displacement=360,
    # type='port_injection',
    ff_units='USG/h',
#    temp_units='F',
    ):
    """
    Returns engine power, based on fuel flow data.  This is an extension
    to fixed-pitch props of on an internal Lycoming document, apparently 
    for use during flight test programs.
    
    ff            = fuel flow
    ff_at_pk_EGT  = fuel flow at peak EGT
    rpm           = engine speed (n/mn)
    rpm_at_pk_EGT = engine speed at peak EGT
    CR            = compression ratio.  Allowable values are 6.75, 7, 7.2, 
                    7.3, 8, 8.5, 8.7 or 9 (10 to be implemented later).
    displacement  = engine displacement in cubic inches.  Allowable values are
                    235, 320, 360, 480, 480S, 540, 540S, 541 or 720.  
                    The suffix S denotes GSO or IGSO engines.
    # type          = type of fuel delivery system.  Allowable values are 
    #                 'port_injection', 'carb', and 'single_point' (i.e fuel 
    #                 injected at a single point, prior to the intake tubes). 
    #                 This input is not yet implemented, as it is only needed
    #                 for an alternate method, for high power conditions where
    #                 it is not safe to lean to peak EGT.
    ff_units      = fuel flow units.  Allowable values are 'USG/h', 'ImpGal/h', 
                   'l/h', 'lb/h', and 'kg/h'
    """
    ff_at_pk_EGT *= rpm / rpm_at_pk_EGT
    
    return power(ff, ff_at_pk_EGT, rpm, CR, displacement, ff_units=ff_units)



def power_lop(ff, n, ff_units='USG/h'):
    """
    Alternate, very simplified and approximate method to determine power, for 
    lean of peak operations.  Optimized for operations at 50 deg F lean of 
    peak on Lycoming IO-360A series engines.  This was a trial, and initial 
    testing suggests this function is not adequately accurate.
    """
    ff_units = ff_units[:-2]
    ff = U.avgas_conv(ff, from_units=ff_units, to_units='USG')

    a, b, c, d, e, f, g, h, i = [4.61824610e+00,  -7.90382136e-01,  -4.09623195e-03,   7.58928066e-04,
      -3.51093492e-05,  -1.87325980e-07,   8.64253036e-09,   3.65001722e-02,
       1.02174312e-06]    
    sfc = a + b * ff + c * n + d * ff * n + e * ff**2 * n + f * ff * n**2 + g * ff**2 * n**2 + h * ff**2 + i * n**2
    pwr = ff * 6.01 / sfc
    
    return pwr


def power_alt(ff, n, Hp, OAT, k=.00283, k2=.007, ff_units='USG/h', temp_units = 'F'):
    """
    Alternate, simplified method to determine power.  Assume that the fuel 
    flow for peak EGT varies linearly with density ratio and rpm.  Then use 
    the main power method to calculate power for cases where there is not a 
    good indication of fuel flow at peak EGT.  Only applicable to Lycoming 
    IO-360A series engines.  Based on a very limited set of flight test data, 
    so the accuracy of the fuel flow at peak EGT has not been established 
    under all conditions.
    """
    oat = U.temp_conv(OAT, from_units='F', to_units='R')
    dr = SA.alt_temp2density_ratio(Hp, OAT, temp_units='F')
    ff_peak_EGT = k * dr * n + k2 * oat
    p = power(ff, ff_peak_EGT, n)
    
    return p

def ffp(Hp, OAT, n, k=.00283, k2=.007):
    oat = U.temp_conv(OAT, from_units='F', to_units='R')
    dr = SA.alt_temp2density_ratio(Hp, OAT, temp_units='F')
    ff_peak_EGT = k * dr * n + k2 * oat
    return ff_peak_EGT

# def solve_pwr_vs_ff():
#     """
#     Create fit to power vs fuel flow data
#     """
#     data = [(.74, .86), (.77, .9), (.8125, .94), (.85, .963), (.9, .981), (.925, .988), (.95, .994), (.975, .998), (1., 1.), (1.025, 1.), (1.05, 1.), (1.075, 1.), (1.1, .999), (1.125, .998), (1.2, .989), (1.3, .976), (1.4, .959), (1.5, .933), (1.55, .914)]
#     ff_ratios = []
#     pwr_ratios = []
#     for point in data:
#         ff_ratios.append(point[0])
#         pwr_ratios.append(point[1])
#     ff_ratios = N.array(ff_ratios)
#     pwr_ratios = N.array(pwr_ratios)
#     
#     i = 9
#     # print ff_ratios[:i], pwr_ratios[:i]
#     fit_low, P_low = LGP.lst_sq_fit3(ff_ratios[:i], pwr_ratios[:i], params=True)
#     print fit_low, '\n'
#     print P_low, '\n'
# 
#     i = 9
#     # print ff_ratios[i:], pwr_ratios[i:]
#     response=[]
#     fit_high, P_high = LGP.lst_sq_fit4(ff_ratios[i:], pwr_ratios[i:], params=True)
#     print fit_high, '\n'
#     print P_high, '\n'

def pwr2ff(p, n, ffp_ratio = 1.2, CR=8.7, displacement=360, ff_units='USG/h', fric_power_factor=1, verbose =0):
    """
    Returns fuel flow for a given power, rpm, etc
    
    p = power
    n = rpm
    ffp_ratio = fuel flow / fuel flow at peak EGT (typically 1.2 for best 
                power, and about 0.9 for 50 deg F LOP)
    
    ffp_ratio may be specified as a numerical value or 'ROP' or 'LOP', which 
    are defined as 1.2 and 0.9 respectively.
    """
    if ffp_ratio == 'ROP':
        ffp_ratio = 1.2
    elif ffp_ratio == 'LOP':
        ffp_ratio = 0.9

    ff_guess_low = 1
    ff_guess_high = 40
    
    error = 1
    count=0
    while 1:
        count+=1
        ff_guess = (ff_guess_low + ff_guess_high) / 2.
        ffp_guess = ff_guess / ffp_ratio
        pwr_guess = power(ff_guess, ffp_guess, n, CR, displacement, ff_units, fric_power_factor)
        
        error = M.fabs(pwr_guess - p) / p
        if error < 0.0001:
            if verbose == 0:
                return ff_guess
            else:
                return ff_guess, ffp_guess, pwr_guess
        if count > 100:
            if verbose == 0:
                return ff_guess * p / pwr_guess
            else:
                return ff_guess * p / pwr_guess, ffp_guess * p / pwr_guess, p
        
        if pwr_guess > p:
            ff_guess_high = ff_guess
            # print "High.  ff_guess=%.8f, pwr_guess=%.8f" % (ff_guess, pwr_guess)
        else:
            ff_guess_low = ff_guess
            # print "Low.  ff_guess=%.8f, pwr_guess=%.8f" % (ff_guess, pwr_guess)


def pwr_ratio_vs_ff_ratio(ff_ratio):
    """
    Returns ratio of ihp to ihp at best power mixture, given the ratio of fuel flow to fuel flow at best power mixture
    """
    if ff_ratio <1:
        pwr_ratio = min(-6.6460733842049100 + 23.3288519147936704 * ff_ratio + -23.8953796371913860 * ff_ratio**2 + 8.2135973070476958 * ff_ratio**3, 1)
    elif ff_ratio <= 1.075:
        pwr_ratio = 1.
    else:
        pwr_ratio = min(-5.2028639120930054 + 19.7100843534666197 * ff_ratio + -23.3508142352661530 * ff_ratio**2 + 12.2739948562721999 * ff_ratio**3 + -2.4324891578525345 * ff_ratio**4, 1.)

    return pwr_ratio
    
def iSFC(CR, imep=150):
    """
    Return indicated specific fuel consumption as a function of compression ratio and indicated mean effective pressure in pounds per square inch
    """
    if CR == 6.75:
        if imep >= 140:
            return .439
        else:
            return 0.9059482911201194 + -0.0083412394761360 * imep + 0.0000488027896066 * imep**2 + -0.0000000931918973 * imep**3
            
    elif CR == 7:
        if imep >= 140:
            return .433
        else:
            return 0.8576343912445054 + -0.0072234206668588 * imep + 0.0000390214749438 * imep**2 + -0.0000000649197368 * imep**3

    elif CR == 7.2:
        if imep >= 140:
            return .427
        else:
            return 1.0679731853455388 + -0.0128164477003122 * imep + 0.0000876252573784 * imep**2 + -0.0000002057439786 * imep**3

    elif CR == 7.3:
        if imep >= 140:
            return .424
        else:
            return 0.7597347244765934 + -0.0049979030346516 * imep + 0.0000210043956902 * imep**2 + -0.0000000174001560 * imep**3

    elif CR == 8:
        if imep >= 140:
            return .413
        else:
            return 0.8077120372839203 + -0.0065003274173203 * imep + 0.0000335404587916 * imep**2 + -0.0000000517752682 * imep**3

    elif CR == 8.5:
        if imep >= 140:
            return .407
        else:
            return 0.8379959978754954 + -0.0076050045481202 * imep + 0.0000430354417519 * imep**2 + -0.0000000763804104 * imep**3

    elif CR == 8.7:
        if imep >= 140:
            return .4
        elif imep >= 94:
            return 0.8016382542597682 + -0.0070362208555203 * imep + 0.0000397959939526 * imep**2 + -0.0000000716015877 * imep**3
        else:
            return 0.8379959978754954 + -0.0076050045481202 * imep + 0.0000430354417519 * imep**2 + -0.0000000763804104 * imep**3 - .004

    elif CR == 9:
        if imep >= 140:
            return .4
        else:
            return 0.8016382542597682 + -0.0070362208555203 * imep + 0.0000397959939526 * imep**2 + -0.0000000716015877 * imep**3
    elif CR == 10:
        if imep >= 140:
            return .39
        else:
            return 0.8016382542597682 + -0.0070362208555203 * imep + 0.0000397959939526 * imep**2 + -0.0000000716015877 * imep**3 - 0.01

    else:
        print 'The compression ratio must be one of 6.75, 7, 7.2, 7.3, 8, 8.5, 8.7, 9 or 10'
        return 'The compression ratio must be one of 6.75, 7, 7.2, 7.3, 8, 8.5, 8.7, 9 or 10'
        

fhp_n = [2000., 2300., 2600., 2900., 3400.]
fhp_235  = [ 9,   12.5, 16,   20,   28]
fhp_320  = [13,   17.,  21.5, 27.5, 38]
fhp_360  = [17,   22.,  28.,  35.,  48]
fhp_480  = [21,   27.5, 35.5, 44,   60]
fhp_540  = [27,   34.5, 45,   55.5, 76]
fhp_480S = [31,   41,   53,   66.,  90]
fhp_720  = [38,   50.5, 64,   80.5, 110.5]

def friction_hp(disp, n):
    """
    Return friction horsepower as a function of displacement and rpm.
    
    disp = displacement in cubic inches
    
    n = engine speed in revolutions per minute
    """
    # fhp_data_n = [2000, 2300, 2600, 2900, 3400]
    # fhp_fhp_360 = [17, 22, 28, 34.5, 38]
        
    if disp == 235 or disp == '235':
        return -29.3467601780368952 + 0.0328180834559705 * n + -0.0000098617092143 * n**2 + 0.0000000015207014 * n**3
    elif disp == 290 or disp == '290':
        return (32.2852879043700369 + -0.0358206349342127 * n + 0.0000160531054837 * n**2 + -0.0000000014770586 * n**3)*290/320.
    elif disp == 320 or disp == '320':
        return 32.2852879043700369 + -0.0358206349342127 * n + 0.0000160531054837 * n**2 + -0.0000000014770586 * n**3
    elif disp == 340 or disp == '340':
        return (32.2852879043700369 + -0.0358206349342127 * n + 0.0000160531054837 * n**2 + -0.0000000014770586 * n**3)*340/320.
    elif disp == 360 or disp == '360':
        return 26.3615029922214319 + -0.0287849165689263 * n + 0.0000145043760676 * n**2 + -0.0000000012253464 * n**3
    elif disp == 375 or disp == '375':
        return (26.3615029922214319 + -0.0287849165689263 * n + 0.0000145043760676 * n**2 + -0.0000000012253464 * n**3) * 375/360.
    elif disp == 390 or disp == '390':
        return (26.3615029922214319 + -0.0287849165689263 * n + 0.0000145043760676 * n**2 + -0.0000000012253464 * n**3) * 390/360.
    elif disp == 400 or disp == '400':
        return (26.3615029922214319 + -0.0287849165689263 * n + 0.0000145043760676 * n**2 + -0.0000000012253464 * n**3) * 400/360.
    elif disp == 409 or disp == '409':
        return (26.3615029922214319 + -0.0287849165689263 * n + 0.0000145043760676 * n**2 + -0.0000000012253464 * n**3) * 409/360.
    elif disp == 480 or disp == '480':
        return 23.5315907011200203 + -0.0281685136434028 * n + 0.0000163114436151 * n**2 + -0.0000000014331379 * n**3
    elif disp == 540 or disp == 541 or disp == '540' or disp == '541':
        return 60.1933087214705722 + -0.0684571189991537 * n + 0.0000322114546823 * n**2 + -0.0000000031506484 * n**3
    elif disp == 580 or disp == '580':
        return (60.1933087214705722 + -0.0684571189991537 * n + 0.0000322114546823 * n**2 + -0.0000000031506484 * n**3) * 580/540.
    elif disp == '480S':
        return 34.7592092352365540 + -0.0432705496941272 * n + 0.0000252414999859 * n**2 + -0.0000000022755592 * n**3
    elif disp == 720 or disp == '720' or disp == '540S':
        return 17.6480415158379031 + -0.0202542241199032 * n + 0.0000170050762205 * n**2 + -0.0000000008863450 * n**3
    else:
        raise LookupError('ERROR - The displacement must be one of 235, 290, 320, 340, 360, 375, 390, 400, 409, 480, 480S, 540, 540S, 541, 580 or 720.  The suffix S denotes GSO or IGSO engines.')


def ff_table(FFP, n, CR, disp):
    import numpy
    print "%6s %6s %6s %9s" % ('Fuel', 'Pwr', 'Pwr', 'bSFC')
    print "%6s %6s %6s %9s" % ('Flow', ' ', 'per', '')
    print "%6s %6s %6s %9s" % ('', ' ', 'GPH', '')
    print "%6s %6s %6s %9s" % ('(GPH)', '(hp)', '(hp/GPH)', '(lb/h/hp)')
    for ff in numpy.arange(FFP-3, FFP+5, 0.01):
        FF_best_power = FFP / .849
        p = power(ff, FFP, n, CR, disp)
        if numpy.abs(ff-FFP) < 0.005:
            remarks = "Fuel flow for peak EGT"
        elif numpy.abs((ff - FF_best_power)/FF_best_power) < 0.005:
            remarks = "Fuel flow for best power"
        else:
            remarks = ' '
            
        print "%5.2f %7.2f %7.2f %9.3f %23s" % (ff, p, p/ff, ff * 6.01/p, remarks)
