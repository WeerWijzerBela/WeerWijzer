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
address = jsonData["address"]

for day in jsonData["days"]:
    date_day = datetime.strptime(day["datetime"], "%Y-%m-%d").date()
    for day_data, value in day.items():
        match day_data:
            case "temp":
                day_temp = value
            case "humidity":
                day_humidity = value
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
                                date_hour = datetime.strptime(hour["datetime"], "%H:%M:%S").time()
                                date_day_hour = datetime.combine(date_day, date_hour)
                            case "temp":
                                hour_temp = value
                            case "humidity":
                                hour_humidity = value
                            case "winddir":
                                hour_winddir = value
                            case "pressure":
                                hour_pressure = value
                                print(
                                    f"{date_day_hour} values: temp: {hour_temp}, humidity: {hour_humidity}, winddir: {hour_winddir}, pressure: {hour_pressure}"
                                )

