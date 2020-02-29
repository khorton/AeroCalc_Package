#! /usr/bin/env python3


"""prop efficiency map decoding
"""

import csv
import glob
import interpolator as I
import math as M
import numpy as N
import os.path
from platform import node
import re
import std_atm as SA
import unit_conversion as U

# #############################################################################
#
# version 0.2, 28 Feb 2020
#
# Version History:
# vers     date      Notes
# 0.1    29 May 2009  Initial release
# 0.2    28 Feb 2020  Python 3 compatibility
# #############################################################################
#
# To Do:  1. Remove hard coded pointers to directories on kwh's computers.
#            Perhaps create a config file to hold default directories.
#
#         2. Fix 'nan' prop_eff returned at low TAS or low power.
#
# Done    1.
#
#         2. 03 Nov 09

# #############################################################################

"""
Performs various calculations relating to constant speed propeller
performance.  Requires data files in csv format.

Calculates thrust, prop efficiency, blade tip mach, advance ratio, power
coefficient, and thrust coefficient, given flight and engine parametres.

Validated against Excel spreadsheet provided by Les Doud (Hartzell).
"""

class Prop:
    def __init__(self, base_name, base_path=''):
        """Returns a propeller object
        
        prop = Prop('7666-2RV')
        prop = Prop('MTV*183-59B')
        prop = Prop('MTV*402')
        """
        self.prop = base_name

        # create temp lists, to hold the data before it is read into arrays
        temp_data_storage1 = []
        temp_data_storage2 = []
        temp_data_storage3 = []

        if '7666' in base_name:
            self.manufacturer = 'Hartzell'
            self.model = base_name
            if base_path == '': 
                node_name = node()
                if node_name[:9] == 'PowerBook':
                    base_path = '/Users/kwh/RV/Engine_prop/Hartzell_prop_maps/'
                elif node_name == 'Kevins-MacBook-Air.local':
                    base_path = '/Users/kwh/Documents/RV/Engine_prop/Hartzell_prop_maps/'
                elif node_name == 'Kevins-MBPr.local':
                    base_path = '/Users/kwh/Documents/RV/Engine_prop/Hartzell_prop_maps/'
                elif node_name == 'MacMini.local':
                    base_path = '/Users/kwh/Documents/Flying/RV/Engine_prop/Hartzell_prop_maps/'
                elif node_name == 'ncrnbhortonk2':
                    base_path = 'C:\\Documents and Settings\\hortonk\\My Documents\\rv\\Prop\\Hartzell_prop_maps\\'
                elif node_name == 'eeepc':
                    base_path = '/home/kwh/RV/Hartzell_prop_maps/'
                elif node_name == 'sage-BHYVE':
                    base_path = '/home/kwh/Prop_Maps/Hartzell_prop_maps/'
                elif node_name == 'sage-ubuntu-1404':
                    base_path = '/home/kwh/python/prop_maps/Hartzell_prop_maps/'
                else:
                    raise ValueError('Unknown computer')

            # confirm the path to the data files exists
            if os.path.exists(base_path):
                pass
            else:
                raise ValueError('The path specified for the prop map files does not exist')

            file_glob = base_path + base_name + '*.csv'
            file_names = glob.glob(file_glob)

            # confirm that at least one data file was found
            if len(file_names) < 1:
                raise ValueError('No prop data files were found.')

            # need names in sorted order, so the array ends up in order of mach
            # sorting seems to not be needed on OS X, as glob.glob() returns a sorted list
            # but, on Linux, the list is not sorted
            file_names.sort()
            
            for file_name in file_names:
                FILE = open(file_name)  
                raw_data = csv.reader(FILE)

                # parse mach number
                for line in raw_data:
                    mach_search = re.search('Mach\s0\.\d+', line[0])
                    if mach_search:
                        mach_group = re.search('0\.\d+', line[0])
                        mach = mach_group.group()
                        break

                # find start of CT data
                for line in raw_data:
                    try:
                        header_search = re.search('THRUST COEFFICIENT', line[0])
                        if header_search:
                            break       

                    except IndexError:
                        pass
                # load block of CT values into temp storage
                temp_lines1 = []
                while 1:
                    value_line = next(raw_data)
                    try:
                        value_line_search = re.match('[0\.\d+,CP]', value_line[0])
                    except IndexError:
                        # at the end of the data block - move on
                        break               
                    if value_line_search:
                        # strip spurious zeros from right end of data
                        while value_line[-1] == '0':
                            value_line.pop()
                        temp_lines1.append(value_line)

                        # convert values to float
                        for i, item in enumerate(value_line):
                            try:
                                value_line[i] = float(item)
                            except ValueError:
                                value_line[i] = 0               
                    else:
                        # at the end of the data block - move on
                        break

                # strip of "CP / J" from first line, and replace by mach,
                temp_lines1[0][0] = float(mach)

                # find start of blade angle data
                for line in raw_data:
                    try:
                        header_search = re.search('BLADE ANGLE', line[0])
                        if header_search:
                            break
                    except IndexError:
                        pass

                # load block of blade angle values into temp storage
                temp_lines3 = []
                while 1:
                    try:
                        value_line = next(raw_data)
                    except StopIteration:
                        break
                    try:
                        value_line_search = re.match('[0\.\d+,CP]', value_line[0])
                    except IndexError:
                        # at the end of the data block - move on
                        break               
                    if value_line_search:
                        # strip spurious zeros from right end of data
                        while value_line[-1] == '0':
                            value_line.pop()
                        temp_lines3.append(value_line)

                        # convert values to float
                        for i, item in enumerate(value_line):
                            try:
                                value_line[i] = float(item)
                            except ValueError:
                                value_line[i] = 0               
                    else:
                        # at the end of the data block - move on
                        break

                # strip of "CP / J" from first line, and replace by mach,
                temp_lines3[0][0] = float(mach)





                # find start of efficiency data
                for line in raw_data:
                    try:
                        header_search = re.search('EFFICIENCY', line[0])
                        if header_search:
                            break
                    except IndexError:
                        pass

                # load block of efficiency values into temp storage
                temp_lines2 = []
                while 1:
                    try:
                        value_line = next(raw_data)
                    except StopIteration:
                        break
                    try:
                        value_line_search = re.match('[0\.\d+,CP]', value_line[0])
                    except IndexError:
                        # at the end of the data block - move on
                        break               
                    if value_line_search:
                        # strip spurious zeros from right end of data
                        while value_line[-1] == '0':
                            value_line.pop()
                        temp_lines2.append(value_line)

                        # convert values to float
                        for i, item in enumerate(value_line):
                            try:
                                value_line[i] = float(item)
                            except ValueError:
                                value_line[i] = 0               
                    else:
                        # at the end of the data block - move on
                        break

                # strip of "CP / J" from first line, and replace by mach,
                temp_lines2[0][0] = float(mach)


                # determine required size for array
                # this is done once for each data file, but only the last result is used
                self.x_size = len(temp_lines1[0])
                self.y_size = len(temp_lines1)
                self.z_size = len(file_names)

                # push data blocks into temp storage
                temp_data_storage1.append(temp_lines1)      
                temp_data_storage2.append(temp_lines2)      
                temp_data_storage3.append(temp_lines3)      

            # create array for CT data, and populate it
            self.prop_CT_map = N.zeros((self.z_size, self.y_size, self.x_size))

            # trim length of temp data to be sure it will fit in array
            for i, layer in enumerate(temp_data_storage1):
                for i, line in enumerate(layer):
                    while len(line) > self.x_size:
                        if line[-1] == 0:
                            line.pop(-1)
                        else:
                            print('Problem line =', line)
                            raise ValueError('Problem - Trying to remove real data from end of line')

            for i, item in enumerate(temp_data_storage1):
                self.prop_CT_map[i] = temp_data_storage1[i]

            # determine range of mach, advance ratio and power coefficient in the CT data
            self.Ct_mach_min = min(self.prop_CT_map[:,0,0])
            self.Ct_mach_max = max(self.prop_CT_map[:,0,0])
            self.Ct_Cp_min = min(self.prop_CT_map[0,1:,0])
            self.Ct_Cp_max = max(self.prop_CT_map[0,1:,0])
            self.Ct_J_min = min(self.prop_CT_map[0,0,:])
            self.Ct_J_max = max(self.prop_CT_map[0,0,:])

            # create array for blade angle data, and populate it
            self.blade_angle_map = N.zeros((self.z_size, self.y_size, self.x_size))

            # trim length of temp data to be sure it will fit in array
            for i, layer in enumerate(temp_data_storage3):
                for i, line in enumerate(layer):
                    while len(line) > self.x_size:
                        if line[-1] == 0:
                            line.pop(-1)
                        else:
                            raise ValueError('Problem - Trying to remove real data from end of line')

            for i, item in enumerate(temp_data_storage1):
                self.blade_angle_map[i] = temp_data_storage3[i]

            # determine range of mach, advance ratio and power coefficient in the blade angle data
            self.blade_angle_mach_min = min(self.blade_angle_map[:,0,0])
            self.blade_angle_mach_max = max(self.blade_angle_map[:,0,0])
            self.blade_angle_Cp_min = min(self.blade_angle_map[0,1:,0])
            self.blade_angle_Cp_max = max(self.blade_angle_map[0,1:,0])
            self.blade_angle_J_min = min(self.blade_angle_map[0,0,:])
            self.blade_angle_J_max = max(self.blade_angle_map[0,0,:])

            # create array for efficiency data, and populate it
            self.prop_eff_map = N.zeros((self.z_size, self.y_size, self.x_size))

            # trim length of temp data to be sure it will fit in array
            for i, layer in enumerate(temp_data_storage2):
                for i, line in enumerate(layer):
                    while len(line) > self.x_size:
                        if line[-1] == 0:
                            line.pop(-1)
                        else:
                            raise ValueError('Problem - Trying to remove real data from end of line')

            for i, item in enumerate(temp_data_storage1):
                self.prop_eff_map[i] = temp_data_storage2[i]

            # determine range of mach, advance ratio and power coefficient in the efficiency data
            self.eff_mach_min = min(self.prop_eff_map[:,0,0])
            self.eff_mach_max = max(self.prop_eff_map[:,0,0])
            self.eff_Cp_min = min(self.prop_eff_map[0,1:,0])
            self.eff_Cp_max = max(self.prop_eff_map[0,1:,0])
            self.eff_J_min = min(self.prop_eff_map[0,0,:])
            self.eff_J_max = max(self.prop_eff_map[0,0,:])


            # wipe temp storage, to be sure to start with a clean slate for the next type of data
            temp_data_storage1 = []
            temp_data_storage2 = []
            temp_data_storage3 = []

            if base_name == '7666-4RV':
                self.dia = 72
            elif base_name == '7666-2RV':
                self.dia = 74
            else:
                raise ValueError('Invalid prop')
        elif 'MTV' in base_name:
            if base_path == '': 
                node_name = node()
                if node_name[:9] == 'PowerBook':
                    base_path = '/Users/kwh/Documents/RV/MT_Prop/'
                elif node_name == 'Kevins-MacBook-Air.local':
                    base_path = '/Users/kwh/Documents/RV/Engine_prop/MT_Prop/'
                elif node_name == 'Kevins-MBPr.local':
                    base_path = '/Users/kwh/Documents/RV/Engine_prop/MT_Prop/'
                elif node_name == 'MacMini.local':
                    base_path = '/Users/kwh/Documents/Flying/RV/Engine_prop/MT_Prop/'
                elif node_name == 'ncrnbhortonk2':
                    base_path = 'C:\\Documents and Settings\\hortonk\\My Documents\\rv\\Prop\\MT_Prop\\'
                elif node_name == 'eeepc':
                    base_path = '/home/kwh/RV/MT_Prop/'
                elif node_name == 'sage-BHYVE':
                    base_path = '/home/kwh/Prop_Maps/MT_Prop/'
                elif node_name == 'sage-ubuntu-1204':
                    base_path = '/home/kwh/python//prop_maps/'
                else:
                    raise ValueError('Unknown computer')

            # confirm the path to the data files exists
            if os.path.exists(base_path):
                pass
            else:
                raise ValueError('The path specified for the prop map files does not exist')
            file_glob = base_path + base_name + '*.csv'
