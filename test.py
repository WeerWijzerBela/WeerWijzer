import requests
import logfiles

logfiles.basicConfig(level=logfiles.DEBUG)

def get_data():
    try:
        response = requests.get('http://example.com')
        response.raise_for_status()
        logfiles.info('Data opgehaald: %s', response.text)
    except requests.exceptions.HTTPError as http_err:
        logfiles.error('HTTP-fout opgetreden: %s', http_err)
    except requests.exceptions.ConnectionError as conn_err:
        logfiles.error('Verbindingsfout opgetreden: %s', conn_err)
    except requests.exceptions.Timeout as timeout_err:
        logfiles.error('Time-out opgetreden: %s', timeout_err)
    except requests.exceptions.RequestException as req_err:
        logfiles.error('Er is een fout opgetreden bij het verwerken van het verzoek: %s', req_err)

get_data()
