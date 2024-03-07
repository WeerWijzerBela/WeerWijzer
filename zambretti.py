# Bron: https://github.com/sassoftware/iot-zambretti-weather-forcasting
import math as m
def CalcLuchtdrukZee(luchtdruk, hoogte, temperatuur):
    '''Luchtdruk in mbar // Hoogte in meter // Temperatuur in graden Celsius'''
    return luchtdruk * (1 - (0.0065 * hoogte) / (temperatuur + (0.0065 * hoogte) + 273.15)) ** -5.257

def CalcLuchtdrukTrend(luchtdruk, vorige_luchtdruk):
    '''Luchtdruk en vorigeluchtdruk in mbar (Luchtdruk op zee niveau) // Luchtdruk trend: 0=stijgend, 1=constant, 2=dalend, 999=onbekend'''
    verschil = luchtdruk - vorige_luchtdruk
    if luchtdruk >= 985 and luchtdruk <= 1050 and verschil <= -1.6 :
        return 2 # Dalend
    elif luchtdruk >= 947 and luchtdruk <= 1030 and verschil >= 1.6:
        return 0 # Stijgend
    elif luchtdruk >= 960 and luchtdruk <= 1033:
        return 1 # Constant
    else:
        return 999 # Onbekend

def Zambretti(luchtdruk, vorige_luchtdruk, temperatuur, hoogtenap, windrichting):
    '''Luchtdruk en vorigeluchtdruk in mbar // Temperatuur in graden Celsius // Hoogte in meter // Windrichting in graden (0-360)'''
    luchtdruk = CalcLuchtdrukZee(luchtdruk, hoogtenap, temperatuur)
    vorige_luchtdruk = CalcLuchtdrukZee(vorige_luchtdruk, hoogtenap, temperatuur)
    trend = CalcLuchtdrukTrend(luchtdruk, vorige_luchtdruk)
    weertypen = {
        1: "Kalm mooi weer",
        2: "Mooi weer",
        3: "Mooi, wordt minder kalm",
        4: "Redelijk mooi, later buien",
        5: "Buien, wordt onrustiger",
        6: "Onrustig, later regen",
        7: "Regen af en toe, later slechter",
        8: "Regen af en toe, wordt zeer onrustig",
        9: "Zeer onrustig, regen",
        10: "Kalm mooi weer",
        11: "Mooi weer",
        12: "Mooi, mogelijk buien",
        13: "Redelijk mooi, waarschijnlijk buien",
        14: "Buien met opklaringen",
        15: "Veranderlijk, enkele regenbuien",
        16: "Onrustig, af en toe regen",
        17: "Regen met regelmatige tussenpozen",
        18: "Zeer onrustig, regen",
        19: "Stormachtig, veel regen",
        20: "Kalm mooi weer",
        21: "Mooi weer",
        22: "Wordt mooi",
        23: "Redelijk mooi, verbetering",
        24: "Redelijk mooi, mogelijk buien vroeg",
        25: "Buien vroeg, verbetering",
        26: "Veranderlijk, wordt beter",
        27: "Tamelijk onrustig, later opklarend",
        28: "Onrustig, waarschijnlijk verbeterend",
        29: "Onrustig, korte mooi periodes",
        30: "Zeer onrustig, af en toe beter",
        31: "Stormachtig, mogelijk verbeterend",
        32: "Stormachtig, veel regen",
        888: "ERROR",
        999: "Onbekend weertype, kan niet voorspeld worden."
    }

    if windrichting >= 135 and windrichting <= 225:
        zWind = 2
    elif windrichting >= 315 or windrichting <= 45:
        zWind = 0
    else:
        zWind = 1

    if trend == 2:  # Dalend
        z = 127 - 0.12 * luchtdruk
    elif trend == 0: # Stijgend
        z = 144 - 0.13 * luchtdruk
    elif trend == 1: # Constant
        z = 185 - 0.16 * luchtdruk
    elif trend == 999: # Onbekend
        z = 999
    else: z = 888 # ERROR

    z = m.floor(z + zWind)
    ## Hier moet z worden geruturned, en gestuurd worden naar de api
    return weertypen[int(z)]

############################################################################################################
##     Test                                                                                               ##
############################################################################################################

print(Zambretti(1010, 1003, 21, 300, 320))