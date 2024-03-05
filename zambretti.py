# Bron: https://www.meteoalarm.eu/documents/other/Zambretti.pdf

def CalcLuchtdrukZee(luchtdruk, hoogte, temperatuur):
    # Luchtdruk in mbar
    # Hoogte in meter
    # Temperatuur in graden Celsius
    return luchtdruk * (1 - (0.0065 * hoogte) / (temperatuur + (0.0065 * hoogte) + 273.15)) ** -5.257

def CalcLuchtdrukTrend(luchtdruk, vorige_luchtdruk):
    # Luchtdruk trend: 0=stijgend, 1=constant, 2=dalend
    print("niks")

def Zambretti(luchtdruk, luchtdruk_trend, seizoen):
    # Luchtdruk in mbar
    # Luchtdruk trend: 0=stijgend, 1=constant, 2=dalend
    # Seizoen: 0=winter, 1=lente, 2=zomer, 3=herfst
    print("niks")

print(CalcLuchtdrukZee(1013.25, 36, 21))