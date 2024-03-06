import math as m
import datetime

def ZambrettiAPI(luchtdruk, vorige_luchtdruk, temperatuur, hoogtenap, windrichting):
    '''Luchtdruk en vorigeluchtdruk in mbar // Temperatuur in graden Celsius // Hoogte in meter // Windrichting in graden (0-360)'''
    # Luchtdruk omrekenen naar luchtdruk op zeeniveau
    luchtdruk = luchtdruk * (1 - (0.0065 * hoogtenap) / (temperatuur + (0.0065 * hoogtenap) + 273.15)) ** -5.257
    vorige_luchtdruk = vorige_luchtdruk * (1 - (0.0065 * hoogtenap) / (temperatuur + (0.0065 * hoogtenap) + 273.15)) ** -5.257
    # Trend berekenen
    verschil = luchtdruk - vorige_luchtdruk
    if luchtdruk >= 985 and luchtdruk <= 1050 and verschil <= -1.6 :
        trend = 2 # Dalend
    elif luchtdruk >= 947 and luchtdruk <= 1030 and verschil >= 1.6:
        trend =  0 # Stijgend
    elif luchtdruk >= 960 and luchtdruk <= 1033:
        trend =  1 # Constant
    else:
        trend =  999 # Onbekend
    # zWind uitrekenen aan de hand van windrichting
    if windrichting >= 135 and windrichting <= 225:
        zWind = 2
    elif windrichting >= 315 or windrichting <= 45:
        zWind = 0
    else:
        zWind = 1
    # z uitrekenen aan de hand van trend en luchtdruk
    if trend == 2:  # Dalend
        z = 127 - 0.12 * luchtdruk
    elif trend == 0: # Stijgend
        z = 144 - 0.13 * luchtdruk
    elif trend == 1: # Constant
        z = 185 - 0.16 * luchtdruk
    elif trend == 999: # Onbekend
        z = 999
    else: z = 888 # ERROR
    # zWind bij z optellen en afronden
    z = m.floor(z + zWind)
    return z, trend, temperatuur


print(ZambrettiAPI(1010, 1005, 20, 34, 180)) # 1010 mbar, 1005 mbar, 20 graden, 0 meter, 180 graden windrichting