#            file_glob = base_path + '*' + base_name + '*.csv'
            
            file_names = glob.glob(file_glob)

            # confirm that at least one data file was found
            if len(file_names) < 1:
                raise ValueError('No prop data files were found.')

            for file_name in file_names:
                temp_lines = []
                FILE = open(file_name)  
                raw_data = csv.reader(FILE)
                header_lines = 2
                line1 = next(raw_data)
                model_match = re.search('(\S+)\s+(\S+)\s.*', line1[0])
                self.manufacturer = model_match.group(1)
                self.model = model_match.group(2)
                self.dia = float(re.search('[^-]+-[^-]+-[^-]+-(\d+).*', line1[0]).group(1))
                self.dia = U.length_conv(self.dia, from_units='cm', to_units='in')
                for n in range(header_lines - 1):
                    next(raw_data)

                #replace "J" with mach 0
                temp_lines.append(next(raw_data))
                temp_lines[0][0] = 0

                # load block of efficiency values into temp storage
                while 1:
                    try:
                        temp_lines.append(next(raw_data))
                    except StopIteration:
                        break
                for l, line in enumerate(temp_lines):
                    for i, item in enumerate(line):
                        try:
                            temp_lines[l][i] = float(item)
                        except ValueError:
                            temp_lines[l][i] = 0.

                # determine required size for array
                self.x_size = len(temp_lines[0])
                self.y_size = len(temp_lines)
                self.z_size = 2
                
                temp_array1 = []
                for line in temp_lines:
                    temp_array1.append(line)
                # MT eff map does not have different data for different tip mach numbers.
                # To allow using the same routines as for Hartzell props, set the original 
                # data for Mach 0, and make a copy for Mach 1.
                temp_array=[temp_array1, temp_array1]
                self.prop_eff_map = N.array(temp_array)
                self.prop_eff_map[1,0,0] = 1
                
                # MT eff data has Cp running left to right, and Js running 
                # vertically, which is the reverse of the Hartzell data.
                # Must swapaxes to get the same orientation for both props.
                self.prop_eff_map = self.prop_eff_map.swapaxes(1,2)

                # determine range of mach, advance ratio and power coefficient in the efficiency data
                self.eff_mach_min = min(self.prop_eff_map[:,0,0])
                self.eff_mach_max = max(self.prop_eff_map[:,0,0])
                self.eff_Cp_min = min(self.prop_eff_map[0,:,0])
                self.eff_Cp_max = max(self.prop_eff_map[0,:,0])
                self.eff_J_min = min(self.prop_eff_map[0,0,1:])
                self.eff_J_max = max(self.prop_eff_map[0,0,1:])
                
        else:
            print('prop type not known')


