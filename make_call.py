from dotenv import load_dotenv
import os
from twilio.rest import Client
import sys
from pathlib import Path

env_path = Path(__file__).parent / "src" / ".env"
load_dotenv(dotenv_path=env_path)

def make_outbound_call():
    """Make an outbound call using Twilio directly"""
    # Check if required environment variables are set
    twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
    twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
    twilio_phone_number = os.environ.get('TWILIO_PHONE_NUMBER')
    personal_phone = os.environ.get('PERSONAL_PHONE')
    base_url = os.environ.get('BASE_URL')
    if not all([twilio_account_sid, twilio_auth_token, twilio_phone_number, personal_phone, base_url]):
        print("Error: Missing required environment variables")
        print(f"TWILIO_ACCOUNT_SID: {'Set' if twilio_account_sid else 'Missing'}")
        print(f"TWILIO_AUTH_TOKEN: {'Set' if twilio_auth_token else 'Missing'}")
        print(f"TWILIO_PHONE_NUMBER: {twilio_phone_number or 'Missing'}")
        print(f"PERSONAL_PHONE: {personal_phone or 'Missing'}")
        print(f"BASE_URL: {base_url or 'Missing'}")
        return
    
    print(f"Making outbound call from {twilio_phone_number} to {personal_phone}")
    print(f"Using webhook URL: {base_url}/handle-call")
    
    # Initialize Twilio client
    client = Client(twilio_account_sid, twilio_auth_token)
    
    try:
        # Make the call
        call = client.calls.create(
            url=f"{base_url}/handle-call",
            to=personal_phone,
            from_=twilio_phone_number,
            status_callback=f"{base_url}/call-status",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        print(f"Call initiated with SID: {call.sid}")
        print(f"Call status: {call.status}")
        
        # Wait for user input to exit
        input("Press Enter to exit...")
        
    except Exception as e:
        print(f"Error making call: {e}")

if __name__ == "__main__":
    make_outbound_call()
