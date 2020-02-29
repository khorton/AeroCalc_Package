#!/usr/bin/env python3


import commands

def l(t):
    """Return latitude or longitude in degrees, given an input 
    string like:
    51 34 6 N
    
    or:
    0 41 29 E
    
    This is the format originally used on the live tracking page for Chalkie Stobbart's 
    Cape Town to London solo record attempt flight:    
    
    http://www.henshaw-challenge.com/dnn/FollowFlight/tabid/62/Default.aspx
    """
    t=t.lstrip(' ')
    t=t.rstrip(' ')
    
    items = t.split(' ')
    deg = int(items[0][:-2])
    mn = int(items[1][:-3])
    sec = int(items[2][:-3])
    NSEW = t[-1:]
    if NSEW == 'S':
        k = -1
    elif NSEW == 'E':
        k = -1
    else:
        k = 1
    
    return (k * (deg + mn/60 + sec/3600))
    
def ll(t):
    """Return tuple of latitude and longitude in degrees, given an input 
    string like:
    51d 34' 6" N   0d 41' 29" E
    
    This is the format used on the live tracking page for Chalkie Stobbart's 
    Cape Town to London solo record attempt flight:    
    
    http://www.henshaw-challenge.com/dnn/FollowFlight/tabid/62/Default.aspx
    """
    # print t
    t=t.lstrip(' ')
    t=t.rstrip(' ')
    
    items = t.split(' ')
    lat_deg = int(items[0][:-2])
    lat_mn = int(items[1][:-3])
    lat_sec = int(items[2][:-3])
    NS = items[3]
    if NS == 'S':
        lat_k = -1
    else:
        lat_k = 1

    long_deg = int(items[-4][:-2])
    long_mn = int(items[-3][:-3])
    long_sec = int(items[-2][:-3])
    EW = items[-1]
    if EW == 'E':
        long_k = -1
    else:
        long_k = 1
    
    return (lat_k * (lat_deg + lat_mn/60 + lat_sec/3600), long_k * (long_deg + long_mn/60 + long_sec/3600))
    
def lll():
    """Return tuple of latitude and longitude in degrees, copying an input 
    string like from the system clipboard:
    51d 34' 6" N   0d 41' 29" E
    
    This is the format used on the live tracking page for Chalkie Stobbart's 
    Cape Town to London solo record attempt flight:    
    
    http://www.henshaw-challenge.com/dnn/FollowFlight/tabid/62/Default.aspx
    """
    t=commands.getoutput('pbpaste')
    # print t
    t=t.lstrip(' ')
    t=t.rstrip(' ')
    
    items = t.split(' ')
    # print items
    lat_deg = int(items[0][:-1])
    lat_mn = int(items[1][:-1])
    lat_sec = int(items[2][:-1])
    NS = items[3]
    if NS == 'S':
        lat_k = -1
    else:
        lat_k = 1

    long_deg = int(items[-4][:-1])
    long_mn = int(items[-3][:-1])
    long_sec = int(items[-2][:-1])
    EW = items[-1]
    if EW == 'E':
        long_k = -1
    else:
        long_k = 1
    # print lat_deg, lat_mn, lat_sec, lat_k, long_deg, long_mn, long_sec, long_k
    return (lat_k * (lat_deg + lat_mn/60 + lat_sec/3600), long_k * (long_deg + long_mn/60 + long_sec/3600))
    
    