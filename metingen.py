
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
                insertMetingUren = f"INSERT INTO metinguren(metingenId,datetime,temperature,pressure,winddirection) VALUES ('{metingId}', '{i['datetime']}', {i['temp']}, {i['pressure']}, '{i['winddir']}')"
                cursor.execute(insertMetingUren)
                connection.commit()
    else:
        print("Unexpected Status code: ", response.status_code)
        sys.exit()

def getWeerData(locatie):
    API_temp = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{locatie}/next7days?unitGroup=metric&elements=datetime%2Ctemp%2Cwinddir%2Cpressure&include=hours%2Ccurrent&key=ZW8NCV6JP8ZUGX33D769DJ693&contentType=json"
    response = requests.request("GET", API_temp)
    if response.status_code == 200:
        jsonData = response.json()
        address = jsonData["address"]
        firstTime = True
        connection = DB.connect_to_database()
        cursor = connection.cursor()
        insertQuery = f"INSERT INTO metingen (locatieId, datetime) VALUES ((SELECT locatieId FROM locaties WHERE locatie = '{address}'), '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
        cursor.execute(insertQuery)
        connection.commit()
        metingId = cursor.lastrowid
        for day in jsonData["days"]:
            date_day = datetime.strptime(day["datetime"], "%Y-%m-%d").date()
            if firstTime == True:
                firstTime = False
                for currentCondition_data, value in jsonData["currentConditions"].items():
                    match currentCondition_data:
                        case "datetime":
                            currentCondition_time = datetime.combine(date_day, datetime.strptime(value, "%H:%M:%S").time())
                        case "temp":
                            currentCondition_temp = value
                        case "winddir":
                            currentCondition_winddir = value
                        case "pressure":
                            currentCondition_pressure = value
                            print(f"Current: {currentCondition_time} values: temp: {currentCondition_temp}, winddir: {currentCondition_winddir}, pressure: {currentCondition_pressure}")
                            insertQuery = f"INSERT INTO metinguren (metingenId, datetime, temperature, pressure, winddirection) VALUES ('{metingId}', '{currentCondition_time}', {currentCondition_temp}, {currentCondition_pressure}, '{currentCondition_winddir}')"
                            cursor.execute(insertQuery)
                            connection.commit()
            for day_data, value in day.items():
                match day_data:
                    case "temp":
                        day_temp = value
                    case "winddir":
                        day_winddir = value
                    case "pressure":
                        day_pressure = value
                    case "hours":
                        hoursLst = value
                        for hour in hoursLst:
                            for hour_data, value in hour.items():
                                match hour_data:
                                    case "datetime":
                                        dt = datetime.combine(date_day, datetime.strptime(hour["datetime"], "%H:%M:%S").time())
                                        if dt <= currentCondition_time:
                                            break
                                    case "temp":
                                        hour_temp = value
                                    case "winddir":
                                        hour_winddir = value
                                    case "pressure":
                                        hour_pressure = value
                                        print(
                                            f"{dt} values: temp: {hour_temp}, winddir: {hour_winddir}, pressure: {hour_pressure}"
                                        )
                                        insertQuery = f"INSERT INTO metinguren (metingenId, datetime, temperature, pressure, winddirection) VALUES ('{metingId}', '{dt}', {hour_temp}, {hour_pressure}, '{hour_winddir}')"
                                        cursor.execute(insertQuery)
                                        connection.commit()
        connection.close()
    else:
        print("Unexpected Status code: ", response.status_code)
        sys.exit()
getWeerData(locatie)