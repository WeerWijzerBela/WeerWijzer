import requests
from datetime import datetime, date, timedelta
import sys
from logfiles.log import logging
import math as m
import os
from dotenv import load_dotenv

load_dotenv()

API = "https://weerwijzer-belastingdienst.nl"
API_KEY = os.environ.get("API_KEY")

def bereken_zambretti(luchtdruk, vorige_luchtdruk, windrichting):
    """Luchtdruk en vorigeluchtdruk in mbar // Temperatuur in graden Celsius // Windrichting in graden (0-360)"""
    # zWind uitrekenen aan de hand van windrichting
    if 225 >= windrichting >= 135:
        zWind = 2
    elif 45 >= windrichting >= 315:
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


def bereken_voorspellingen_uren(locatie, API=API):
    try:
        url_meting = API + f"/metinguren/{locatie}?api_key={API_KEY}"
        response = requests.get(url_meting)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        jsonData = response.json()

        zambrettiList = []
        for i in range(0, len(jsonData), 1):
            if 0 < i < 5:
                continue
            huidige_meting = jsonData[i]
            vorige_meting = jsonData[1] if i == 0 else jsonData[i - 3]
            zambretti_value = bereken_zambretti(
                huidige_meting["pressure"],
                vorige_meting["pressure"],
                windrichting=huidige_meting["winddirection"],
            )
            zambrettiList.append(
                {
                    "datetime": huidige_meting["datetime"],
                    "temperature": huidige_meting["temperature"],
                    "zWaarde": zambretti_value,
                }
            )

        nieuwe_voorspelling = {
            "locatie": locatie,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        url_voorspellingen = API + f"/voorspellingen?api_key={API_KEY}"
        response_metingen = requests.post(url_voorspellingen, json=nieuwe_voorspelling)
        response_metingen.raise_for_status()  # Raise an exception for non-200 status codes

        url_voorspellingen_uren = API + f"/voorspellinguren?api_key={API_KEY}"
        response_batch = requests.post(url_voorspellingen_uren, json=zambrettiList)
        response_batch.raise_for_status()  # Raise an exception for non-200 status codes

        # Verwijder oude voorspellinguren
        url_delete = API + f"/voorspellingen/{locatie}?api_key={API_KEY}"
        response_delete = requests.delete(url_delete)
        response_delete.raise_for_status()  # Raise an exception for non-200 status codes
    except Exception as e:
        logging.error("[run] Er is een fout opgetreden: %s", e)
        sys.exit(1)


def post_weer_data(locatie, API=API):
    APIEXT = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locatie}/next7days?unitGroup=metric&elements=datetime%2Ctemp%2Cwinddir%2Cpressure&include=hours%2Ccurrent&key=ZW8NCV6JP8ZUGX33D769DJ693&contentType=json"
    try:
        response = requests.get(APIEXT)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        jsonData = response.json()

        nieuwe_meting_data_metingen = {
            "locatie": locatie,
            "datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        url_metingen = API + f"/metingen?api_key={API_KEY}"
        response_metingen = requests.post(
            url_metingen, json=nieuwe_meting_data_metingen
        )
        response_metingen.raise_for_status()  # Raise an exception for non-200 status codes

        nieuwe_metinguren = [
            {
                "datetime": str(date.today())
                + " "
                + jsonData["currentConditions"]["datetime"],
                "temperature": jsonData["currentConditions"]["temp"],
                "pressure": jsonData["currentConditions"]["pressure"],
                "winddirection": jsonData["currentConditions"]["winddir"],
            }
        ]
        for data in jsonData["days"]:
            for i in data["hours"]:
                i_datetime = f"{data['datetime']} {i['datetime']}"
                if (
                    i_datetime
                    < (
                        datetime.strptime(
                            str(date.today())
                            + " "
                            + jsonData["currentConditions"]["datetime"],
                            "%Y-%m-%d %H:%M:%S",
                        ).replace(minute=0, second=0, microsecond=0)
                        - timedelta(hours=3)
                    ).strftime("%Y-%m-%d %H:%M:%S")
                    and i_datetime
                    <= str(date.today())
                    + " "
                    + jsonData["currentConditions"]["datetime"]
                ):
                    continue
                nieuwe_metinguren.append(
                    {
                        "datetime": i_datetime,
                        "temperature": i["temp"],
                        "pressure": i["pressure"],
                        "winddirection": i["winddir"],
                    }
                )
        url_metinguren = API + f"/metinguren?api_key={API_KEY}"
        response_batch = requests.post(url_metinguren, json=nieuwe_metinguren)
        response_batch.raise_for_status()  # Raise an exception for non-200 status codes

        # Verwijder oude metingen
        url_metingen = API + f"/metingen/{locatie}?api_key={API_KEY}"
        response_delete = requests.delete(url_metingen)
        response_delete.raise_for_status()  # Raise an exception for non-200 status codes

        # Bereken voorspellingen
        bereken_voorspellingen_uren(locatie, API)

    except Exception as e:
        logging.error("[run] Er is een fout opgetreden: %s", e)
        sys.exit(1)


def post_weer_data_locaties():
    try:
        url_locaties = API + "/locaties"
        response = requests.get(url_locaties)
        response.raise_for_status()  # Raise an exception for non-200 status codes
        jsonData = response.json()
        for locatie in jsonData:
            try:
                post_weer_data(locatie["locatie"])
            except Exception as e:
                logging.error("[run] Er is een fout opgetreden bij locatie: %s / %s", locatie["locatie"], e)
                continue
    except Exception as e:
        logging.error("[run] Er is een fout opgetreden: %s", e)
        sys.exit(1)


if __name__ == "__main__":
    post_weer_data_locaties()
    logging.info("[run] Weerdata is succesvol verwerkt.")
    sys.exit(0)