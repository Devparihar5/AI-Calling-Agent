# Detailed Setup Guide for AI Calling Agent

This guide provides step-by-step instructions for setting up the AI Calling Agent, with particular focus on Twilio configuration and local testing with ngrok.

## Twilio Setup (Detailed)

### 1. Create a Twilio Account

1. Go to [twilio.com/try-twilio](https://www.twilio.com/try-twilio)
2. Sign up with your email, name, and password
3. Verify your email address and phone number
4. Complete the account verification process (may require a credit card)

### 2. Navigate to Twilio Console

1. After logging in, you'll be taken to the [Twilio Console Dashboard](https://www.twilio.com/console)
2. This is where you'll find your Account SID and Auth Token

### 3. Locate Your Account SID and Auth Token

1. On the Twilio Console Dashboard, look for the "Account Info" section
2. Your Account SID is displayed prominently (it starts with "AC")
3. Your Auth Token is initially hidden - click on "Show" to reveal it
4. Copy both values - you'll need them for your `.env` file

### 4. Purchase a Twilio Phone Number

1. In the left sidebar, navigate to "Phone Numbers" > "Manage" > "Buy a Number"
2. Use the search filters to find a number with voice capabilities:
   - Select your country
   - Check the "Voice" capability box
   - Click "Search"
3. Choose a number from the results and click "Buy"
4. Complete the purchase process
5. Your new number will appear in the "Active Numbers" section
6. Copy this number (with country code, e.g., +1234567890) for your `.env` file

### 5. Configure Voice Settings (Optional)

1. Go to "Phone Numbers" > "Manage" > "Active Numbers"
2. Click on your newly purchased number
3. Scroll down to the "Voice & Fax" section
4. For "A Call Comes In", select "Webhook" and enter your ngrok URL + "/handle-call" (e.g., https://a1b2c3d4.ngrok.io/handle-call)
5. For "Call Status Changes", enter your ngrok URL + "/call-status"
6. Click "Save"

## Ngrok Setup for Local Testing (Detailed)

### 1. Download and Install Ngrok

1. Go to [ngrok.com/download](https://ngrok.com/download)
2. Download the appropriate version for your operating system
3. Extract the downloaded file to a location of your choice

### 2. Create an Ngrok Account

1. Go to [dashboard.ngrok.com/signup](https://dashboard.ngrok.com/signup)
2. Sign up for a free account
3. Verify your email address

### 3. Get Your Authtoken

1. Log in to your ngrok dashboard
2. Navigate to the "Getting Started" section or "Your Authtoken" section
3. Copy your authtoken

### 4. Authenticate Ngrok

1. Open a terminal or command prompt
2. Navigate to the directory where you extracted ngrok
3. Run the following command:
   ```
   ./ngrok authtoken YOUR_AUTH_TOKEN
   ```
   Replace `YOUR_AUTH_TOKEN` with the token you copied

### 5. Start Ngrok

1. Make sure your Flask application is running on port 5000
2. In a new terminal window, run:
   ```
   ./ngrok http 5000
   ```
3. Ngrok will display a screen with information about your tunnel
4. Look for the "Forwarding" line that shows your public URL (e.g., https://a1b2c3d4.ngrok.io)
5. Copy this URL - this is your `BASE_URL` for the `.env` file

### 6. Update Your .env File

1. Open your `.env` file in the src directory
2. Set the `BASE_URL` to your ngrok URL:
   ```
   BASE_URL = "https://a1b2c3d4.ngrok.io"
   ```
3. Save the file

## Testing Your Setup

### 1. Verify Environment Variables

Ensure all required environment variables are set in your `.env` file:

```
# Twilio credentials
TWILIO_ACCOUNT_SID = "your_twilio_account_sid"
TWILIO_AUTH_TOKEN = "your_twilio_auth_token"
TWILIO_PHONE_NUMBER = "+1234567890"

# OpenAI API key
OPENAI_API_KEY = "your_openai_api_key"

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"

# Base URL for your application
BASE_URL = "https://your-ngrok-url.ngrok.io"

# Your personal phone for testing
PERSONAL_PHONE = "+1987654321"
```

### 2. Start Your Flask Application

1. Activate your virtual environment
2. Navigate to the src directory
3. Run:
   ```
   flask run
   ```

### 3. Make a Test Call

1. Open a new terminal window
2. Navigate to your project root directory
3. Run:
   ```
   python make_call.py
   ```
4. You should receive a call on your personal phone number
5. The terminal will display information about the call status

### 4. Troubleshooting

If the call doesn't work:

1. Check the terminal output for error messages
2. Verify that all environment variables are set correctly
3. Ensure your ngrok tunnel is active and the URL is correct
4. Check the Twilio console for any error messages or logs
5. Verify that your personal phone number is in the correct format (with country code)

## Additional Resources

- [Twilio Documentation](https://www.twilio.com/docs/voice)
- [Ngrok Documentation](https://ngrok.com/docs)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs/api-reference)
