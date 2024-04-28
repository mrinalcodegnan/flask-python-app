from flask import request
from flask_restful import Resource
from pymongo import MongoClient

class GetAppliedJobsList(Resource):
    def __init__(self, client, db, job_collection, student_collection):
        super().__init__()
        self.client = client
        self.db_name = db
        self.job_collection_name = job_collection
        self.student_collection_name = student_collection
        self.db = self.client[self.db_name]
        self.job_collection = self.db[self.job_collection_name]
        self.student_collection = self.db[self.student_collection_name]

    def get(self):
        try:
            # Search for the student document with the provided student_id
            student_id = request.args.get('student_id')
            student_document = self.student_collection.find_one({"id": student_id})

            if student_document:
                # Retrieve the applied_jobs array from the student document
                applied_jobs = student_document.get('applied_jobs', [])

                # Fetch the job descriptions for the applied jobs
                job_descriptions = []
                for job_id in applied_jobs:
                    job_document = self.job_collection.find_one({"id": job_id})
                    if job_document:
                        job_descriptions.append({
                            "job_id": job_document.get('id'),
                            "companyName": job_document.get('companyName'),
                            "jobRole": job_document.get('jobRole'),
                            "graduates": job_document.get('graduates'),
                            "salary": job_document.get('salary'),
                            "educationQualification": job_document.get('educationQualification'),
                            "department": job_document.get('department'),
                            "percentage": job_document.get('percentage'),
                            "technologies": job_document.get('technologies'),
                            "bond": job_document.get('bond'),
                            "jobLocation": job_document.get('jobLocation'),
                            "specialNote": job_document.get('specialNote')
                        })
                return {"jobs_applied": job_descriptions}, 200
            else:
                return {"error": "Student not found with the provided student_id"}, 404

        except Exception as e:
            return {"error": str(e)}, 500

