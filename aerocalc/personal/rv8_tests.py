#! /usr/bin/env python3

import rv8_test as R
import prop_map as PM

p0 = PM.Prop('7666-4RV')
p1 = PM.Prop('7666-2RV')
p2 = PM.Prop('MTV-12-B-183-59B')
props = [p0, p1, p2]

# print 'Running run_tests()'
# R.run_tests()

# for prop in props:
#     print 'WOT speed of %.1f KTAS at 2700 rpm at sea level with prop %s' % (R.WOT_speed(prop, 0), prop.model)
# 
# print ''
# for prop in props:
#     print 'WOT speed of %.1f KTAS at 2700 rpm at 8000 ft with prop %s' % (R.WOT_speed(prop, 8000), prop.model)
# 
# print ''
# for prop in props:
#     print 'WOT speed of %.1f KTAS at 2600 rpm at 8000 ft with prop %s' % (R.WOT_speed(prop, 8000, rpm = 2600), prop.model)
# 
# print ''
# for prop in props:
#     print 'WOT speed of %.1f KTAS at 2500 rpm at 8000 ft with prop %s' % (R.WOT_speed(prop, 8000, rpm = 2500), prop.model)
# 
# print ''
# for prop in props:
#     print 'WOT speed of %.1f KTAS at 2400 rpm at 8000 ft with prop %s' % (R.WOT_speed(prop, 8000, rpm = 2400), prop.model)
# 
# print ''
# for prop in props:
#     print 'WOT speed of %.1f KTAS at 2300 rpm at 8000 ft with prop %s' % (R.WOT_speed(prop, 8000, rpm = 2300), prop.model)
# 
# print ''
# for prop in props:
#     print 'WOT speed of %.1f KTAS at 2100 rpm at 8000 ft with prop %s' % (R.WOT_speed(prop, 8000, rpm = 2100), prop.model)
# print ''

# for prop in props:
#     print prop.model
#     R.roc_sweep(prop, 80, 120, 1, 0, 1800, 200, 2700)
#     print ''

# for prop in props:
#     # print prop.model
#     meas, mroc = R.roca(prop, 0)
#     print 'Max ROC of %.0f ft/mn at %.1f EAS with prop %s' % (mroc, meas, prop.model)
# print ''
# 
# for prop in props:
#     # print prop.model
#     meas, mroc = R.aoca(prop, 0)
#     print 'Max climb gradient of %.2f %% at %.1f EAS with prop %s' % (mroc * 100, meas, prop.model)
# print ''

for prop in props:
    print prop.model
    print "Data for 200 hp, 2700 rpm, 80 kt, sea level"
    PM.prop_data(prop, 200, 2700, 80, 0)  