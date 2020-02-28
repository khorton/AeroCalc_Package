#! /usr/bin/env python3

"""
Example of how to use the o360a.py script to create a custom power chart.

# version 0.2, 28 Feb 2019

# Version History:
# vers     date       Notes
#  0.1   14 May 2006  First release.
#  0.2   28 Feb 2019  Python3 compatibility tweaks

"""

import io360a as I
import std_atm as SA

max_pwr = 200

# column widths
col1 = 8
col2 = 6
cols = 6
full_width = col1 + col2 + 12 * cols + 15

diff = 0.75 # amount the MP must be less than the atmospheric pressure.  
            # otherwise it is assumed that full throttle is reached.

print('-' * full_width)

piece = []
piece.append('Press.'.center(col1))
piece.append('Std.'.center(col2))
piece.append('110 HP -- 55% Rated'.center(cols * 4 + 3))
piece.append('130 HP -- 65% Rated'.center(cols * 4 + 3))
piece.append('150 HP -- 75% Rated'.center(cols * 4 + 3))
full_line = '|'.join(piece)
print('|' + full_line + '|')

piece = []
piece.append('Alt.'.center(col1))
piece.append('Alt.'.center(col2))
piece.append('Approx. Fuel 9.3 Gal/Hr'.center(cols * 4 + 3))
piece.append('Approx. Fuel 10.7 Gal/Hr.'.center(cols * 4 + 3))
piece.append('Approx. Fuel 12.1 Gal/Hr'.center(cols * 4 + 3))
full_line = '|'.join(piece)
print('|' + full_line + '|')

piece = []
piece.append('1000'.center(col1))
piece.append('Temp.'.center(col2))
piece.append(' '.center(cols * 4 + 3))
piece.append(' '.center(cols * 4 + 3))
piece.append(' '.center(cols * 4 + 3))
full_line = '|'.join(piece)
print('|' + full_line + '|')

piece = []
piece.append('Feet'.center(col1))
piece.append('deg F'.center(col2))
piece.append('RPM & Man. Press.'.center(cols * 4 + 3))
piece.append('RPM & Man. Press.'.center(cols * 4 + 3))
piece.append('RPM & Man. Press.'.center(cols * 4 + 3))
full_line = '|'.join(piece)
print('|' + full_line + '|')

print('-' * full_width)

piece = []
piece.append(' '.center(col1))
piece.append(' '.center(col2))
piece.append('2100'.center(cols))
piece.append('2200'.center(cols))
piece.append('2300'.center(cols))
piece.append('2400'.center(cols))
piece.append('2100'.center(cols))
piece.append('2200'.center(cols))
piece.append('2300'.center(cols))
piece.append('2400'.center(cols))
piece.append('2200'.center(cols))
piece.append('2300'.center(cols))
piece.append('2400'.center(cols))
piece.append('2500'.center(cols))
full_line = '|'.join(piece)
print('|' + full_line + '|')


for alt in range(0, 16000, 1000):
	piece = []
	piece.append(str(alt).rjust(col1))
	temp = SA.alt2temp(alt, temp_units = 'F')
	temp = int(temp)
	piece.append(str(temp).rjust(col2))
	press = SA.alt2press(alt)

	pwr = .55 * max_pwr
	for rpm in range(2100, 2500, 100):
		mp = float(I.pwr2mp(pwr, rpm, alt))
		if press - mp < diff:
			piece.append('FT'.center(col2))
		else:
			piece.append(str(round(mp,1)).center(col2))
		
	pwr = .65 * max_pwr
	for rpm in range(2100, 2500, 100):
		mp = float(I.pwr2mp(pwr, rpm, alt))
		if press - mp < diff:
			piece.append('FT'.center(col2))
		else:
			piece.append(str(round(mp,1)).center(col2))
		
	pwr = .75 * max_pwr
	for rpm in range(2200, 2501, 100):
		mp = float(I.pwr2mp(pwr, rpm, alt))
		if press - mp < diff:
			piece.append('FT'.center(col2))
		else:
			piece.append(str(round(mp,1)).center(col2))
	
	full_line = '|'.join(piece)
	print('|' + full_line + '|')

print('-' * full_width)

if __name__=='__main__':
    # run doctest to check the validity of the examples in the doc strings.
    import doctest, sys
    doctest.testmod(sys.modules[__name__])