def ct2thrust(Ct, Rho, rpm, dia, thrust_units = 'lb', density_units = 'lb/ft**3', dia_units = 'in'):
    """
    Returns the thrust, given thrust coefficient, Ct, density, rpm and prop
    diameter.
    """
    Rho = U.density_conv(Rho, from_units = density_units, to_units = 'kg/m**3')
    dia = U.length_conv(dia, from_units = dia_units, to_units = 'm')
    # convert rpm to revolutions / s
    n = rpm / 60.
    thrust = Ct * Rho * n ** 2. * dia ** 4.
    
    return U.force_conv(thrust, from_units = 'N', to_units = thrust_units)


def eff2thrust(eff, bhp, TAS, power_units = 'hp', speed_units = 'kt', thrust_units = 'lb'):
    """
    Returns thrust, given prop efficiency, true airspeed and brake power.
    
    Matches the results from the Hartzell prop map program fairly closely.
    """
    TAS = U.speed_conv(TAS, from_units = speed_units, to_units = 'm/s')
    bhp = U.power_conv(bhp, from_units = power_units, to_units = 'W')
    thrust = eff * bhp / TAS
    
    return U.force_conv(thrust, from_units = 'N', to_units = thrust_units)


def tip_mach(tas, rpm, temperature, dia, speed_units = 'kt', temp_units = 'C', dia_units = 'in'):
    """
    Returns the mach number of the propeller blade tip, given the
    true airspeed (tas), revolutions per minute (rpm), temperature and
    propeller diameter.
    
    The speed units may be specified as "kt", "mph", "km/h" or "ft/s", but
    default to "kt" if not specified.
    
    The temperature units may be specified as "C", "F", "K" or "R", but
    default to deg C if not specified.
    
    The diameter units may be specified as "in", "ft", or "m", but default
    to inches if not specified.
    """
    dia = U.length_conv(dia, from_units = dia_units, to_units = 'm')
    tas = U.speed_conv(tas, from_units = speed_units, to_units = 'm/s')
    speed_of_sound = SA.temp2speed_of_sound(temperature, temp_units = temp_units, speed_units = 'm/s')
    
    rotation_speed = dia * rpm * M.pi/ 60
    tip_speed = M.sqrt(tas ** 2 + rotation_speed ** 2)
    tip_mach = tip_speed / speed_of_sound
        
    return tip_mach


