import math as m

def Zambretti(luchtdruk, vorige_luchtdruk, temperatuur, hoogtenap, windrichting):
    '''Luchtdruk en vorigeluchtdruk in mbar // Temperatuur in graden Celsius // Hoogte in meter // Windrichting in graden (0-360)'''
    # Luchtdruk omrekenen naar luchtdruk op zeeniveau
    f = (1 - (0.0065 * hoogtenap) / (temperatuur + (0.0065 * hoogtenap) + 273.15)) ** -5.257
    luchtdruk = luchtdruk * f
    vorige_luchtdruk = vorige_luchtdruk * f
    # zWind uitrekenen aan de hand van windrichting
    if windrichting >= 135 and windrichting <= 225:
        zWind = 2
    elif windrichting >= 315 or windrichting <= 45:
        zWind = 0
    else:
        zWind = 1
    # Trend berekenen
    verschil = luchtdruk - vorige_luchtdruk
    if luchtdruk >= 985 and luchtdruk <= 1050 and verschil <= -1.6 :
        trend = 2 # Dalend
        z = 127 - 0.12 * luchtdruk
    elif luchtdruk >= 947 and luchtdruk <= 1030 and verschil >= 1.6:
        trend =  0 # Stijgend
        z = 144 - 0.13 * luchtdruk
    elif luchtdruk >= 960 and luchtdruk <= 1033:
        trend =  1 # Constant
        z = 185 - 0.16 * luchtdruk
    else:
        return 999
    return m.floor(z + zWind)

def postData():
    '''Post data to the server'''