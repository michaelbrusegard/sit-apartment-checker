import requests
import json
import time
import logging
import os
from dotenv import load_dotenv
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

load_dotenv()

GRAPHQL_ENDPOINT = "https://as-portal-a-prod884f86a.azurewebsites.net/graphql"
INTERVAL_SECONDS = 30


TWILIO_ACCOUNT_SID = os.environ.get(
    "TWILIO_ACCOUNT_SID", "ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
)
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "your_auth_token_here")

TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "+15017122661")

MY_PHONE_NUMBER = os.environ.get("MY_PHONE_NUMBER", "+47xxxxxxxx")


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
PAYLOAD = {
    "operationName": "GetHousingIds",
    "variables": {
        "input": {
            "location": [{"parent": "Trondheim", "children": []}],
            "availableMaxDate": "2025-08-06T00:00:00.000Z",
            "showUnavailable": False,
            "residenceCategories": ["1-roms"],
            "offset": 0,
            "pageSize": 10,
            "includeFilterCounts": True,
        }
    },
    "query": "query GetHousingIds($input: GetHousingsInput!) { housings(filter: $input) { housingRentalObjects { rentalObjectId isAvailable availableFrom availableTo } totalCount } }",
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def test_sms_notification(twilio_client):
    test_message = "This is a test message from SiT Apartment Checker. If you receive this, your SMS notifications are working correctly!"
    success = send_sms(twilio_client, test_message)
    if success:
        logging.info("Test SMS sent successfully! Check your phone.")
        return True
    else:
        logging.error(
            "Failed to send test SMS. Please check your Twilio configuration."
        )
        return False


def send_sms(twilio_client, message_body):
    try:
        message = twilio_client.messages.create(
            body=message_body,
            from_=TWILIO_PHONE_NUMBER,
            to=MY_PHONE_NUMBER,
        )
        logging.info(f"SMS sent successfully! SID: {message.sid}")
        return True
    except TwilioRestException as e:
        logging.error(f"Error sending SMS: {e}")
        return False


def check_for_apartments(twilio_client, notified_ids):
    logging.info("Checking for new apartments...")
    try:
        response = requests.post(
            GRAPHQL_ENDPOINT, headers=HEADERS, json=PAYLOAD, timeout=15
        )
        response.raise_for_status()
        response_data = response.json()

        housings_data = response_data.get("data", {}).get("housings", {})
        apartments = housings_data.get("housingRentalObjects", [])
        total_count = housings_data.get("totalCount", 0)

        if total_count > 0 and apartments:
            new_apartments_found = False
            for apt in apartments:
                apt_id = apt.get("rentalObjectId")
                if apt_id not in notified_ids:
                    new_apartments_found = True
                    logging.info(f"!!! NEW APARTMENT FOUND: {apt_id}")
                    notified_ids.add(apt_id)
                    available_from = apt.get("availableFrom", "N/A")
                    message = f"New 1-room apartment available at Sit!\nID: {apt_id}\nFrom: {available_from}\nCheck now: https://bolig.sit.no/no/"
                    send_sms(twilio_client, message)
            if not new_apartments_found:
                logging.info("Apartments are available, but you've been notified.")
        else:
            logging.info("No available 1-room apartments found.")

    except requests.exceptions.RequestException as e:
        logging.error(f"Network error checking apartments: {e}")
    except (KeyError, TypeError, json.JSONDecodeError) as e:
        logging.error(f"Could not parse the response JSON. Error: {e}")


if __name__ == "__main__":
    if "ACxxxx" in TWILIO_ACCOUNT_SID or "your_auth_token" in TWILIO_AUTH_TOKEN:
        logging.error("Please fill in your Twilio Account SID and Auth Token.")
        exit()
    if "+47xxxxxxxx" in MY_PHONE_NUMBER:
        logging.error("Please fill in your personal phone number.")
        exit()

    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

    if not test_sms_notification(client):
        logging.error("Exiting due to SMS test failure")
        exit(1)

    notified_apartments = set()

    logging.info("Starting apartment checker script...")
    while True:
        try:
            check_for_apartments(client, notified_apartments)
            logging.info(f"Waiting for {INTERVAL_SECONDS} seconds...")
            time.sleep(INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logging.info("Script stopped by user.")
            break
        except Exception as e:
            logging.error(f"An unexpected error occurred in the main loop: {e}")
            time.sleep(INTERVAL_SECONDS)
