from flask import request
from flask_restful import Resource
from pymongo import MongoClient

class JobsApplied(Resource):
    def __init__(self, client, db, job_collection, student_collection):
        super().__init__()
        self.client = client
        self.db = db
        self.job_collection = job_collection
        self.student_collection = student_collection

    def get(self, student_id):
        # Search for the student document with the provided student_id
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
                        "company_name": job_document.get('company_name'),
                        "profile": job_document.get('profile'),
                        "branches": job_document.get('branches'),
                        "skills_required": job_document.get('skills_required'),
                        "ctc": job_document.get('ctc'),
                        "percentage": job_document.get('percentage'),
                        "bond_years": job_document.get('bond_years'),
                        "work_location": job_document.get('work_location'),
                        "year_of_passing": job_document.get('year_of_passing'),
                        "positions_open": job_document.get('positions_open')
                    })
            return {"jobs_applied": job_descriptions}, 200
        else:
            return {"error": "Student not found with the provided student_id"}, 404
