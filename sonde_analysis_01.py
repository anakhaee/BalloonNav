#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 13:18:29 2018

@author: nehir
"""

import numpy as np
from matplotlib import pyplot as plt
import sys




def read_file_Wyoming(filename):
    #read in file
    f = open(filename, "rb")
    
    pressure = []   #[mb] (original format) or in [mb/10] (new format)
    height = []     #[km]
    temperature = []#[degree C]
    dewpoint = []   #[degree C/10] dewpoint temperature
    wind_dir = []   #[degree]
    wind_speed = [] #[m/s]
    new_measurement = []

    s = np.array(f.read().split('\n'))
    
    for i in range(len(s)):
        l = s[i].split()
        if len(l)==11 and not l[0] in ['PRES', 'hPa']:
            pressure.append(float(l[0]))
            height.append(float(l[1])*10**(-3))
            temperature.append(float(l[-1]))
            dewpoint.append(float(l[3]))
            wind_dir.append(int(l[6]))
            wind_speed.append(int(l[7])*0.514444)
        if len(l)==5 and l[0]=='Station':
            new_measurement.append(len(height))

    return np.array(pressure), np.array(height), np.array(temperature), np.array(dewpoint), np.array(wind_dir), np.array(wind_speed),  np.array(new_measurement)


def read_file_NOAA(filename):
    #read in file
    f = open(filename, "rb")
    
    random_nr = []  #type of identification line
    pressure = []   #[mb] (original format) or in [mb/10] (new format)
    height = []     #[km]
    temperature = []#[degree C]
    dewpoint = []   #[degree C/10] dewpoint temperature
    wind_dir = []   #[degree]
    wind_speed = [] #[m/s]
    new_measurement = []


    s = np.array(f.read().split('\n'))
    
    for i in range(len(s)):
        l = s[i].split()
        if len(l)==7 and int(l[0]) in [2,3,4,5,6,7,8,9] and not '99999' in l[5] and not'99999' in l[2]:
            random_nr.append(int(l[0]))
            pressure.append(int(l[1]))
            height.append(int(l[2])*10**(-3))
            temperature.append(int(l[3]))
            dewpoint.append(int(l[4]))
            wind_dir.append(int(l[5]))
            wind_speed.append(int(l[6])/10.)
        if len(l)==7 and int(l[0])==1:
            new_measurement.append(len(random_nr))
    return np.array(random_nr), np.array(pressure), np.array(height), np.array(temperature), np.array(dewpoint), np.array(wind_dir), np.array(wind_speed),  np.array(new_measurement)


def carthesian_wind(wind_dir, wind_speed):
    wind_N = np.array([wind_speed[i]*np.cos(wind_dir[i]*np.pi/180.) for i in range(len(wind_speed))])
    wind_E = np.array([-wind_speed[i]*np.sin(wind_dir[i]*np.pi/180.) for i in range(len(wind_speed))])
    return wind_N, wind_E


def plot_wind(wind_N, wind_E, new_measurement, mean_wind, max_min):
    
    plt.figure('Wind N direction') 
    plt.axvline(x=0.0, linestyle='--', color='k')
    plt.axvline(x=mean_wind[0,0], linestyle='--', color='k')
    #plt.axhline(y=20, linestyle='--', color='k')
    #plt.axhline(y=30, linestyle='--', color='k')
    height_barrier = 25.5
    for i in range(len(new_measurement)-1):
        if height[new_measurement[i+1]-1]>height_barrier:
            plt.plot(wind_N[new_measurement[i]:new_measurement[i+1]-1], height[new_measurement[i]:new_measurement[i+1]-1])
    plt.ylabel('height [km]', fontsize=14)
    plt.xlabel('wind N [m/s]', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    
    plt.figure('Wind E direction')  
    plt.axvline(x=0.0, linestyle='--', color='k')
    plt.axvline(x=mean_wind[0,1], linestyle='--', color='k')
    #plt.axhline(y=20, linestyle='--', color='k')
    #plt.axhline(y=30, linestyle='--', color='k')
    for i in range(len(new_measurement)-1):
        if height[new_measurement[i+1]-1]>height_barrier:
            plt.plot(wind_E[new_measurement[i]:new_measurement[i+1]-1], height[new_measurement[i]:new_measurement[i+1]-1])
    plt.ylabel('height [km]', fontsize=14)
    plt.xlabel('wind E [m/s]', fontsize=14)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.show()
    

def mean_wind(wind_N, wind_E, roi):
    mean_N = np.mean(wind_N[roi])
    mean_E = np.mean(wind_E[roi])
    err_mean_N = np.std(wind_N[roi])
    err_mean_E = np.std(wind_E[roi])
    return np.array([[mean_N, mean_E], [err_mean_N, err_mean_E]])
    


def maxima_minima(wind_N, wind_E, roi, new_measurement):
    maxima_N = []
    minima_N = []
    maxima_E = []
    minima_E = []
    
    for i in range(len(new_measurement)-1):
        maxima_N.append(np.max(wind_N[roi[i]:new_measurement[i+1]-1]))
        minima_N.append(np.min(wind_N[roi[i]:new_measurement[i+1]-1]))
        maxima_E.append(np.max(wind_E[roi[i]:new_measurement[i+1]-1]))
        minima_E.append(np.min(wind_E[roi[i]:new_measurement[i+1]-1]))
    
    maximum_N = np.mean(maxima_N)
    minimum_N = np.mean(minima_N)
    maximum_E = np.mean(maxima_E)
    minimum_E = np.mean(minima_E)
    err_maximum_N = np.std(maxima_N)
    err_minimum_N = np.std(minima_N)
    err_maximum_E = np.std(maxima_E)
    err_minimum_E = np.std(minima_E)
    
    abs_maximum_N = np.max(maxima_N)
    abs_minimum_N = np.min(minima_N)
    abs_maximum_E = np.max(maxima_E)
    abs_minimum_E = np.min(minima_E)
        
    return np.array([[maximum_N, minimum_N, maximum_E, minimum_E], [err_maximum_N, err_minimum_N, err_maximum_E, err_minimum_E],[abs_maximum_N, abs_minimum_N, abs_maximum_E, abs_minimum_E]])


def rate_of_change(wind_N, wind_E, roi, height):
    wind_change_N = []
    wind_change_E = []
    for i in range(len(roi)-1):
        if abs(roi[i+1]-roi[i])<=1 and not (height[roi[i+1]]-height[roi[i]])==0:
            wind_change_N.append(1.*np.abs((wind_N[roi[i+1]]-wind_N[roi[i]])/(height[roi[i+1]]-height[roi[i]])))
            wind_change_E.append(1.*np.abs((wind_E[roi[i+1]]-wind_E[roi[i]])/(height[roi[i+1]]-height[roi[i]])))
    mean_change_N = np.mean(wind_change_N)
    mean_change_E = np.mean(wind_change_E)
    err_change_N = np.std(wind_change_N)
    err_change_E = np.std(wind_change_E)
    return np.array([[mean_change_N, mean_change_E], [err_change_N, err_change_E]])


def print_data(filename, mean_wind, max_min, wind_change, clear=False):
    if clear==False:
        f = open("radiosondes_output.txt","a+")
    else:
        f = open("radiosondes_output.txt","w+")
    f.write("%s \r\n" % filename)
    f.write('mean_N: %f +/- %f m/s \r\n' % (mean_wind[0,0],mean_wind[1,0]))
    f.write('mean_E: %f +/- %f m/s \r\n' % (mean_wind[0,1],mean_wind[1,1]))
    f.write('max_N: %f +/- %f m/s \r\n' % (max_min[0,0],max_min[1,0]))
    f.write('min_N: %f +/- %f m/s \r\n' % (max_min[0,1],max_min[1,1]))
    f.write('max_E: %f +/- %f m/s \r\n' % (max_min[0,2],max_min[1,2]))
    f.write('min_E: %f +/- %f m/s \r\n' % (max_min[0,3],max_min[1,3]))
    f.write('max_change_N: %f +/- %f m/s \r\n' % (wind_change[0,0],wind_change[1,0]))
    f.write('max_change_E: %f +/- %f m/s \r\n' % (wind_change[0,1],wind_change[1,1]))
    f.write("\r\n\n")
    f.close()


if __name__=='__main__':
    #filename = sys.argv[1]
    filename = 'sonde_data/Sodankyla_October_2017.txt'
    mode = 'NOAA'
    
    if mode == 'NOAA':
        random_nr, pressure, height, temperature, dewpoint, wind_dir, wind_speed, new_measurement = read_file_NOAA(filename)
    if mode == 'wyoming':
        pressure, height, temperature, dewpoint, wind_dir, wind_speed, new_measurement = read_file_Wyoming(filename)
    roi = np.where([i>=20 for i in height])[0]

    wind_N, wind_E = carthesian_wind(wind_dir, wind_speed)
    mean_wind = mean_wind(wind_N, wind_E, roi)
    max_min = maxima_minima(wind_N, wind_E, roi, new_measurement)
    wind_change = rate_of_change(wind_N, wind_E, roi, height)
    
#    print_data(filename, mean_wind, max_min, wind_change)

    plot_wind(wind_N, wind_E, new_measurement, mean_wind, max_min)