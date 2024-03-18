from flask import request
from flask_restful import Resource
from pymongo import MongoClient

class ApplyJob(Resource):
    def __init__(self, client, db, job_collection, student_collection):
        super().__init__()
        self.client = client
        self.db_name = db
        self.job_collection= job_collection
        self.student_collection = student_collection
        self.db = self.client[self.db_name]
        self.job_collection = self.db[self.job_collection]
        self.student_collection = self.db[student_collection]
        print("student col", self.student_collection)
        print("job_col", self.job_collection)

    def post(self):
        
        data = request.get_json()
        student_id = data.get('student_id')
        job_id = data.get('job_id')

        # Check if both student_id and job_id are provided
        if not (student_id and job_id):
            return {"error": "Both student_id and job_id are required"}, 400

        # Search for the job document with the provided job_id
        job_document = self.job_collection.find_one({"id": job_id})

        if job_document:
            # Update the job document to append the student_id to the applicants_ids array
            applicants_ids = job_document.get('applicants_ids', [])
            if student_id not in applicants_ids:
                applicants_ids.append(student_id)
                self.job_collection.update_one({"id": job_id}, {"$set": {"applicants_ids": applicants_ids}})
            else:
                return {"error": "Student already applied to this job"}, 400
        else:
            return {"error": "Job not found with the provided job_id"}, 404

        # Search for the student document with the provided student_id
        student_document = self.student_collection.find_one({"id": student_id})

        if student_document:
            # Update the student document to append the job_id to the applied_jobs array
            applied_jobs = student_document.get('applied_jobs', [])
            if job_id not in applied_jobs:
                applied_jobs.append(job_id)
                self.student_collection.update_one({"id": student_id}, {"$set": {"applied_jobs": applied_jobs}})
            else:
                return {"error": "Student already applied to this job"}, 400
        else:
            return {"error": "Student not found with the provided student_id"}, 404

        return {"message": "Student applied to job successfully"}, 200
