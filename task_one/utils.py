import requests
import datetime

# ------------------------------------------------------------------------------------
def fetch_weather_data(city: str, api_key: str) -> dict:

    """
        Fetches current weather data for a specified city using the OpenWeatherMap API.
        
        Args:
            city (str): Name of the city to fetch weather data for
            api_key (str): Valid API key for OpenWeatherMap API access
            
        Returns:
            dict: JSON response containing weather data if successful, None if any error occurs
            
        The function makes an HTTP GET request to OpenWeatherMap API with:
        - City name and API key as required parameters
        - Metric units for temperature
        - 10 second timeout to prevent hanging
        
        Handles common HTTP errors including:
        - Invalid API key or city name (HTTPError)
        - Network connectivity issues (ConnectionError) 
        - Request timeout after 10s (Timeout)
        - Other request failures (RequestException)
    """

    api_url = 'http://api.openweathermap.org/data/2.5/weather'
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'  # Use metric units for temperature
    }
    try:
        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()  # Raises HTTPError for bad responses (4xx, 5xx)
        return response.json()
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred for {city}: {http_err}')
    except requests.exceptions.ConnectionError as conn_err:
        print(f'Connection error occurred for {city}: {conn_err}')
    except requests.exceptions.Timeout as timeout_err:
        print(f'Timeout error occurred for {city}: {timeout_err}')
    except requests.exceptions.RequestException as req_err:
        print(f'An error occurred for {city}: {req_err}')
    return None

# ------------------------------------------------------------------------------------
def process_weather_data(data):

    """
        Processes the raw weather data from the OpenWeatherMap API into a structured format.
        
        Args:
            data (dict): Raw JSON response from OpenWeatherMap API containing weather data
                Expected format:
                {
                    'name': str,           # City name
                    'main': {
                        'temp': float,     # Temperature in Celsius
                        'humidity': int    # Humidity percentage
                    },
                    'weather': [{
                        'description': str # Weather description
                    }],
                    'wind': {
                        'speed': float     # Wind speed in m/s
                    }
                }
        
        Returns:
            dict: Processed weather data with standardized keys if successful:
                {
                    'city': str,           # City name
                    'temperature': float,   # Temperature in Celsius
                    'description': str,     # Weather description
                    'humidity': int,        # Humidity percentage 
                    'wind_speed': float     # Wind speed in m/s
                }
            None: If processing fails due to missing/invalid data
        
        The function uses .get() to safely handle missing fields and avoid KeyErrors.
        Weather description is extracted from first weather condition in list.
    """

    try:
        processed_data = {
            'city': data.get('name'),
            'temperature': data['main'].get('temp'),
            'description': data['weather'][0].get('description'),
            'humidity': data['main'].get('humidity'),
            'wind_speed': data['wind'].get('speed')
        }
        return processed_data
    except (KeyError, TypeError) as e:
        print(f"Data processing error: {e}")
        return None

# ------------------------------------------------------------------------------------
def insert_weather_data_bigquery(client, table_id, weather):

    """
        Inserts processed weather data into the specified BigQuery table.
        
        Args:
            client (google.cloud.bigquery.Client): Initialized BigQuery client instance
            table_id (str): Full path to target BigQuery table in format: 
                        "project.dataset.table_name"
            weather (dict): Processed weather data dictionary containing:
                - city (str): Name of the city
                - temperature (float): Temperature in Celsius
                - description (str): Weather description
                - humidity (int): Humidity percentage
                - wind_speed (float): Wind speed in m/s
        
        Returns:
            None
            
        Side Effects:
            - Inserts a new row into the specified BigQuery table
            - Prints success/error message to console
            
        The function:
        1. Constructs a row with weather data and current UTC timestamp
        2. Attempts to insert the row using BigQuery streaming insert
        3. Handles and reports any insertion errors
    """

    rows_to_insert = [
        {
            "city": weather["city"],
            "temperature": weather["temperature"], 
            "description": weather["description"],
            "humidity": weather["humidity"],
            "wind_speed": weather["wind_speed"],
            "timestamp": datetime.datetime.utcnow().isoformat()
        }
    ]

    errors = client.insert_rows_json(table_id, rows_to_insert)
    if errors:
        print(f"Encountered errors while inserting rows: {errors}")
    else:
        print(f"Data for {weather['city']} inserted successfully into BigQuery.")