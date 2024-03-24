
from flask import request
from flask_restful import Resource
import json
from pymongo import MongoClient
import uuid
import json
from datetime import datetime

class JobPosting(Resource):
    def __init__(self,client, db, collection):
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
        companyName = data.get('companyName')
        jobRole = data.get('jobRole')
        graduates = data.get('graduates')
        salary = data.get('salary')
        educationQualification = data.get('educationQualification')
        department = data.get('department')
        percentage = data.get('percentage')
        technologies = data.get('technologies')
        bond = data.get('bond')
        jobLocation = data.get('jobLocation')
        specialNote=data.get("specialNote")
        # Check if all required fields are present
        #if not (id and company_name and profile and branches and skills_required and ctc and percentage and bond_years and
        #        work_location and year_of_passing and positions_open):
        #       return {"error": "Missing required fields"}, 400

        # Insert job posting data into MongoDB

        # Check if the database exists, if not, create it
        if self.db_name not in self.client.list_database_names():
            self.client[self.db_name]

        # Check if the collection exists, if not, create it
        if self.collection_name not in self.db.list_collection_names():
            self.db.create_collection(self.collection_name)

        job_data = {
            "id":id,
            "timestamp":timestamp,
            "companyName" : companyName,
            "jobRole" : jobRole,
            "graduates" : graduates,
            "salary" : salary,
            "educationQualification" : educationQualification,
            "department" : department,
            "percentage" : percentage,
            "technologies" : technologies,
            "bond" : bond,
            "jobLocation" : jobLocation,
            "specialNote":specialNote,
        }
        result = self.collection.insert_one(job_data)
        job_data['_id'] = str(result.inserted_id)

        # Return a success message along with job data
        return {"message": "Job posting successful", "job_posting": job_data}, 201
