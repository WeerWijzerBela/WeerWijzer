# Bron: https://github.com/sassoftware/iot-zambretti-weather-forcasting
import math as m
import requests
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
        32: "Stormachtig, veel regen"
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

    z = m.floor(z + zWind)

    return weertypen[int(z)]

############################################################################################################
##     Test                                                                                               ##
############################################################################################################

############################################################################################################

# z1 = "Settled Fine"
# z2 = "Fine Weather"
# z3 = "Fine, Becoming Less Settled"
# z4 = "Fairly Fine, Showery Later"
# z5 = "Showery, Becoming More Unsettled"
# z6 = "Unsettled, Rain Later"
# z7 = "Rain at Times, Worse Later"
# z8 = "Rain at Times, Becoming Very Unsettled"
# z9 = "Very Unsettled, Rain"
#
# z10 = "Settled Fine"
# z11 = "Fine Weather"
# z12 = "Fine, Possibly Showers"
# z13 = "Fairly Fine, Showers Likely"
# z14 = "Showery Bright Intervals"
# z15 = "Changeable Some Rain"
# z16 = "Unsettled, Rain at Times"
# z17 = "Rain at Frequent Intervals"
# z18 = "Very Unsettled, Rain"
# z19 = "Stormy, Much Rain"
#
# z20 = "Settled Fine"
# z21 = "Fine Weather"
# z22 = "Becoming Fine"
# z23 = "Fairly Fine, Improving"
# z24 = "Fairly Fine, Possibly Showers Early"
# z25 = "Showery Early, Improving"
# z26 = "Changeable, Mending"
# z27 = "Rather Unsettled Clearing Later"
# z28 = "Unsettled, Probably Improving"
# z29 = "Unsettled, Short Fine Intervals"
# z30 = "Very Unsettled, Finer at Times"
# z31 = "Stormy, Possibly Improving"
# z32 = "Stormy, Much Rain"

############################################################################################################

# z1 = "kalm mooi weer"
# z2 = "mooi weer"
# z3 = "mooi, wordt minder kalm"
# z4 = "redelijk mooi, later buien"
# z5 = "buien, wordt onrustiger"
# z6 = "onrustig, later regen"
# z7 = "regen af en toe, later slechter"
# z8 = "regen af en toe, wordt zeer onrustig"
# z9 = "zeer onrustig, regen"
#
# z10 = "kalm mooi weer"
# z11 = "mooi weer"
# z12 = "mooi, mogelijk buien"
# z13 = "redelijk mooi, waarschijnlijk buien"
# z14 = "buien met opklaringen"
# z15 = "veranderlijk, enkele regenbuien"
# z16 = "onrustig, af en toe regen"
# z17 = "regen met regelmatige tussenpozen"
# z18 = "zeer onrustig, regen"
# z19 = "stormachtig, veel regen"
#
# z20 = "kalm mooi weer"
# z21 = "mooi weer"
# z22 = "wordt mooi"
# z23 = "redelijk mooi, verbetering"
# z24 = "redelijk mooi, mogelijk buien vroeg"
# z25 = "buien vroeg, verbetering"
# z26 = "veranderlijk, wordt beter"
# z27 = "tamelijk onrustig, later opklarend"
# z28 = "onrustig, waarschijnlijk verbeterend"
# z29 = "onrustig, korte mooi periodes"
# z30 = "zeer onrustig, af en toe beter"
# z31 = "stormachtig, mogelijk verbeterend"
# z32 = "stormachtig, veel regen"