#!/usr/bin/env python

"""
Performs various functions with data files
"""

##############################################################################
# Copyright (c) 2006, Kevin Horton
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
##############################################################################
#
# version 0.11, 30 Jun 2009
#
# Version History:
# vers     date     Notes
# 0.10   18 Oct 08  First public release.
# 0.11   30 Jun 09  Python 3.0 compatibility.  Removed from __future__ 
#                   import division
# 0.12   06 Sep 10  Add col_index()
##############################################################################
#
# To Do:  1.

# Done: 1.
##############################################################################

from __future__ import division
import airspeed as A
import math as M
import std_atm as SA
import unit_conversion as U
import re
import numpy as N
import numpy.core.records as NR
import pickle

def col_index(data_file, col_name, col_name_row=3, header_rows=4, record_sep='\t'):
    """
    Returns column index for col_name
    
    data_file = text file with the data.  One row per data record
    col_name = text that identifies the column with the desired data.  This text must exactly match what is in the data file.
    col_name_row = the row number that has the column names to be matched to col_name, with the row numbers starting at 1
    header_rows = the number of header rows before the data starts
    record_sep = the character(s) that separate the data items in the data record
    """
    DATA = open(data_file)
    
    for i in range(col_name_row - 1):
        # advance to row with column names
        DATA.readline()
        
    col_names = DATA.readline().split(record_sep)
    col_index = col_names.index(col_name)

    return col_index

def grab_data(data_file, col_name, time_slice, col_name_row=3, time_slice_col=0, header_rows=4, record_sep='\t', min_max=False):
    """
    pulls data from a file and returns the average of a data item over a time slice
    
    data_file = text file with the data.  One row per data record
    col_name = text that identifies the column with the desired data.  This text must exactly match what is in the data file.
    time_slice is a tuple with start and end times.  The format of the times must exactly match that of the times in the data.
    time_slice_col = the column number that has the time slice data
    col_name_row = the row number that has the column names to be matched to col_name, with the row numbers starting at 1
    header_rows = the number of header rows before the data starts
    record_sep = the character(s) that separate the data items in the data record
    """
    
    DATA = open(data_file)
    
    for i in range(col_name_row - 1):
        # advance to row with column names
        DATA.readline()
        
    col_names = DATA.readline().split(record_sep)
    col_index = col_names.index(col_name)
    
    for  i in range(header_rows - col_name_row):
        # advance to firs row with data
        DATA.readline()
        
    data_items = DATA.readline().split(record_sep)
    
    count, data_sum = 0, 0
    while data_items[time_slice_col] < time_slice[0]:
        data_items = DATA.readline().split(record_sep)
        try:
            value = float(data_items[col_index])
            min_val = value
            max_val = value
        except ValueError:
            pass
    while data_items[time_slice_col] <= time_slice[1]:
        try:
            value = float(data_items[col_index])
            data_sum += value
            count += 1
            min_val = min(min_val, value)
            max_val = max(max_val, value)
        except ValueError:
            pass
        data_items = DATA.readline().split(record_sep)
        
        data_ave = data_sum / count
    if min_max:
        return data_ave, min_val, max_val
    else:
        return data_ave

def load_array(data_file, col_name_row=3, header_rows=4, time_slice_col=0, time_slice='', record_sep='\t'):
    """
    Returns a records array (from numpy.core.records)
    
    data_file = text file with the data.  One row per data record
    col_name_row = the row number that has the column names to be matched to col_name, with the row numbers starting at 1
    header_rows = the number of header rows before the data starts
    time_slice_col = the column number that has the time slice data
    record_sep = the character(s) that separate the data items in the data record
    """
    DATA = open(data_file)
    data_list = []
    header_names = []
    
    for i in range(col_name_row - 1):
        # advance to row with column names
        DATA.readline()
        
    col_names = DATA.readline().split(record_sep)
    for name in col_names:
        # replace white space in name with '_' to avoid errors later
        name = re.sub(r'\s+',r'_',name)
        header_names.append(name)
    for  i in range(header_rows - col_name_row):
        # advance to firs row with data
        line = DATA.readline()
    
    # advance to start of desired data if it is specified
    try:
        if time_slice[0]:
            data_items = DATA.readline().split(record_sep)
            while data_items[time_slice_col] < time_slice[0]:
                data_items = DATA.readline().split(record_sep)
    except IndexError:
#         print "error 0"
        pass
    
    while 1:
        data_items = DATA.readline().split(record_sep)
        if data_items[0]=="":
#             return data_list, header_names
            return NR.fromrecords(data_list, names=header_names)
        
        # check to see if time is past end of desired data if it is specified
        try:
            if time_slice[1]:
                try:
                    if data_items[time_slice_col] > time_slice[1]:
#                         return data_list, header_names
                        return NR.fromrecords(data_list, names=header_names)
                except IndexError:
#                         return data_list, header_names
                        return NR.fromrecords(data_list, names=header_names)
        except IndexError:
            pass
        for n, item in enumerate(data_items):
            try:
                data_items[n] = float(item)
            except ValueError:
                # pass
                if data_items[n] == '':
                    data_items[n] = 0.0
        data_list.append(data_items[:-1])
    
#     return data_list
    
def pickle_data(file_name, *objects):
    file_handle = file(file_name, 'w')
    pickle.dump(objects, file_handle)

