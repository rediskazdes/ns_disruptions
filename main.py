import requests
import json

# NS API endpoint for disruptions (you may need an actual API key or a specific URL)
API_URL = "https://api.ns.nl/reisinformatie/v3/disruptions"  # This URL is an example; you may need to adjust it.
API_KEY = 'your_api_key_here'  # Replace this with your actual API key if needed

# Parameters to filter for Delft station disruptions
params = {
    'station': 'Delft'
}

headers = {
    'Authorization': f'Bearer {API_KEY}',  # Include the Authorization header if required by the API
    'Accept': 'application/json'
}


def get_disruptions():
    try:
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()  # Check if the request was successful
        disruptions = response.json()

        if 'disruptions' in disruptions:
            print("Current disruptions at Delft station:")
            for disruption in disruptions['disruptions']:
                print(f"Disruption: {disruption['title']}")
                print(f"Details: {disruption['description']}")
                print(f"Start Time: {disruption['startTime']}")
                print(f"End Time: {disruption['endTime']}")
                print('---' * 10)
        else:
            print("No disruptions reported at Delft station.")
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving disruptions: {e}")


if __name__ == "__main__":
    get_disruptions()
