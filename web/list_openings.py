import pymongo
from flask_restful import Resource, reqparse


class ListOpenings(Resource):
    def __init__(self, client, db, collection):
        super().__init__()
        self.client = client
        self.db = db
        self.collection = collection

    def get(self):
        # Retrieve all jobs from the collection
        job_documents = self.collection.find()

        # Prepare the list of job dictionaries
        job_list = []
        for job_document in job_documents:
            job_dict = {
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
            }
            job_list.append(job_dict)

        return {"jobs": job_list}, 200