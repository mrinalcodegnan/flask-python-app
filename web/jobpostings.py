from flask import request
from flask_restful import Resource
from pymongo import MongoClient
import uuid
from datetime import datetime
import threading
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class JobEmailSender(threading.Thread):
    def __init__(self, job_data, student_emails):
        super().__init__()
        self.job_data = job_data
        self.student_emails = student_emails

    def run(self):
        # Email sending logic
        for email in self.student_emails:
            self.send_email(email, self.job_data)

    def send_email(self, email, job_data):
        # Email content in HTML format
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>New Job Opportunity at {job_data['companyName']}!</title>
            <!-- CSS styles -->
        </head>
        <body>
            <!-- Email content -->
        </body>
        </html>
        """

        # Email configuration
        sender_email = "mrinalcodegnan@outlook.com"
        recipient_email = email
        subject = f"New Job Opportunity at {job_data['companyName']}!"

        # Create message container
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach HTML content to the email
        msg.attach(MIMEText(html_content, 'html'))

        # Send email using SMTP
        smtp_server = smtplib.SMTP('smtp.office365.com', 587)  # Update SMTP server details
        smtp_server.starttls()
        smtp_server.login(sender_email, 'Mrinal@iitm18')  # Update sender's email and password
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        smtp_server.quit()

class JobPosting(Resource):
    def __init__(self, client, db, collection, student_collection):
        super().__init__()
        self.client = client
        self.db_name = db
        self.collection_name = collection
        self.student_collection_name = student_collection
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        self.student_collection = self.db[self.student_collection_name]

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
        specialNote = data.get("specialNote")
        deadLine = data.get("deadLine")

        # Insert job posting data into MongoDB
        if self.db_name not in self.client.list_database_names():
            self.client[self.db_name]

        if self.collection_name not in self.db.list_collection_names():
            self.db.create_collection(self.collection_name)

        job_data = {
            "id": id,
            "timestamp": timestamp,
            "companyName": companyName,
            "jobRole": jobRole,
            "graduates": graduates,
            "salary": salary,
            "educationQualification": educationQualification,
            "department": department,
            "percentage": percentage,
            "technologies": technologies,
            "bond": bond,
            "jobLocation": jobLocation,
            "specialNote": specialNote,
            "deadLine": deadLine
        }
        result = self.collection.insert_one(job_data)
        job_data['_id'] = str(result.inserted_id)

        # Fetch only email addresses from student documents
        student_emails_cursor = self.student_collection.find({}, {"email": 1})
        student_emails = [student["email"] for student in student_emails_cursor]

        # Start a thread to send emails in the background
        email_sender_thread = JobEmailSender(job_data, student_emails)
        email_sender_thread.start()

        return {"message": "Job posting successful", "job_posting": job_data}, 200
