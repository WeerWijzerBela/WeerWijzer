import requests
from datetime import datetime, date, timedelta
import sys
from logfiles.log import logging

LOCATIE = "Apeldoorn"
APIEXT = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{LOCATIE}/next7days?unitGroup=metric&elements=datetime%2Ctemp%2Cwinddir%2Cpressure&include=hours%2Ccurrent&key=ZW8NCV6JP8ZUGX33D769DJ693&contentType=json"
API = "http://localhost:8000"
def post_external_data():
    try:
        response = requests.get(APIEXT)
        if response.status_code != 200:
            logging.error("Fout bij het ophalen van gegevens van /VisualCrossingWebServices. Statuscode: %d", response.status_code)
            sys.exit(1)
        else:
            logging.info("Gegevens succesvol opgehaald van /VisualCrossingWebServices. Statuscode: %d", response.status_code)
            jsonData = response.json()
            nieuwe_meting_data_metingen = {
                "locatie": LOCATIE,
                "datetime": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            url_metingen = API + '/metingen'
            response_metingen = requests.post(url_metingen, json=nieuwe_meting_data_metingen)
            if response_metingen.status_code != 201:
                logging.error("Fout bij het verzenden van gegevens - /meting. Statuscode: %d", response_metingen.status_code)
                sys.exit(1)
            else:
                logging.info("Nieuwe meting succesvol toegevoegd aan de database. Statuscode: %d", response_metingen.status_code)
                nieuwe_metinguren = [{
                    "datetime": str(date.today()) + ' ' + jsonData['currentConditions']['datetime'],
                    "temperature": jsonData['currentConditions']['temp'],
                    "pressure": jsonData['currentConditions']['pressure'],
                    "winddirection": jsonData['currentConditions']['winddir']
                }]
                for data in jsonData["days"]:
                    for i in data['hours']:
                        i_datetime = f"{data['datetime']} {i['datetime']}"
                        if (i_datetime < (datetime.strptime(str(date.today()) + ' ' + jsonData['currentConditions']['datetime'],
                                                            '%Y-%m-%d %H:%M:%S').replace(minute=0, second=0,
                                                                                             microsecond=0) - timedelta(
                            hours=3)).strftime('%Y-%m-%d %H:%M:%S')
                                and i_datetime <= str(date.today()) + ' ' + jsonData['currentConditions']['datetime']):
                            continue
                        nieuwe_metinguren.append({
                            "datetime": i_datetime,
                            "temperature": i['temp'],
                            "pressure": i['pressure'],
                            "winddirection": i['winddir']
                        })
                # Voeg nieuwe metingen voor 'metinguren' tabel toe in batches
                url_metinguren = API + '/metinguren'
                batch_size = 190
                for i in range(0, len(nieuwe_metinguren), batch_size):
                    batch_data = nieuwe_metinguren[i:i + batch_size]
                    response_batch = requests.post(url_metinguren, json=batch_data)
                    if response_batch.status_code != 201:
                        logging.error("Fout bij het verzenden van batchgegevens - /metinguren. Statuscode: %d", response_batch.status_code)
                        sys.exit(1)
                    else:
                        logging.info("Nieuwe metinguren succesvol toegevoegd aan de database. Statuscode: %d", response_batch.status_code)
                        url_metinguren = API + '/deletemetingen'
                        response_delete = requests.delete(url_metinguren)
                        if response_delete.status_code != 202:
                            logging.error("Fout bij het verwijderen van oude metingen - /deletemetingen. Statuscode: %d", response_delete.status_code)
                            sys.exit(1)
                        else:
                            logging.info("Oude metingen succesvol verwijderd uit de database. Statuscode: %d", response_delete.status_code)
    except Exception as e:
        logging.critical("Er is een fout opgetreden: %s", e)
        sys.exit(1)
post_external_data()