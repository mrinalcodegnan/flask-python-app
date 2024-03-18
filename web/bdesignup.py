from flask import request
from flask_restful import Resource
from pymongo import MongoClient
import uuid
from datetime import datetime

class BdeSignup(Resource):
    def __init__(self, client, db, collection):
        super().__init__()
        self.client = client
        self.db_name = db
        self.collection_name = collection
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def post(self):
        # Extract data from the request
        data = request.get_json()
        id = str(uuid.uuid4())
        
        timestamp = datetime.now().isoformat()
        name = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if self.db_name not in self.client.list_database_names():
            self.client[self.db_name]

        # Check if the collection exists, if not, create it
        if self.collection_name not in self.db.list_collection_names():
            self.db.create_collection(self.collection_name)

        # Check if all required fields are present
        if not (name and email and password):
            return {"error": "Missing required fields"}, 400

        # Check if the email already exists in the collection
        if self.collection.find_one({"email": email}):
            return {"error": "Email already exists"}, 400

        # Insert BDE signup data into MongoDB
        bde_data = {
            "id": id,
            "timestamp": timestamp,
            "name": name,
            "email": email,
            "password": password,
            
        }
        result = self.collection.insert_one(bde_data)
        bde_data['_id'] = str(result.inserted_id)

        # Return a success message along with BDE data
        return {"message": "BDE signup successful", "bde": bde_data}, 201
