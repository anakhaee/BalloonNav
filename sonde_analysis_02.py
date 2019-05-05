import numpy as np
from matplotlib import pyplot as plt
import sys


def read_file_Wyoming(filename):
    # read in file
    f = open(filename, "rb")

    pressure = []  # [mb] (original format) or in [mb/10] (new format)
    height = []  # [km]
    temperature = []  # [degree C]
    dewpoint = []  # [degree C/10] dewpoint temperature
    wind_dir = []  # [degree]
    wind_speed = []  # [m/s]
    new_measurement = []

    s = np.array(f.read().split('\n'))

    for i in range(len(s)):
        l = s[i].split()
        if len(l) == 11 and not l[0] in ['PRES', 'hPa']:
            pressure.append(float(l[0]))
            height.append(float(l[1]) * 10 ** (-3))
            temperature.append(float(l[-1]) + 273.15)
            dewpoint.append(float(l[3]) + 273.15)
            wind_dir.append(int(l[6]))
            wind_speed.append(int(l[7]) * 0.514444)
        if len(l) == 5 and l[0] == 'Station':
            new_measurement.append(len(height))

    return np.array(pressure), np.array(height), np.array(temperature), np.array(dewpoint), np.array(
        wind_dir), np.array(wind_speed), np.array(new_measurement)


def read_file_NOAA(filename):
    # read in file
    f = open(filename, "rb")

    random_nr = []  # type of identification line
    pressure = []  # [mb] (original format) or in [mb/10] (new format)
    height = []  # [km]
    temperature = []  # [degree C]
    dewpoint = []  # [degree C/10] dewpoint temperature
    wind_dir = []  # [degree]
    wind_speed = []  # [m/s]
    new_measurement = []

    s = np.array(f.read().split('\n'))

    for i in range(len(s)):
        l = s[i].split()
        if len(l) == 7 and int(l[0]) in [2, 3, 4, 5, 6, 7, 8, 9] and not '99999' in l[5] and not '99999' in l[2]:
            random_nr.append(int(l[0]))
            pressure.append(int(l[1]))
            height.append(int(l[2]) * 10 ** (-3))
            temperature.append(int(l[3])/10. + 273.15)
            dewpoint.append(int(l[4])/10. + 273.15)
            wind_dir.append(int(l[5]))
            wind_speed.append(int(l[6]) / 10.)
        if len(l) == 7 and int(l[0]) == 1:
            new_measurement.append(len(random_nr))

    return np.array(random_nr), np.array(pressure), np.array(height), np.array(temperature), np.array(
        dewpoint), np.array(wind_dir), np.array(wind_speed), np.array(new_measurement)


def Buck_eq(T):
    if T > 0 :
        P = 0.61121*np.exp((18.678 - (T/234.5))*(T/(257.14+T)))
    else:
        P = 0.61115*np.exp((23.036 - (T/333.7))*(T/(279.82+T)))
    return P


def RH_eq(T_dew, T):
    P_w = Buck_eq(T_dew)
    P_w_s = Buck_eq(T)
    RH = P_w/P_w_s
    return RH


def Molar_eq(RH):
    M_dair = 28.9647 # [g/mol] Molar weight dry air
    M_h2O = 18.01528 # [g/mol] Molar weight water
    M_air = M_dair * (1. - RH) + M_h2O * RH
    return M_air

def R_eq(M_air):
    k = 1.381 * 10**(-23.) # [J/K] Boltzman Constant
    N_A = 6.022 * 10**23.  # [1/mol] Avogadro Number
    R = (k*N_A)/M_air
    return R

def Density_eq(dewpoint,temperature):
    density = []
    for i in range(len(temperature)):
        RH = RH_eq(dewpoint[i], temperature[i])
        M_air = Molar_eq(RH)
        R = R_eq(M_air)
        density.append(float(pressure[i]/(R*temperature[i])))
    return density

def mean_layers(filename, height, temperature, pressure, density, r_humidity, wind_speed, wind_dir,  clear=False):

    i = 0
    while True:

        lay = np.where([ (((i+1)*0.5)+np.min(height)) > n >= ((i*0.5)+np.min(height)) for n in height])[0]
        i+=1
        if len(lay) == 0:
            break;

        np.mean(wind_speed[lay])
        np.std(wind_speed[lay])

        np.mean(wind_dir[lay])
        np.std(wind_dir[lay])

    return

def print_data(filename, height, temperature, pressure, density, r_humidity, clear=False):
    if clear==False:
        f = open("Output_Wind_Layers.txt","a+")
    else:
        f = open("Output_Wind_Layers.txt","w+")
    f.write("%s \r\n" % filename)
    f.write('  Height [Km] ')
    f.write('  Temperature [K] ')
    f.write(' Pressure [mBar]  ')
    f.write('  Densisty  [kg/m3]')
    f.write('  Relative Humidity  ')
    f.write("\r\n")

    for i in range(len(height)):
        f.write(('  %f   ') % (height[i]))
        f.write(('    %f   ') % (temperature[i]))
        f.write(('     %f   ') % (pressure[i]))
        f.write(('     %f  ') % (density[i]))
        f.write(('         %f  ') % (r_humidity[i]))
        f.write("\r\n")
    f.close()


if __name__=='__main__':

    #old_settings = np.seterr(all='ignore')  # seterr to known value

    # filename = sys.argv[1]
    filename = 'sonde_data/Andoya_October_2015.txt'
    mode = 'wyoming'

    if mode == 'NOAA':
        random_nr, pressure, height, temperature, dewpoint, wind_dir, wind_speed, new_measurement = read_file_NOAA(
            filename)
    if mode == 'wyoming':
        pressure, height, temperature, dewpoint, wind_dir, wind_speed, new_measurement = read_file_Wyoming(filename)
    roi = np.where([i >= 15 for i in height])[0]

    density = np.array(Density_eq(dewpoint, temperature))
    r_humidity = np.array([RH_eq(dewpoint[i], temperature[i]) for i in range(len(temperature))])
    print r_humidity

    print_data(filename, height, temperature, pressure, density, r_humidity)

    np.where([i >= 15 for i in height])[0]