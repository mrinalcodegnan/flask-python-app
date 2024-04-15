from flask import request
from flask_restful import Resource
from pymongo import MongoClient

class GetAppliedStudentList(Resource):
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
            # data = request.get_json()
            # job_id = data.get('job_id')
            job_id = request.args.get('job_id')
            print("job id",job_id)
            # Check if the database exists, if not, create it
            if self.db_name not in self.client.list_database_names():
                self.client[self.db_name]

            # Check if the job collection exists, if not, create it
            if self.job_collection_name not in self.db.list_collection_names():
                self.db.create_collection(self.job_collection_name)

            job_document = self.job_collection.find_one({"id": job_id})

            if job_document:
                applicants_ids = job_document.get('applicants_ids', [])

                student_details = []
                for student_id in applicants_ids:
                    student_document = self.student_collection.find_one({"id": student_id})
                    if student_document:
                        student_details.append({
                            "student_id": student_document.get('id'),
                            "name": student_document.get('name'),
                            "email": student_document.get('email'),
                            "highestGraduationCGPA": student_document.get('highestGraduationCGPA'),
                            "studentSkills":student_document.get('studentSkills'),
                            "phone": student_document.get('phone'),
                            "age": student_document.get('age'),
                            "state": student_document.get('state'),
                            "tenthStandard":student_document.get('tenthStandard'),
                            "twelfthStandard": student_document.get('twelfthStandard'),
                            "qualification": student_document.get('qualification'),
                            "yearOfPassing": student_document.get('yearOfPassing'),
                            "city" : student_document.get('city'),
                            "department" : student_document.get('department'),
                            "collegeName": student_document.get('collegeName')
                        })
                return {"students_applied": student_details}, 200
            else:
                return {"error": "Job not found with the provided job_id"}, 404

        except Exception as e:
            return {"error": str(e)}, 500
