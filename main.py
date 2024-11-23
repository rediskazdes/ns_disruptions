import requests
from datetime import datetime
import pytz
from deep_translator import GoogleTranslator


def translate_text(text, target_lang='en'):
    """Translate text using deep_translator"""
    if not text:
        return text

    try:
        translator = GoogleTranslator(source='nl', target=target_lang)
        return translator.translate(text)
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails


def parse_ns_datetime(date_str):
    """Parse NS API datetime string which comes in format '2024-11-23T14:20:38+0100'"""
    try:
        return datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S%z')
    except ValueError:
        try:
            base_dt = datetime.strptime(date_str[:-5], '%Y-%m-%dT%H:%M:%S')
            offset_hours = int(date_str[-5:-2])
            offset_minutes = int(date_str[-2:])
            tz = pytz.FixedOffset(offset_hours * 60 + offset_minutes)
            return base_dt.replace(tzinfo=tz)
        except Exception as e:
            print(f"Warning: Could not parse date {date_str}: {e}")
            return None


def get_disruptions(station_code='DT'):
    """
    Fetch and parse disruptions affecting a specific station from NS API v3.
    """
    API_URL = f"https://gateway.apiportal.ns.nl/disruptions/v3/station/{station_code}"
    API_KEY = '224e253460f34fdcb3df8e0f26e5f434'

    headers = {
        'Ocp-Apim-Subscription-Key': API_KEY,
        'Accept': 'application/json'
    }

    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        disruptions = response.json()

        if not disruptions:
            print(f"\nNo current disruptions affecting {station_code}")
            return

        print(f"\nCurrent disruptions affecting {station_code}:")
        print("=" * 50)

        for disruption in disruptions:
            print(f"\nType: {disruption['type']}")
            print(f"Title: {translate_text(disruption['title'])}")

            # Print times
            if 'start' in disruption:
                start_time = parse_ns_datetime(disruption['start'])
                if start_time:
                    print(f"Start: {start_time.strftime('%Y-%m-%d %H:%M')}")

            if 'end' in disruption:
                end_time = parse_ns_datetime(disruption['end'])
                if end_time:
                    print(f"End: {end_time.strftime('%Y-%m-%d %H:%M')}")

            # Print phase if available
            if 'phase' in disruption and 'label' in disruption['phase']:
                print(f"Phase: {translate_text(disruption['phase']['label'])}")

            # Print situation and cause from timespans
            if 'timespans' in disruption and disruption['timespans']:
                timespan = disruption['timespans'][0]
                if 'situation' in timespan:
                    print(f"Situation: {translate_text(timespan['situation']['label'])}")

                if 'cause' in timespan:
                    print(f"Cause: {translate_text(timespan['cause']['label'])}")

                if 'additionalTravelTime' in timespan:
                    print(f"Travel Time Impact: {translate_text(timespan['additionalTravelTime']['label'])}")

                if 'advices' in timespan and timespan['advices']:
                    english_advices = [translate_text(advice) for advice in timespan['advices']]
                    print("Advice:", ", ".join(english_advices))

            # Print impact level if available
            if 'impact' in disruption and 'value' in disruption['impact']:
                print(f"Impact Level: {disruption['impact']['value']}/5")

            # Print expected duration if available
            if 'expectedDuration' in disruption and 'description' in disruption['expectedDuration']:
                print(f"Expected Duration: {translate_text(disruption['expectedDuration']['description'])}")

            print("-" * 50)

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving disruptions: {e}")
        if hasattr(e, 'response') and hasattr(e.response, 'text'):
            print("Response content:", e.response.text)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    get_disruptions('DT')  # DT is the station code for Delft