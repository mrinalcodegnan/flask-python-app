from flask import Flask, send_file, request
from flask_restful import Resource
from pymongo import MongoClient
from gridfs import GridFS
from io import BytesIO
import zipfile

class DownloadResumes(Resource):
    def __init__(self, client, db):
        super().__init__()
        self.client = client
        self.db_name = db
        self.db = self.client[self.db_name]
        self.fs = GridFS(self.db)  # Initialize GridFS for retrieving files

    def post(self):
        # Get the list of student IDs from the request body
        student_ids = ["dd3bd3c6-b560-4ea8-8e61-c603df28ae09", "fa845f65-452d-4b93-af3e-a7a72ab702de"] #request.json.get("student_ids", [])
        print("Hello there!")
        if not student_ids:
            return {"error": "Missing required parameter: student_ids"}, 400

        # Create a BytesIO object to hold the zip archive
        zip_data = BytesIO()

        with zipfile.ZipFile(zip_data, 'w', zipfile.ZIP_DEFLATED) as zip_archive:
            for student_id in student_ids:
                # Find the file document in fs.files collection by filename
                file_doc = self.db.fs.files.find_one({"filename": student_id})

                if file_doc:
                    # Get the file's ID and retrieve the file from GridFS
                    file_id = file_doc["_id"]
                    grid_out = self.fs.get(file_id)

                    # Read the file's content
                    pdf_content = grid_out.read()

                    # Add the content to the zip archive with a specified name
                    zip_archive.writestr(f"{student_id}.pdf", pdf_content)
                else:
                    # Log or handle if a file is not found
                    print(f"No file found with filename '{student_id}'")

        # Reset the position of the zip_data for reading
        zip_data.seek(0)

        # Return the zip archive with appropriate headers for download
        return send_file(
            zip_data,
            mimetype="application/zip",
            as_attachment=True,
            download_name="resumes.zip"  # Name for the downloaded zip file
        )
