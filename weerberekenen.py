import math as m
import requests
from datetime import datetime, date, timedelta
import sys
from logfiles.log import logging
API = "http://localhost:8000"

def bereken_zambretti(luchtdruk, vorige_luchtdruk, windrichting):
    '''Luchtdruk en vorigeluchtdruk in mbar // Temperatuur in graden Celsius // Hoogte in meter // Windrichting in graden (0-360)'''
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
        return m.floor(127 - 0.12 * luchtdruk + zWind)
    elif 947 <= luchtdruk <= 1030 and verschil >= 1.6:
        return m.floor(185 - 0.16 * luchtdruk + zWind)
    elif 960 <= luchtdruk <= 1033:
        return m.floor(144 - 0.13 * luchtdruk + zWind)
    else:
        return 999

def post_zambretti():
    try:
        response = requests.get(API + '/metinguren')
        if response.status_code != 200:
            logging.error("Fout bij het ophalen van gegevens van /metinguren. Statuscode: %d", response.status_code)
            return
        logging.info("Gegevens succesvol opgehaald van /metinguren. Statuscode: %d", response.status_code)
        jsonData = response.json()
        zambrettiList = []
        for i in range(0, len(jsonData), 1):
            if 0 < i < 5:
                continue
            huidige_meting = jsonData[i]
            if i == 0:
                vorige_meting = jsonData[1]
            else:
                vorige_meting = jsonData[i - 3]
            zambretti_value = bereken_zambretti(huidige_meting['pressure'], vorige_meting['pressure'], windrichting = huidige_meting['winddirection'])
            zambrettiList.append({
                "datetime" : huidige_meting["datetime"],
                "temperature": huidige_meting["temperature"],
                "zwaarde": zambretti_value
            })

        print(zambrettiList)

    except Exception as e:
        logging.error("Er is een fout opgetreden bij het berekenen van Z: %s", str(e))

post_zambretti()

print(bereken_zambretti(1010, 1011.9, 196))