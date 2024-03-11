
import requests
import sys
from datetime import datetime,date
import DB

locatie = "Apeldoorn"
API_temp = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locatie}/next7days?unitGroup=metric&elements=datetime%2Ctemp%2Cwinddir%2Cpressure&include=hours%2Ccurrent&key=ZW8NCV6JP8ZUGX33D769DJ693&contentType=json"
def post_external_data():
    """
    posts data from an external API.
    """
    response = requests.request("GET", API_temp)
    if response.status_code == 200:
        jsonData = response.json()
        connection = DB.connect_to_database()
        cursor = connection.cursor()
        insertMetingen = f"INSERT INTO metingen (locatieId, datetime) VALUES ((SELECT locatieId FROM locaties WHERE locatie = '{locatie}'), '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
        cursor.execute(insertMetingen)
        connection.commit()
        metingId = cursor.lastrowid
        insertQuery = f"INSERT INTO metinguren (metingenId,datetime,temperature,pressure,winddirection)VALUES ('{metingId}', '{str(date.today())  + ' ' + jsonData['currentConditions']['datetime']}', '{jsonData['currentConditions']['temp']}', '{jsonData['currentConditions']['pressure']}', '{jsonData['currentConditions']['winddir']}')"
        cursor.execute(insertQuery)
        connection.commit()

        for data in jsonData["days"]:
            for i in data['hours']:
                i['datetime'] = data['datetime'] + ' ' + i['datetime']
                if i['datetime'] < str(date.today())  + ' ' + jsonData['currentConditions']['datetime']:
                    continue
                else:
                    insertMetingUren = f"INSERT INTO metinguren(metingenId,datetime,temperature,pressure,winddirection) VALUES ('{metingId}', '{i['datetime']}', {i['temp']}, {i['pressure']}, '{i['winddir']}')"
                    cursor.execute(insertMetingUren)
                    connection.commit()
    else:
        print("Unexpected Status code: ", response.status_code)
        sys.exit()
        
post_external_data()