def advance_ratio(tas, rpm, dia, speed_units = 'kt', dia_units = 'in'):
    """
    Returns the propeller advance ratio, J, given the
    revolutions per minute (rpm), true airspeed (tas), temperature and
    propeller diameter.

    The advance ratio is the forward distance that the propeller advances
    during one revolution, divided by the diameter of the propeller.

    The diameter units may be specified as "in", "ft", or "m", but default
    to inches if not specified.
    """
    tas = U.speed_conv(tas, from_units = speed_units, to_units = 'm/s')
    dia = U.length_conv(dia, from_units = dia_units, to_units = 'm')
    
    advance_ratio = tas * 60. / (rpm * dia)
    
    return advance_ratio


def bhp2Cp(bhp, rpm, density, dia, power_units = 'hp', density_units = 'lb/ft**3', dia_units = 'in'):
    """
    Returns the propeller power coefficient, Cp, given power, revolutions per 
    minute (rpm), and propeller diameter.

    The power units may be specified as "hp", "ft-lb/mn", "ft-lb/s", "W"
    (watts) or "kW" (kilowatts), but default to "hp" if not specified.

    The density units may be specified as "lb/ft**3", "slug/ft**3" or 
    "kg/m**3", but default to "lb/ft**3" if not specified.

    The diameter units may be specified as "in", "ft", or "m", but default
    to inches if not specified.
    """
    bhp = U.power_conv(bhp, from_units = power_units, to_units = 'W')
    density = U.density_conv(density, from_units = density_units, to_units = 'kg/m**3')
    dia = U.length_conv(dia, from_units = dia_units, to_units = 'm')
    
    Cp = bhp / (density * ((rpm / 60.) ** 3) * dia ** 5)
    
    return Cp

def cp2bhp(Cp, rpm, density, dia, power_units = 'hp', density_units = 'lb/ft**3', dia_units = 'in'):
    """
    Returns the bhp, given propeller power coefficient (Cp), revolutions per 
    minute (rpm), and propeller diameter.

    The power units may be specified as "hp", "ft-lb/mn", "ft-lb/s", "W"
    (watts) or "kW" (kilowatts), but default to "hp" if not specified.

    The density units may be specified as "lb/ft**3", "slug/ft**3" or 
    "kg/m**3", but default to "lb/ft**3" if not specified.

    The diameter units may be specified as "in", "ft", or "m", but default
    to inches if not specified.
    """
    # bhp = U.power_conv(bhp, from_units = power_units, to_units = 'W')
    density = U.density_conv(density, from_units = density_units, to_units = 'kg/m**3')
    dia = U.length_conv(dia, from_units = dia_units, to_units = 'm')
    
    bhp = Cp * (density * ((rpm / 60.) ** 3) * dia ** 5)
    bhp = U.power_conv(bhp, from_units='W', to_units=power_units)
    
    return bhp

def prop_eff(prop, bhp, rpm, tas, altitude, temp = 'std', power_units = 'hp', alt_units = 'ft', temp_units = 'C', speed_units = 'kt', dia_units = 'in'):
    """
    Returns propeller efficiency based on engine power provided to the propeller.
    """
    press_ratio = SA.alt2press_ratio(altitude, alt_units = alt_units)
    if temp == 'std':
        temp = SA.alt2temp(altitude, temp_units = temp_units, alt_units = alt_units)
    temp_ratio = U.temp_conv(temp, from_units = temp_units, to_units = 'K') / 288.15
    density_ratio = press_ratio / temp_ratio
    density = density_ratio * SA.Rho0
    Cp = bhp2Cp(bhp, rpm, density, prop.dia, power_units = power_units, density_units = 'kg/m**3', dia_units = dia_units)
    J = advance_ratio(tas, rpm, prop.dia, speed_units = speed_units, dia_units = dia_units)
    blade_tip_mach = tip_mach(tas, rpm, temp, prop.dia, speed_units = speed_units, temp_units = temp_units, dia_units = dia_units)
    
    prop_eff = cp2eff(prop, Cp, J, blade_tip_mach)
    
    if N.isnan(prop_eff):
        raise ValueError('Out of range inputs')

    return prop_eff
    
def prop_eff2(prop, thp, rpm, tas, altitude, temp = 'std', power_units = 'hp', alt_units = 'ft', temp_units = 'C', speed_units = 'kt', dia_units = 'in'):
    """
    Returns propeller efficiency based on thrust power provided by the propeller.
    """
    prop_eff_guess = 0.85
    # do up to 100 iterations, stopping if convergence is achieved first
    for n in range(100):
        bhp_guess = thp / prop_eff_guess
        prop_eff_guess_new = prop_eff(prop, bhp_guess, rpm, tas, altitude, temp, power_units, alt_units, temp_units, speed_units, dia_units)
        if (M.fabs((prop_eff_guess_new - prop_eff_guess)/prop_eff_guess) < 0.0001):
            # we have converged within 0.01%
            return prop_eff_guess
        prop_eff_guess = prop_eff_guess_new

    #print "hit iteration limit: guesses are", prop_eff_guess, prop_eff_guess_new
    # convergence was not achieved before 100 iterations.  Return the average of the current and previous guesses
    return (prop_eff_guess_new + prop_eff_guess) / 2
    

