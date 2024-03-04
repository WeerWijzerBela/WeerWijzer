#file for external api data
import requests

API_URL = "https://weerlive.nl/api/json-data-10min.php?key=da59fac1e0&locatie=Amsterdam"

def getData(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
    
        else:   
            print("Failed to get data")
            return response.status_code
    except Exception:
        print("an error occured")
        return None
    
def postData():
    data = getData(API_URL)
    
    if data:
        for i in data["liveweer"]:
            print(i)
    
    else:
        print("failed to receive data")

postData()