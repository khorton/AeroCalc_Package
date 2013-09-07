AeroCalc is a pure python package with modules that perform various aeronautical 
engineering related calculations.

This package contains the following modules:

airspeed         airspeed conversions and calculations.  Provides interactive
                 mode when run directly, e.g. 'python airspeed.py'.

cd               drag related functions

cl               lift related functions

constants        provides various constants to be used by all modules

data_file        read data from text data files

default_units    defines default units to be used by all modules.  May be 
                 overridden by a user units file.
                 
interpolator     perform two and three dimensional interpolation4

least_sq_fit_gnuplot  functions to draw best fit lines in Gnuplot

ssec             Currently contains functions to calculate true airspeed given 
                 GPS ground speed and track data from multiple runs on various 
                 tracks.  Will eventually also contain various calculations 
                 related to static source error correction.

std_atm          standard atmosphere parametres and calculations.

unit_conversion  convert various aeronautical parametres between commonly
                 used units.

val_input        validates user input when in interactive mode.

engine/piston    functions applicable to all piston engines

engine/lycoming/io360a calculate engine power for Lycoming IO-360-A and -C
                       engines

engine/lycoming/360a  calculate engine power for Lycoming O-360-A engines

engine/lycoming/lycoming_power  calculate power for Lycoming engines based on 
                                fuel flow data
                                