def blade_angle(prop, bhp, rpm, tas, altitude, temp = 'std', power_units = 'hp', alt_units = 'ft', temp_units = 'C', speed_units = 'kt', dia_units = 'in'):
    """
    Returns propeller blade angle.
    """
    press_ratio = SA.alt2press_ratio(altitude, alt_units = alt_units)
    if temp == 'std':
        temp = SA.alt2temp(altitude, temp_units = temp_units, alt_units = alt_units)
    temp_ratio = U.temp_conv(temp, from_units = temp_units, to_units = 'K') / 288.15
    density_ratio = press_ratio / temp_ratio
    density = density_ratio * SA.Rho0
    Cp = bhp2Cp(bhp, rpm, density, prop.dia, power_units = power_units, density_units = 'kg/m**3', dia_units = dia_units)
    J = advance_ratio(tas, rpm, prop.dia, speed_units = speed_units, dia_units = dia_units)
    blade_tip_mach = tip_mach(tas, rpm, temp, prop.dia, speed_units = speed_units, temp_units = temp_units, dia_units = dia_units)
    
    blade_angle = cp2blade_angle(prop, Cp, J, blade_tip_mach)
    
    return blade_angle

def prop_eff_vs_tas(prop, alt, bhp, rpm):
    """
    Prints prop efficiency over a range of speeds.
    """
    print('Prop:', prop.prop)
    print('Altitude:', alt)
    print('Power:', bhp)
    print('RPM:', rpm)
    for tas in range(10, 230, 10):
        p_eff = prop_eff(prop, bhp, rpm, tas, alt)
        pe_format = '%.1f' % (p_eff * 100)
        print('TAS:', tas, 'Prop eff:', pe_format, '%')

def prop_eff_vs_bhp(prop, alt, tas, rpm):
    """
    Prints prop efficiency over a range of powers.
    """
    print('Prop:', prop.prop)
    print('Altitude:', alt)
    print('TAS:', tas)
    print('RPM:', rpm)
    for bhp in range(50, 350, 10):
        p_eff = prop_eff(prop, bhp, rpm, tas, alt)
        pe_format = '%.1f' % (p_eff * 100)
        print('Power:', bhp, 'Prop eff:', pe_format, '%')

def prop_eff_vs_rpm(prop, alt, tas, bhp):
    """
    Prints prop efficiency over a range of rpms.
    """
    print('Prop:', prop.prop)
    print('Altitude:', alt)
    print('TAS:', tas)
    print('Power:', bhp)
    for rpm in range(1500, 3500, 100):
        p_eff = prop_eff(prop, bhp, rpm, tas, alt)
        pe_format = '%.1f' % (p_eff * 100)
        print('RPM:', rpm, 'Prop eff:', pe_format, '%')

def prop_data(prop, bhp, rpm, tas, altitude, temp = 'std', power_units = 'hp', alt_units = 'ft', temp_units = 'C', speed_units = 'kt', dia_units = 'in', thrust_units = 'lb'):
    """
    Returns advance ratio, power coefficient, thrust coefficient, blade tip
    mach number, propeller efficiency and thrust.
    
    Validated against Excel spreadsheet provided by Les Doud (Hartzell).
    """
    press_ratio = SA.alt2press_ratio(altitude, alt_units = alt_units)
    if temp == 'std':
        temp = SA.alt2temp(altitude, temp_units = temp_units, alt_units = alt_units)
    temp_ratio = U.temp_conv(temp, from_units = temp_units, to_units = 'K') / 288.15
    density_ratio = press_ratio / temp_ratio
    density = density_ratio * SA.Rho0
    
    Cp = bhp2Cp(bhp, rpm, density, prop.dia, power_units = power_units, density_units = 'kg/m**3', dia_units = dia_units)
    J = advance_ratio(tas, rpm, prop.dia, speed_units = speed_units, dia_units = dia_units)
    blade_tip_mach = tip_mach(tas, rpm, temp, prop.dia, speed_units = speed_units, temp_units = temp_units, dia_units = dia_units)

    prop_eff = cp2eff(prop, Cp, J, blade_tip_mach)
    try:
        Ct = cp2ct(prop, Cp, J, blade_tip_mach)
    except:
        Ct = cp2ct_alt(prop, Cp, bhp, rpm, tas, altitude, temp = temp, power_units = power_units, alt_units = alt_units, temp_units = temp_units, speed_units = speed_units)

    if prop_eff > 0.1:
        thrust = eff2thrust(prop_eff, bhp, tas, power_units = power_units, speed_units = speed_units, thrust_units = thrust_units)
    else:
        thrust = ct2thrust(Ct, density, rpm, prop.dia, thrust_units = thrust_units, density_units = 'kg/m**3', dia_units = dia_units)
    # data_block = 'J = ' + str(J) + '\nCp = ' + str(Cp) + '\n Tip mach = ' + str(blade_tip_mach) + '\n Ct = ' + str(Ct) + '\n Thrust = ' + str(thrust) + ' ' + thrust_units + '\n Prop efficiency = ' + str(prop_eff)
    
    print('           prop = ', prop.prop)
    print('              J = %.3f' % J)
    print('             Cp = %.5f' % Cp)
    print('       Tip Mach = %.3f' % blade_tip_mach)
    print('             Ct = %.3f' % Ct)
    print('         Thrust = %.2f' % thrust, thrust_units)
    print('Prop efficiency = %.4f' % prop_eff)
    print('      Thrust HP = %.2f' % bhp * prop_eff)
    
    return


