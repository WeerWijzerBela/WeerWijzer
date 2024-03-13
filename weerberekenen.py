import math as m

def Zambretti(luchtdruk, vorige_luchtdruk, windrichting):
    '''Luchtdruk en vorigeluchtdruk in mbar // Temperatuur in graden Celsius // Hoogte in meter // Windrichting in graden (0-360)'''
    # Luchtdruk omrekenen naar luchtdruk op zeeniveau
    # zWind uitrekenen aan de hand van windrichting
    if windrichting >= 135 and windrichting <= 225:
        zWind = 2
    elif windrichting >= 315 or windrichting <= 45:
        zWind = 0
    else:
        zWind = 1

    # Trend berekenen
    verschil = luchtdruk - vorige_luchtdruk
    if 985 <= luchtdruk <= 1050 and verschil <= -1.6:
        z = 127 - 0.12 * luchtdruk
    elif 947 <= luchtdruk <= 1030 and verschil >= 1.6: 
        z = 185 - 0.16 * luchtdruk
    elif 960 <= luchtdruk <= 1033:
        z = 144 - 0.13 * luchtdruk
    else:
        return 999
    return m.floor(z + zWind)

def postData():
    '''Post data to the server'''