import os
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Database:
    def __init__(self):
        """Initialize database connection"""
        mongo_uri = os.environ.get('MONGO_URI')
        if not mongo_uri:
            raise ValueError("MongoDB URI not found in environment variables")
            
        print(f"Connecting to MongoDB at: {mongo_uri[:10]}...")
        self.client = MongoClient(mongo_uri)
        self.db = self.client['calling_agent_db']
        self.customers = self.db['customers']
        self.calls = self.db['calls']
    
    def get_customers_to_call(self, limit=10):
        """Get a list of customers to call"""
        # Get customers who haven't been called in the last 30 days or never called
        customers = list(self.customers.find({
            '$or': [
                {'last_called': {'$exists': False}},
                {'last_called': {'$lt': datetime.now().timestamp() - (30 * 24 * 60 * 60)}}
            ]
        }).limit(limit))
        
        return customers
    
    def update_call_status(self, call_sid, status):
        """Update call status in the database"""
        self.calls.update_one(
            {'call_sid': call_sid},
            {
                '$set': {
                    'status': status,
                    'updated_at': datetime.now().timestamp()
                }
            },
            upsert=True
        )
    
    def update_customer_details(self, call_data):
        """Update customer details based on call outcome"""
        customer_id = call_data.get('customer_id')
        phone_number = call_data.get('phone_number')
        
        # If we don't have a customer ID but have a phone number, try to find the customer
        if not customer_id and phone_number:
            customer = self.customers.find_one({'phone_number': phone_number})
            if customer:
                customer_id = customer['_id']
        
        # If we still don't have a customer ID, create a new customer
        if not customer_id:
            result = self.customers.insert_one({
                'phone_number': phone_number,
                'created_at': datetime.now().timestamp()
            })
            customer_id = result.inserted_id
        
        # Update customer with call information
        self.customers.update_one(
            {'_id': customer_id},
            {
                '$set': {
                    'last_called': datetime.now().timestamp(),
                    'last_call_outcome': call_data.get('call_outcome'),
                    'updated_at': datetime.now().timestamp()
                },
                '$push': {
                    'call_history': {
                        'call_sid': call_data.get('call_sid', ''),
                        'timestamp': datetime.now().timestamp(),
                        'outcome': call_data.get('call_outcome'),
                        'responses': call_data.get('customer_responses', {})
                    }
                }
            }
        )
        
        # Store complete call data
        self.calls.update_one(
            {'call_sid': call_data.get('call_sid', '')},
            {
                '$set': {
                    'customer_id': customer_id,
                    'phone_number': phone_number,
                    'outcome': call_data.get('call_outcome'),
                    'customer_responses': call_data.get('customer_responses', {}),
                    'conversation_history': call_data.get('history', []),
                    'completed_at': datetime.now().timestamp()
                }
            },
            upsert=True
        )
    
    def get_call_data(self, call_sid):
        """Get call data from the database"""
        call_data = self.calls.find_one({'call_sid': call_sid})
        if not call_data:
            return {
                'call_sid': call_sid,
                'conversation_history': []
            }
        return call_data
    
    def update_conversation_history(self, call_sid, conversation_history):
        """Update conversation history in the database"""
        self.calls.update_one(
            {'call_sid': call_sid},
            {
                '$set': {
                    'conversation_history': conversation_history,
                    'updated_at': datetime.now().timestamp()
                }
            },
            upsert=True
        )
