from flask import request
from flask_restful import Resource
from pymongo import MongoClient

class StudentsApplied(Resource):
    def __init__(self, client, db, job_collection, student_collection):
        super().__init__()
        self.client = client
        self.db = db
        self.job_collection = job_collection
        self.student_collection = student_collection

    def get(self, job_id):
        # Search for the job document with the provided job_id
        job_document = self.job_collection.find_one({"id": job_id})

        if job_document:
            # Retrieve the applicants_ids array from the job document
            applicants_ids = job_document.get('applicants_ids', [])

            # Fetch the student details for the applicants
            student_details = []
            for student_id in applicants_ids:
                student_document = self.student_collection.find_one({"id": student_id})
                if student_document:
                    student_details.append({
                        "student_id": student_document.get('id'),
                        "name": student_document.get('name'),
                        "email": student_document.get('email'),
                        "phone": student_document.get('phone')
                    })
            return {"students_applied": student_details}, 200
        else:
            return {"error": "Job not found with the provided job_id"}, 404
