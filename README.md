# Sit Apartment Checker

This is a very simple  script for checking the SIT API for available of 1 room apartments in Trondheim. It can be easily modified to check for other types of apartments by modifying the GraphQL request. It uses Twilio for sending SMS notifications when a new apartment is available to your phone number.

## Prerequisites

- Python 3.11 or higher
- uv (Python package installer)
- Twilio account (for SMS notifications)

## Installation

1. Install uv (if not already installed):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone this repository:

```bash
git clone https://github.com/yourusername/sit-apartment-checker.git
cd sit-apartment-checker
```

3. Create and activate a virtual environment with uv:

```bash
uv venv
source .venv/bin/activate  # On Unix/macOS
# or
.venv\Scripts\activate  # On Windows
```

4. Install dependencies:

```bash
uv sync
```

## Configuration

1. Sign up for a [Twilio account](https://www.twilio.com/) if you don't have one

2. Copy the example environment file:

```bash
cp .env.example .env
```

3. Edit `.env` with your settings:

```
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
MY_PHONE_NUMBER=your_personal_phone_number
```

- `TWILIO_ACCOUNT_SID`: Your Twilio Account SID
- `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token
- `TWILIO_PHONE_NUMBER`: Your Twilio phone number (format: +1234567890)
- `MY_PHONE_NUMBER`: Your personal phone number to receive SMS (format: +1234567890)

## Usage

Run the script:

```bash
python main.py
```

The script will:

1. Test the SMS notification setup
2. Start checking for available apartments every 30 seconds
3. Send you an SMS when new apartments become available

## Customization

To check for different types of apartments, modify the `PAYLOAD` variable in `main.py`. The current setup checks for 1-room apartments (`"residenceCategories": ["1-roms"]`).

## Notes

- The script uses Twilio's free tier, which has limitations. Check Twilio's pricing for more details.
- Make sure your phone number is in the international format (+XXX).
- The script will exit if the Twilio credentials are invalid or if the test SMS fails.
