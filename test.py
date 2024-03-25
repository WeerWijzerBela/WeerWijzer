import logging
import requests
import sys
from datetime import datetime, date, timedelta

def post_weer_data(locatie):
    APIEXT = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locatie}/next7days?unitGroup=metric&elements=datetime%2Ctemp%2Cwinddir%2Cpressure&include=hours%2Ccurrent&key=ZW8NCV6JP8ZUGX33D769DJ693&contentType=json"
    API = "http://localhost:8000"

    try:
        response = requests.get(APIEXT)
        response.raise_for_status()  # Raises HTTPError if response status is not 200
        jsonData = response.json()

        nieuwe_metinguren = [{
            "datetime": str(date.today()) + ' ' + jsonData['currentConditions']['datetime'],
            "temperature": jsonData['currentConditions']['temp'],
            "pressure": jsonData['currentConditions']['pressure'],
            "winddirection": jsonData['currentConditions']['winddir']
        }]

        for data in jsonData["days"]:
            for i in data['hours']:
                i_datetime = f"{data['datetime']} {i['datetime']}"
                current_datetime = datetime.strptime(str(date.today()) + ' ' + jsonData['currentConditions']['datetime'], '%Y-%m-%d %H:%M:%S')
                if (i_datetime < current_datetime.replace(minute=0, second=0, microsecond=0) - timedelta(hours=3)) and (i_datetime <= str(date.today()) + ' ' + jsonData['currentConditions']['datetime']):
                    continue
                nieuwe_metinguren.append({
                    "datetime": i_datetime,
                    "temperature": i['temp'],
                    "pressure": i['pressure'],
                    "winddirection": i['winddir']
                })

        url_metinguren = API + '/metinguren'
        batch_size = 190

        for i in range(0, len(nieuwe_metinguren), batch_size):
            batch_data = nieuwe_metinguren[i:i + batch_size]
            response_batch = requests.post(url_metinguren, json=batch_data)
            response_batch.raise_for_status()

        url_metingen = API + '/metingen'
        response_delete = requests.delete(url_metingen)
        response_delete.raise_for_status()

        #bereken_voorspellingen(locatie)

    except Exception as e:
        logging.critical("Er is een fout opgetreden: %s", e)
        sys.exit(1)
