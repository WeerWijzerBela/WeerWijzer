from fastapi import FastAPI, HTTPException, Depends
from fastapi.requests import Request
from fastapi.responses import JSONResponse
import requests
import sys
import json
from datetime import datetime
from dotenv import load_dotenv
import os
import DB

load_dotenv()

app = FastAPI()

response = requests.request("GET", os.getenv("API_KEY"))
if response.status_code != 200:
    print("Unexpected Status code: ", response.status_code)
    sys.exit()

# Parse the results as JSON
jsonData = response.json()

# print(jsonData)
# Assigning unique variables to all the attributes of jsonData
address = jsonData["address"]
# datetime = jsonData["datetime"]
# temp = jsonData["temp"]
# humidity = jsonData["humidity"]
# winddir = jsonData["winddir"]
# pressure = jsonData["pressure"]
# hours = jsonData["hours"]
# days = jsonData["days"]
# current = jsonData["current"]

for day in jsonData["days"]:
    date = datetime.strptime(day["datetime"], "%Y-%m-%d").date()
    for day_data, value in day.items():
        match day_data:
            case "temp":
                temp = value
            case "humidity":
                humidity = value
            case "winddir":
                winddir = value
            case "pressure":
                pressure = value
            case "hours":
                print(
                    f"{date} values: temp: {temp}, humidity: {humidity}, winddir: {winddir}, pressure: {pressure}"
                )
                # HIER VERDER UITBREIDEN NA CASE "HOURS" OM DE HOUR VALUE (i.e. 00:00) te bekijken, om te zetten naar day_hour en daar gegevens van ophalen

