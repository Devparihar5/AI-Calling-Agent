# AI Calling Agent for Call Worklog AI

An automated calling solution that uses AI to make sales calls for Call Worklog AI product, assist with customer queries, and update customer information in a database.

## Overview

This AI Calling Agent makes outbound calls to potential customers to sell "Call Worklog AI" - a tool that automatically generates work logs based on actual work performed. The agent can also handle customer queries and record call outcomes in a database for follow-up and analysis.

## Features

- **AI-Powered Sales Calls:** Uses OpenAI to generate natural, persuasive sales conversations
- **Outbound Call Automation:** Leverages Twilio for making automated outbound calls
- **Customer Query Resolution:** Answers questions about the Call Worklog AI product
- **Call Recording & Analysis:** Records call outcomes and customer responses
- **Database Integration:** Updates customer information in MongoDB after each call

## Project Structure

```

├── make_call.py          # Script for making a single outbound call
├── requirements.txt      # Project dependencies
└── src/
    ├── .env              # Environment variables (create from .env.example)
    ├── .env.example      # Example environment variables
    ├── agent.py          # AI agent logic using OpenAI
    ├── app.py            # Main Flask application with Twilio webhook handlers
    ├── database.py       # MongoDB database operations
    └── tts_service.py    # Text-to-speech service using Edge TTS
```

## Technology Stack

- **Twilio:** For handling outbound calls
- **OpenAI:** For generating natural conversation and understanding customer responses
- **MongoDB:** For storing customer information and call outcomes
- **Text-to-Speech (TTS):** For converting AI responses to voice using Edge TTS
- **Speech-to-Text (STT):** For converting customer speech to text (handled by Twilio)
- **Flask:** Web framework for handling Twilio webhooks

## Setup Instructions

### 1. Clone and Install

1. Clone this repository
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment:
   - Windows: `.venv\Scripts\activate`
   - Linux/Mac: `source .venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`

### 2. Twilio Setup

1. Create a Twilio account at [twilio.com](https://www.twilio.com/try-twilio)
2. Once registered, navigate to your [Twilio Console Dashboard](https://www.twilio.com/console)
3. Find your Account SID and Auth Token (you'll need these for the .env file)
4. Purchase a Twilio phone number:
   - Go to Phone Numbers > Buy a Number
   - Search for a number with voice capabilities
   - Complete the purchase
5. Note down your new Twilio phone number (with country code, e.g., +1234567890)

### 3. Environment Configuration

1. Copy `.env.example` to `.env` in the src directory:
   ```
   cp src/.env.example src/.env
   ```
2. Edit the `.env` file and fill in your credentials:
   - `TWILIO_ACCOUNT_SID`: Your Twilio Account SID from the console
   - `TWILIO_AUTH_TOKEN`: Your Twilio Auth Token from the console
   - `TWILIO_PHONE_NUMBER`: Your purchased Twilio phone number
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `MONGO_URI`: MongoDB connection string (local or Atlas)
   - `BASE_URL`: Your ngrok URL (see ngrok setup below)

### 4. MongoDB Setup

1. Install MongoDB locally or create a free MongoDB Atlas account
2. If using MongoDB Atlas:
   - Create a new cluster
   - Set up database access (username/password)
   - Set up network access (IP whitelist)
   - Get your connection string and add it to the .env file

### 5. Ngrok Setup for Local Testing

Twilio needs a public URL to send webhooks to your local application. Ngrok creates a secure tunnel to your local server.

1. Download and install [ngrok](https://ngrok.com/download)
2. Sign up for a free ngrok account and get your authtoken
3. Authenticate ngrok with your token:
   ```
   ngrok authtoken YOUR_AUTH_TOKEN
   ```
4. Start ngrok to create a tunnel to your Flask application:
   ```
   ngrok http 5000
   ```
5. Copy the https URL provided by ngrok (e.g., https://a1b2c3d4.ngrok.io)
6. Update your `.env` file with this URL as the `BASE_URL`

## Running the Application

### Start the Flask Application

From the project root directory:

```bash
cd src
flask run
```

The Flask server will start on port 5000 (or the port specified in your .env file).

### Making a Test Call

Use the provided script to make a test call:

```bash
python make_call.py
```

This will initiate a call from your Twilio number to the phone number specified in the PERSONAL_PHONE environment variable.

## API Endpoints

- **POST /handle-call**: Webhook endpoint for Twilio to handle incoming call events
- **POST /call-status**: Webhook endpoint for Twilio to report call status updates
- **POST /outbound-call**: Endpoint to initiate a single outbound call
- **POST /initiate-calls**: Endpoint to initiate calls to all customers in the database

## Troubleshooting

1. **Webhook Errors**: Ensure your ngrok URL is correct in the .env file and Twilio can reach it
2. **Twilio Errors**: Check your Twilio console for error messages and logs
3. **Audio Issues**: Verify TTS settings and that audio files are being generated correctly
4. **Database Connection**: Ensure MongoDB is running and the connection string is correct

## Development Notes

- The AI agent uses OpenAI's API to generate responses based on conversation context
- Call recordings and transcripts are stored in MongoDB for analysis
- The TTS service converts AI responses to audio using Edge TTS
- Twilio handles the actual phone calls and audio streaming

## License

[MIT License](LICENSE)
