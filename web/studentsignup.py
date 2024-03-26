from flask import request, render_template_string
from flask_restful import Resource
from pymongo import MongoClient
import uuid
from datetime import datetime
from gridfs import GridFS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class StudentSignup(Resource):
    def __init__(self, client, db, collection):
        super().__init__()
        self.client = client
        self.db_name = db
        self.collection_name = collection
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        self.fs = GridFS(self.db)  # Initialize GridFS for storing files

    def send_email(self, name, email):
        # Email content in HTML format
        html_content = """
        <html>
            <head>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background-color: #FFA500;
                        color: #000000;
                    }
                    .container {
                        padding: 20px;
                        background-color: #000000;
                        color: #FFA500;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Welcome to Codegnan Placements!</h2>
                    <p>Hello, {{ name }},</p>
                    <p>Thank you for signing up with Codegnan Placements. We are excited to have you on board!</p>
                    <p>Best Regards,<br/>Codegnan Placements Team</p>
                </div>
            </body>
        </html>
        """

        # Render email template with student's name
        rendered_html = render_template_string(html_content, name=name)

        # Email configuration
        sender_email = "mrinalnilotpal@outlook.com"
        recipient_email = email
        subject = "Welcome to Codegnan Placements!"

        # Create message container
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach HTML content to the email
        msg.attach(MIMEText(rendered_html, 'html'))

        # Send email using SMTP
        smtp_server = smtplib.SMTP('smtp.office365.com', 587)  # Update SMTP server details
        smtp_server.starttls()
        smtp_server.login(sender_email, 'Mrinal@iitm181')  # Update sender's email and password
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        smtp_server.quit()

    def post(self):
        # Extract data from the request
        data = request.form
        id = str(uuid.uuid4())

        timestamp = datetime.now().isoformat()
        name = data.get('name')
        age = data.get('age')
        password = data.get('password')
        phone = data.get('mobileNumber')
        email = data.get('email')
        state = data.get('state')
        qualification = data.get("qualification")
        city = data.get("cityname")
        department = data.get("department")
        yearOfPassing = data.get("yearOfPassing")
        collegeName = data.get("collegeName")
        resume_file = request.files.get('resume')  

        # Check if the database exists, if not, create it
        if self.db_name not in self.client.list_database_names():
            self.client[self.db_name]

        # Check if the collection exists, if not, create it
        if self.collection_name not in self.db.list_collection_names():
            self.db.create_collection(self.collection_name)

        # Check if all required fields are present
        if not (name and email and password and resume_file):
            return {"error": "Missing required fields"}, 400

        # Check if the email already exists in the collection
        if self.collection.find_one({"email": email}):
            return {"error": "Email already exists"}, 400

        # Insert student signup data into MongoDB
        student_data = {
            "id": id,
            "timestamp": timestamp,
            "name": name,
            "email": email,
            "password": password,
            "phone": phone,
            "age": age,
            "state": state,
            "qualification": qualification,
            "yearOfPassing": yearOfPassing,
            "city": city,
            "department": department,
            "collegeName": collegeName
        }
        result = self.collection.insert_one(student_data)
        student_data['_id'] = str(result.inserted_id)

        # Save the resume file to GridFS with student ID as filename
        resume_id = self.fs.put(resume_file, filename=id)

        # Add the resume file ID to student data
        student_data['resume_id'] = str(resume_id)

        # Send welcome email to the student
        self.send_email(name, email)

        # Return a success message along with student data
        return {"message": "Student signup successful", "student": student_data}, 201
