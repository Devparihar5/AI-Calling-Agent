from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

# Verify environment variables are loaded
print("Environment variables loaded:")
print(f"TWILIO_ACCOUNT_SID: {'*' * 5 + os.environ.get('TWILIO_ACCOUNT_SID', '')[-5:] if os.environ.get('TWILIO_ACCOUNT_SID') else 'Not found'}")
print(f"OPENAI_API_KEY: {'*' * 5 + os.environ.get('OPENAI_API_KEY', '')[-5:] if os.environ.get('OPENAI_API_KEY') else 'Not found'}")
print(f"MONGO_URI: {'*' * 5 + os.environ.get('MONGO_URI', '')[-5:] if os.environ.get('MONGO_URI') else 'Not found'}")
print(f"BASE_URL: {os.environ.get('BASE_URL', 'Not found')}")

app = Flask(__name__)

# Import database after app initialization to avoid circular imports
from database import Database
db = Database()

# Initialize Twilio client
twilio_client = Client(
    os.environ.get('TWILIO_ACCOUNT_SID'),
    os.environ.get('TWILIO_AUTH_TOKEN')
)

@app.route("/outbound-call", methods=['POST'])
def outbound_call():
    """Handle outbound call initiation"""
    phone_number = request.form.get('phone_number')
    customer_id = request.form.get('customer_id', None)
    
    if not phone_number:
        return {"status": "error", "message": "Phone number is required"}, 400
    
    # Get the base URL from environment variables
    base_url = os.environ.get('BASE_URL')
    if not base_url:
        return {"status": "error", "message": "BASE_URL environment variable not set"}, 500
    
    # check the  the url is correct or not by calling     
    
    # Start the outbound call using Twilio
    try:
        call = twilio_client.calls.create(
            url=f"{base_url}/handle-call",
            to=phone_number,
            from_=os.environ.get('TWILIO_PHONE_NUMBER'),
            status_callback=f"{base_url}/call-status",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        # Store call information in database
        db.calls.update_one(
            {'call_sid': call.sid},
            {
                '$set': {
                    'customer_id': customer_id,
                    'phone_number': phone_number,
                    'status': 'initiated',
                    'created_at': datetime.now().timestamp()
                }
            },
            upsert=True
        )
        
        return {"status": "success", "call_sid": call.sid}
    
    except Exception as e:
        print(f"Error making outbound call: {e}")
        return {"status": "error", "message": str(e)}, 500

@app.route("/call-status", methods=['POST'])
def call_status():
    """Handle call status callbacks from Twilio"""
    call_sid = request.form.get('CallSid')
    call_status = request.form.get('CallStatus')
    
    print(f"Call status update: {call_sid} - {call_status}")
    
    # Update call status in database
    db.update_call_status(call_sid, call_status)
    
    return Response(status=200)

@app.route("/handle-call", methods=['POST'])
def handle_call():
    """Handle the actual call conversation"""
    call_sid = request.form.get('CallSid')
    customer_input = request.form.get('SpeechResult', '')
    
    print(f"Handling call: {call_sid}")
    print(f"Customer input: {customer_input}")
    
    # Create TwiML response
    response = VoiceResponse()
    
    # If this is the first interaction (no customer input yet)
    if not customer_input:
        # Initial greeting
        greeting = "Hello! This is Call Worklog AI. I'm calling to introduce you to our product that automatically generates work logs based on your activities. Would you be interested in learning more about how it can save you time?"
        response.say(greeting)
        
        # Listen for customer response
        gather = response.gather(
            input='speech',
            action='/handle-call',
            method='POST',
            speechTimeout='auto',
            timeout=5
        )
    else:
        # Process customer input using OpenAI
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        # Get conversation context
        call_data = db.get_call_data(call_sid)
        conversation_history = call_data.get('conversation_history', [])
        
        # Add customer input to history
        conversation_history.append({"role": "user", "content": customer_input})
        
        # Generate AI response
        chat_completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an AI sales agent for Call Worklog AI, a tool that automatically generates work logs based on user activities. Your goal is to introduce the product, explain its benefits, answer any questions, and try to make a sale. Be friendly, professional, and concise. Don't be pushy but guide the conversation towards a sale."},
                *conversation_history
            ],
            max_tokens=150
        )
        
        ai_response = chat_completion.choices[0].message.content
        
        # Add AI response to history
        conversation_history.append({"role": "assistant", "content": ai_response})
        
        # Update conversation history in database
        db.update_conversation_history(call_sid, conversation_history)
        
        # Check if we should end the call
        should_end = "goodbye" in ai_response.lower() or "thank you for your time" in ai_response.lower()
        
        # Speak the AI response
        response.say(ai_response)
        
        if should_end:
            # End the call
            response.hangup()
        else:
            # Continue listening for customer input
            gather = response.gather(
                input='speech',
                action='/handle-call',
                method='POST',
                speechTimeout='auto',
                timeout=5
            )
    
    return Response(str(response), mimetype='text/xml')

@app.route("/initiate-calls", methods=['POST'])
def initiate_calls():
    """Initiate calls to a batch of customers"""
    customers = db.get_customers_to_call()
    
    calls_initiated = 0
    for customer in customers:
        try:
            # Make outbound call
            call = twilio_client.calls.create(
                url=f"{os.environ.get('BASE_URL')}/handle-call",
                to=customer['phone_number'],
                from_=os.environ.get('TWILIO_PHONE_NUMBER'),
                status_callback=f"{os.environ.get('BASE_URL')}/call-status",
                status_callback_event=['initiated', 'ringing', 'answered', 'completed']
            )
            
            calls_initiated += 1
            
            # Store call information in database
            db.calls.update_one(
                {'call_sid': call.sid},
                {
                    '$set': {
                        'customer_id': customer['_id'],
                        'phone_number': customer['phone_number'],
                        'status': 'initiated',
                        'created_at': datetime.now().timestamp()
                    }
                },
                upsert=True
            )
        except Exception as e:
            print(f"Error initiating call to {customer['phone_number']}: {e}")
    
    return {"status": "success", "calls_initiated": calls_initiated}

@app.route("/", methods=['GET'])
def index():
    """Simple index route to verify the server is running"""
    return "AI Calling Agent is running!"

if __name__ == "__main__":
    # Run the Flask app
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