def pull_Ct_data_point(prop, tip_mach, J, Cp):
    """
    Returns specific Ct data points from prop map array files.
    """
    (tip_mach, J, Cp) = (float(tip_mach), float(J), float(Cp))
    mach_index = N.searchsorted(prop.blade_angle_map[:,0,0],tip_mach)
    J_index = N.searchsorted(prop.blade_angle_map[0,0,1:],J) + 1
    Cp_index = N.searchsorted(prop.blade_angle_map[0,1:,0],Cp) + 1
    
    blade_angle = prop.blade_angle_map[mach_index, Cp_index, J_index]
    
    return blade_angle


def pull_blade_angle_data_point(prop, tip_mach, J, Cp):
    """
    Returns specific blade angle data points from prop map array files.
    """
    (tip_mach, J, Cp) = (float(tip_mach), float(J), float(Cp))
    mach_index = N.searchsorted(prop.blade_angle_map[:,0,0],tip_mach)
    J_index = N.searchsorted(prop.blade_angle_map[0,0,1:],J) + 1
    Cp_index = N.searchsorted(prop.blade_angle_map[0,1:,0],Cp) + 1
    
    Ct = prop.blade_angle_map[mach_index, Cp_index, J_index]
    
    return Ct


def pull_eff_data_point(prop, tip_mach, J, Cp):
    """
    Returns specific efficiency data points from prop map array files.
    """
    (tip_mach, J, Cp) = (float(tip_mach), float(J), float(Cp))
    mach_index = N.searchsorted(prop.prop_eff_map[:,0,0],tip_mach)
    J_index = N.searchsorted(prop.prop_eff_map[0,0,1:],J) + 1
    Cp_index = N.searchsorted(prop.prop_eff_map[0,1:,0],Cp) + 1
    # Cp_index = N.searchsorted(prop.prop_eff_map[0,1:,0],Cp)
    
    eff = prop.prop_eff_map[mach_index, Cp_index, J_index]
    
    return eff


def cp2ct(prop, Cp, J, tip_mach):
    """
    Returns thrust coefficient, given power coefficient (Cp), advance ratio
    (J) and the mach number of the blade tip.
    """
    mach_low = max(prop.Ct_mach_min, prop.prop_CT_map[max(min(N.searchsorted(prop.prop_CT_map[:,0,0], tip_mach) - 1, prop.z_size - 1),0),0,0])
    if mach_low == prop.Ct_mach_max:
        mach_low = prop.prop_CT_map[-2,0,0]
    mach_high = min(prop.Ct_mach_max, prop.prop_CT_map[min(N.searchsorted(prop.prop_CT_map[:,0,0], tip_mach), prop.z_size - 1),0,0])
    if mach_high == prop.Ct_mach_min:
        mach_high = prop.prop_CT_map[1,0,0]

    J_low = max(prop.Ct_J_min, prop.prop_CT_map[0,0,max(min(N.searchsorted(prop.prop_CT_map[0,0,1:], J), prop.x_size - 2),1)])
    if J_low == prop.Ct_J_max:
        J_low = prop.prop_CT_map[0,0,-2]
    J_high = min(prop.Ct_J_max, prop.prop_CT_map[0,0,min(N.searchsorted(prop.prop_CT_map[0,0,1:], J), prop.x_size - 2) + 1])
    if J_high == prop.Ct_J_min:
        J_high = prop.prop_CT_map[0,0,2]

    Cp_low = max(prop.Ct_Cp_min, prop.prop_CT_map[0,max(min(N.searchsorted(prop.prop_CT_map[0,1:,0], Cp), prop.y_size - 2),1),0])
    if Cp_low == prop.Ct_Cp_max:
        Cp_low = prop.prop_CT_map[0,-2,0]
    Cp_high = min(prop.Ct_Cp_max, prop.prop_CT_map[0,min(N.searchsorted(prop.prop_CT_map[0,1:,0], Cp), prop.y_size - 2) + 1,0])
    if Cp_high == prop.Ct_Cp_min:
        Cp_high = prop.prop_CT_map[0,2,0]

    # get Ct for mach_low, J_low and Cp_low
    Ct_low_low_low = pull_Ct_data_point(prop, mach_low, J_low, Cp_low)

    # get Ct for mach_low, J_high and Cp_low
    Ct_low_high_low = pull_Ct_data_point(prop, mach_low, J_high, Cp_low)

    # get Ct for mach_low, J_low and Cp_high
    Ct_low_low_high = pull_Ct_data_point(prop, mach_low, J_low, Cp_high)

    # get Ct for mach_low, J_high and Cp_high
    Ct_low_high_high = pull_Ct_data_point(prop, mach_low, J_high, Cp_high)

    # get Ct for mach_high, J_low and Cp_low
    Ct_high_low_low = pull_Ct_data_point(prop, mach_high, J_low, Cp_low)

    # get Ct for mach_high, J_high and Cp_low
    Ct_high_high_low = pull_Ct_data_point(prop, mach_high, J_high, Cp_low)

    # get Ct for mach_high, J_low and Cp_high
    Ct_high_low_high = pull_Ct_data_point(prop, mach_high, J_low, Cp_high)

    # get Ct for mach_high, J_high and Cp_high
    Ct_high_high_high = pull_Ct_data_point(prop, mach_high, J_high, Cp_high)

    x = [J_low, J_high]
    y = [Cp_low, Cp_high]
    z = [mach_low, mach_high]
    
    values = [[[Ct_low_low_low, Ct_low_high_low], [Ct_low_low_high, Ct_low_high_high]],
              [[Ct_high_low_low, Ct_high_high_low], [Ct_high_low_high, Ct_high_high_high]]]

    Ct = I.interpolate3(x, y, z, values, J, Cp, tip_mach)

    return Ct

