from flask import request, send_file, Response
from flask_restful import Resource
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId

class DownloadResume(Resource):
    def __init__(self, client, db_name):
        super().__init__()
        self.client = client
        self.db_name = db_name
        self.db = self.client[self.db_name]  # Initialize MongoDB database
        self.fs = GridFS(self.db)  # Initialize GridFS for file storage

    def post(self):
        # Get the resume_id from the request JSON data
        resume_id = request.json.get('student_id')

        if not resume_id:
            return {"error": "Missing student_id parameter"}, 400

        # Find the resume file in GridFS
        resume_file = self.fs.get(ObjectId(resume_id))

        if not resume_file:
            return {"error": "Resume not found"}, 404
        resume_data = resume_file.read()    

        # Return the resume file as a response without the Content-Disposition header
        return Response(resume_data, mimetype='application/pdf')
