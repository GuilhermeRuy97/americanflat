# Imports
import requests
import os
import datetime
from dotenv        import load_dotenv
from google.cloud  import bigquery
from google.oauth2 import service_account
from utils         import fetch_weather_data, process_weather_data, insert_weather_data_bigquery

# Load environment variables from .env file
load_dotenv()

OWM_API_KEY = os.getenv('OWM_API_KEY')
cities = ['London', 'New York', 'Tokyo', 'Paris', 'Sydney', 'São Paulo', 'Rio de Janeiro']

def main():
    if not OWM_API_KEY:
        print("API key not found. Please check your .env file.")
        return

    # Load service account credentials
    credentials_path = "./serviceaccount.json"
    credentials = service_account.Credentials.from_service_account_file(credentials_path)

    # Initialize the BigQuery client
    client = bigquery.Client(credentials=credentials, project=credentials.project_id)
    table_id = "vital-wavelet-443820-j2.americanflat_weather.weather_data"

    for city in cities:
        data = fetch_weather_data(city, OWM_API_KEY)
        if data:
            weather = process_weather_data(data)
            if weather:
                insert_weather_data_bigquery(client, table_id, weather)
            else:
                print(f"Failed to process data for {city}.")
        else:
            print(f"Failed to retrieve data for {city}.")

if __name__ == '__main__':
    main()