def cp2ct_alt(prop, Cp, bhp, rpm, tas, altitude, temp = 'std', power_units = 'hp', alt_units = 'ft', temp_units = 'C', speed_units = 'kt', dia_units = 'in'):
    """
    Alternate calculation of thrust coefficient, for props where there is no thrust coefficient data available from the manufacturer.
    """
    eff = prop_eff(prop, bhp, rpm, tas, altitude, temp = temp, power_units = power_units, alt_units = alt_units, temp_units = temp_units, speed_units = speed_units, dia_units = dia_units)
    J = advance_ratio(tas, rpm, prop.dia, speed_units = speed_units, dia_units = dia_units)
    Ct = eff * Cp / J
    
    return Ct
    

def cp2eff(prop, Cp, J, tip_mach):
    """
    Returns prop efficiency, given power coefficient (Cp), advance ratio
    (J) and the mach number of the blade tip.
    """
    mach_low = max(prop.eff_mach_min, prop.prop_eff_map[max(min(N.searchsorted(prop.prop_eff_map[:,0,0], tip_mach) - 1, prop.z_size - 1),0),0,0])
    if mach_low == prop.eff_mach_max:
        mach_low = prop.prop_eff_map[-2,0,0]
    mach_high = min(prop.eff_mach_max, prop.prop_eff_map[min(N.searchsorted(prop.prop_eff_map[:,0,0], tip_mach), prop.z_size - 1),0,0])
    if mach_high == prop.eff_mach_min:
        mach_high = prop.prop_eff_map[1,0,0]

    J_low = max(prop.eff_J_min, prop.prop_eff_map[0,0,max(min(N.searchsorted(prop.prop_eff_map[0,0,1:], J), prop.x_size - 2),1)])
    if J_low == prop.eff_J_max:
        J_low = prop.prop_eff_map[0,0,-2]
    J_high = min(prop.eff_J_max, prop.prop_eff_map[0,0,min(N.searchsorted(prop.prop_eff_map[0,0,1:], J), prop.x_size - 2) + 1])
    if J_high == prop.eff_J_min:
        J_high = prop.prop_eff_map[0,0,2]
    if J_high == J_low:
        J_high = J_low + 0.1

    Cp_low = max(prop.eff_Cp_min, prop.prop_eff_map[0,max(min(N.searchsorted(prop.prop_eff_map[0,1:,0], Cp), prop.y_size - 1),1),0])
    if Cp_low == prop.eff_Cp_max:
        # print 'in CP-low'
        Cp_low = prop.prop_eff_map[0,-2,0]
    Cp_high = min(prop.eff_Cp_max, prop.prop_eff_map[0,min(N.searchsorted(prop.prop_eff_map[0,1:,0], Cp), prop.y_size - 1) + 1,0])
    if Cp_high == prop.eff_Cp_min:
        # print 'in CP-high'
        Cp_high = prop.prop_eff_map[0,2,0]
    if Cp_high == Cp_low:
        Cp_high = Cp_low + 0.01

    # get eff for mach_low, J_low and Cp_low
    eff_low_low_low = pull_eff_data_point(prop, mach_low, J_low, Cp_low)
    
    # get eff for mach_low, J_high and Cp_low
    eff_low_high_low = pull_eff_data_point(prop, mach_low, J_high, Cp_low)

    # get eff for mach_low, J_low and Cp_high
    eff_low_low_high = pull_eff_data_point(prop, mach_low, J_low, Cp_high)
    
    # get eff for mach_low, J_high and Cp_high
    eff_low_high_high = pull_eff_data_point(prop, mach_low, J_high, Cp_high)

    # get eff for mach_high, J_low and Cp_low
    eff_high_low_low = pull_eff_data_point(prop, mach_high, J_low, Cp_low)
    
    # get eff for mach_high, J_high and Cp_low
    eff_high_high_low = pull_eff_data_point(prop, mach_high, J_high, Cp_low)

    # get eff for mach_high, J_low and Cp_high
    eff_high_low_high = pull_eff_data_point(prop, mach_high, J_low, Cp_high)
    
    # get eff for mach_high, J_high and Cp_high
    eff_high_high_high = pull_eff_data_point(prop, mach_high, J_high, Cp_high)

    x = [J_low, J_high]
    y = [Cp_low, Cp_high]
    z = [mach_low, mach_high]
    
    values = [[[eff_low_low_low, eff_low_high_low], [eff_low_low_high, eff_low_high_high]],
              [[eff_high_low_low, eff_high_high_low], [eff_high_low_high, eff_high_high_high]]]
    
    # print '[J_low, J_high]:', x
    # print '[Cp_low, Cp_high]:', y
    # print '[mach_low, mach_high:]', z
    # print '[[[eff_low_low_low, eff_low_high_low], [eff_low_low_high, eff_low_high_high]], [[eff_high_low_low, eff_high_high_low], [eff_high_low_high, eff_high_high_high]]]:', values
    # print 'J:', J
    # print 'Cp:', Cp
    # print 'tip mach:', tip_mach
    
    eff = I.interpolate3(x, y, z, values, J, Cp, tip_mach)

    return eff

