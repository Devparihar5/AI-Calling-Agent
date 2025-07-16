import os
from twilio.rest import Client
import openai
from tts_service import TextToSpeech
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AIAgent:
    def __init__(self):
        # Initialize Twilio client
        twilio_account_sid = os.environ.get('TWILIO_ACCOUNT_SID')
        twilio_auth_token = os.environ.get('TWILIO_AUTH_TOKEN')
        
        if not twilio_account_sid or not twilio_auth_token:
            print("Warning: Twilio credentials not found in environment variables")
            
        self.twilio_client = Client(twilio_account_sid, twilio_auth_token)
        
        # Initialize OpenAI client
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            print("Warning: OpenAI API key not found in environment variables")
        
        openai.api_key = openai_api_key
        
        # Initialize TTS service
        self.tts = TextToSpeech()
        
        # Store conversation history for each call
        self.conversations = {}
        
        # Product information for the AI to use
        self.product_info = {
            "name": "Call Worklog AI",
            "description": "An AI tool that automatically generates work logs based on your activities",
            "benefits": [
                "Save time by automating work log creation",
                "Ensure accurate documentation of work activities",
                "Improve productivity by focusing on work instead of reporting",
                "Easy integration with existing workflow systems"
            ],
            "pricing": {
                "basic": "$9.99/month",
                "pro": "$19.99/month",
                "enterprise": "Custom pricing"
            }
        }
    
    def start_outbound_call(self, phone_number, customer_id=None):
        """Start an outbound call to a customer"""
        call = self.twilio_client.calls.create(
            url=f"{os.environ.get('BASE_URL')}/handle-call",
            to=phone_number,
            from_=os.environ.get('TWILIO_PHONE_NUMBER'),
            status_callback=f"{os.environ.get('BASE_URL')}/call-status",
            status_callback_event=['initiated', 'ringing', 'answered', 'completed']
        )
        
        # Initialize conversation history for this call
        self.conversations[call.sid] = {
            "customer_id": customer_id,
            "phone_number": phone_number,
            "history": [],
            "customer_responses": {},
            "call_outcome": None,
            "should_end": False
        }
        
        return call.sid
    
    def process_customer_input(self, call_sid, customer_input):
        """Process customer input and generate AI response"""
        if call_sid not in self.conversations:
            # Initialize if this is a new call
            self.conversations[call_sid] = {
                "history": [],
                "customer_responses": {},
                "call_outcome": None,
                "should_end": False
            }
        
        conversation = self.conversations[call_sid]
        
        # Add customer input to history
        if customer_input:
            conversation["history"].append({"role": "user", "content": customer_input})
            
            # Extract key information from customer input
            self._update_customer_responses(call_sid, customer_input)
        
        # Generate AI response
        ai_response = self._generate_ai_response(call_sid)
        
        # Add AI response to history
        conversation["history"].append({"role": "assistant", "content": ai_response})
        
        return ai_response
    
    def _generate_ai_response(self, call_sid):
        """Generate AI response using OpenAI"""
        conversation = self.conversations[call_sid]
        
        # Create system message with instructions
        system_message = {
            "role": "system", 
            "content": f"""You are an AI sales agent for Call Worklog AI, a tool that automatically generates work logs based on user activities.
            Your goal is to introduce the product, explain its benefits, answer any questions, and try to make a sale.
            Be friendly, professional, and concise. Don't be pushy but guide the conversation towards a sale.
            Product information: {json.dumps(self.product_info)}
            
            If the customer shows interest, ask if they'd like to sign up for a free trial.
            If the customer declines or wants to end the call, be polite and end the conversation.
            If the customer asks a question you can't answer, offer to have a product specialist contact them.
            """
        }
        
        # Prepare messages for the API call
        messages = [system_message] + conversation["history"]
        
        # Call OpenAI API
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=messages,
            max_tokens=150
        )
        
        # Check if we should end the call based on the conversation
        if "thank you for your time" in response.choices[0].message.content.lower() or \
           "goodbye" in response.choices[0].message.content.lower():
            conversation["should_end"] = True
        
        return response.choices[0].message.content
    
    def _update_customer_responses(self, call_sid, customer_input):
        """Extract key information from customer input"""
        conversation = self.conversations[call_sid]
        
        # Use OpenAI to extract structured information
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extract key information from the customer response. Return a JSON with these fields if present: interest_level (high/medium/low), objections, questions, contact_preference (email/phone/none), email, callback_time."},
                {"role": "user", "content": customer_input}
            ],
            response_format={"type": "json_object"}
        )
        
        try:
            extracted_info = json.loads(response.choices[0].message.content)
            # Update customer responses with new information
            conversation["customer_responses"].update(extracted_info)
        except json.JSONDecodeError:
            # If JSON parsing fails, continue without updating
            pass
    
    def should_end_call(self, call_sid):
        """Check if the call should be ended"""
        if call_sid not in self.conversations:
            return False
        
        return self.conversations[call_sid]["should_end"]
    
    def get_call_data(self, call_sid):
        """Get all data collected during the call"""
        if call_sid not in self.conversations:
            return {}
        
        conversation = self.conversations[call_sid]
        
        # Determine call outcome
        if "interest_level" in conversation["customer_responses"]:
            interest = conversation["customer_responses"]["interest_level"]
            if interest == "high":
                outcome = "potential_sale"
            elif interest == "medium":
                outcome = "follow_up"
            else:
                outcome = "not_interested"
        else:
            outcome = "unknown"
        
        conversation["call_outcome"] = outcome
        
        return conversation