def cp2blade_angle(prop, Cp, J, tip_mach):
    """
    Returns blade angle, given power coefficient (Cp), advance ratio
    (J) and the mach number of the blade tip.
    """
    mach_low = max(prop.blade_angle_mach_min, prop.blade_angle_map[max(min(N.searchsorted(prop.blade_angle_map[:,0,0], tip_mach) - 1, prop.z_size - 1),0),0,0])
    if mach_low == prop.blade_angle_mach_max:
        mach_low = prop.blade_angle_map[-2,0,0]
    mach_high = min(prop.blade_angle_mach_max, prop.blade_angle_map[min(N.searchsorted(prop.blade_angle_map[:,0,0], tip_mach), prop.z_size - 1),0,0])
    if mach_high == prop.blade_angle_mach_min:
        mach_high = prop.blade_angle_map[1,0,0]

    J_low = max(prop.blade_angle_J_min, prop.blade_angle_map[0,0,max(min(N.searchsorted(prop.blade_angle_map[0,0,1:], J), prop.x_size - 2),1)])
    if J_low == prop.blade_angle_J_max:
        J_low = prop.blade_angle_map[0,0,-2]
    J_high = min(prop.blade_angle_J_max, prop.blade_angle_map[0,0,min(N.searchsorted(prop.blade_angle_map[0,0,1:], J), prop.x_size - 2) + 1])
    if J_high == prop.blade_angle_J_min:
        J_high = prop.blade_angle_map[0,0,2]

    Cp_low = max(prop.blade_angle_Cp_min, prop.blade_angle_map[0,max(min(N.searchsorted(prop.blade_angle_map[0,1:,0], Cp), prop.y_size - 1),1),0])
    if Cp_low == prop.blade_angle_Cp_max:
        # print 'in CP-low'
        Cp_low = prop.blade_angle_map[0,-2,0]
    Cp_high = min(prop.blade_angle_Cp_max, prop.blade_angle_map[0,min(N.searchsorted(prop.blade_angle_map[0,1:,0], Cp), prop.y_size - 1) + 1,0])
    if Cp_high == prop.blade_angle_Cp_min:
        # print 'in CP-high'
        Cp_high = prop.blade_angle_map[0,2,0]

    # get eff for mach_low, J_low and Cp_low
    blade_angle_low_low_low = pull_blade_angle_data_point(prop, mach_low, J_low, Cp_low)
    
    # get eff for mach_low, J_high and Cp_low
    blade_angle_low_high_low = pull_blade_angle_data_point(prop, mach_low, J_high, Cp_low)

    # get eff for mach_low, J_low and Cp_high
    blade_angle_low_low_high = pull_blade_angle_data_point(prop, mach_low, J_low, Cp_high)
    
    # get eff for mach_low, J_high and Cp_high
    blade_angle_low_high_high = pull_blade_angle_data_point(prop, mach_low, J_high, Cp_high)

    # get eff for mach_high, J_low and Cp_low
    blade_angle_high_low_low = pull_blade_angle_data_point(prop, mach_high, J_low, Cp_low)
    
    # get eff for mach_high, J_high and Cp_low
    blade_angle_high_high_low = pull_blade_angle_data_point(prop, mach_high, J_high, Cp_low)

    # get eff for mach_high, J_low and Cp_high
    blade_angle_high_low_high = pull_blade_angle_data_point(prop, mach_high, J_low, Cp_high)
    
    # get eff for mach_high, J_high and Cp_high
    blade_angle_high_high_high = pull_blade_angle_data_point(prop, mach_high, J_high, Cp_high)

    x = [J_low, J_high]
    y = [Cp_low, Cp_high]
    z = [mach_low, mach_high]
    
    values = [[[blade_angle_low_low_low, blade_angle_low_high_low], [blade_angle_low_low_high, blade_angle_low_high_high]],
              [[blade_angle_high_low_low, blade_angle_high_high_low], [blade_angle_high_low_high, blade_angle_high_high_high]]]
    
    blade_angle = I.interpolate3(x, y, z, values, J, Cp, tip_mach)

    return blade_angle

def blade_angle2cp(prop, blade_angle, J, tip_mach):
    """Returns propeller power coefficient (Cp), given blade angle, advance ratio (J) and the mach number of the blade tip.
    """
    temp_cps = []
    temp_blade_angles = []
    
    for cp in N.arange(prop.blade_angle_Cp_min, prop.blade_angle_Cp_max, .005):
        temp_cps.append(cp)
        temp_blade_angles.append(cp2blade_angle(prop, cp, J, tip_mach))
    
    i = N.searchsorted(temp_blade_angles, blade_angle)
    
    return I.interpolate(temp_blade_angles[i:i+2], temp_cps[i:i+2], blade_angle)
        
def blade_angle2bhp(prop, blade_angle, rpm, tas, altitude, temp = 'std', power_units = 'hp', alt_units = 'ft', temp_units = 'C', speed_units = 'kt', dia_units = 'in'):
    """
    Returns returns engine power, given blade angle, rpm and flight conditions.
    """
    press_ratio = SA.alt2press_ratio(altitude, alt_units = alt_units)
    if temp == 'std':
        temp = SA.alt2temp(altitude, temp_units = temp_units, alt_units = alt_units)
    temp_ratio = U.temp_conv(temp, from_units = temp_units, to_units = 'K') / 288.15
    density_ratio = press_ratio / temp_ratio
    density = density_ratio * SA.Rho0
#    Cp = bhp2Cp(bhp, rpm, density, prop.dia, power_units = power_units, density_units = 'kg/m**3', dia_units = dia_units)
    J = advance_ratio(tas, rpm, prop.dia, speed_units = speed_units, dia_units = dia_units)
    blade_tip_mach = tip_mach(tas, rpm, temp, prop.dia, speed_units = speed_units, temp_units = temp_units, dia_units = dia_units)
    
    Cp = blade_angle2cp(prop, blade_angle, J, blade_tip_mach)
    
    bhp = cp2bhp(Cp, rpm, density, prop.dia, power_units=power_units, density_units='kg/m**3', dia_units=dia_units)
    
    return bhp

