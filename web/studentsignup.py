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
    def _init_(self, client, db, collection):
        super()._init_()
        self.client = client
        self.db_name = db
        self.collection_name = collection
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]
        self.fs = GridFS(self.db)  # Initialize GridFS for storing files

    def send_email(self, name, email):
        # Email content in HTML format
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Codegnan Placements!</title>
            <style>
                /* Global styles */
                body {
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }
                .container {
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                }
                .content {
                    text-align: center;
                }
                h1, p {
                    margin-bottom: 20px;
                }
                .button {
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #FFA500;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s ease;
                }
                .button:hover {
                    background-color: #FFD700;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h1>Welcome to Codegnan Placements!</h1>
                    <p>Hello, {{ name }},</p>
                    <p>Congratulations on taking the first step towards a successful career!</p>
                    <p>At Codegnan Placements, we are committed to helping you achieve your goals and aspirations. Our team of experts is here to support you every step of the way.</p>
                    <p>Explore our website to discover a world of opportunities and resources tailored just for you.</p>
                    <a href="http://placements.codegnan.com/login/student" class="button">Explore Now</a>
                </div>
            </div>
        </body>
        </html>
        """

        # Render email template with student's name
        rendered_html = render_template_string(html_content, name=name)

        # Email configuration
        sender_email = "Placements@codegnan.com"
        recipient_email = email
        subject = "Welcome to Codegnan Placements!"

        # Create message container
        msg = MIMEMultipart('alternative')
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach HTML content to the email
        msg.attach(MIMEText(rendered_html, 'html'))

        # Send email using SMTP (for Gmail)
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)  # Update SMTP server details for Gmail
        smtp_server.starttls()
        smtp_server.login(sender_email, 'Codegnan@0818')  # Update sender's email and password
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        smtp_server.quit()

    def post(self):
        # Extract data from the request
        data = request.form
        id = str(uuid.uuid4())
        print(data,"before mongo")

        timestamp = datetime.now().isoformat()
        name = data.get('name')
        age = int(data.get('age'))
        password = data.get('password')
        phone = int(data.get('mobileNumber'))
        email = data.get('email')
        state = data.get('state')
        qualification = data.get("qualification")
        city = data.get("cityName")
        department = data.get("department")
        yearOfPassing = data.get("yearOfPassing")
        collegeName = data.get("collegeName")
        highestGraduationCGPA = float(data.get("highestGraduationCGPA"))
        studentSkills = data.getlist("studentSkills[]")
        tenthStandard = int(data.get("tenthStandard"))
        twelfthStandard = int(data.get("twelfthStandard"))
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
            return {"error": "Email already exists"}, 409

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
            "collegeName": collegeName,
            "highestGraduationCGPA": highestGraduationCGPA,
            "studentSkills": studentSkills,
            "tenthStandard": tenthStandard,
            "twelfthStandard":twelfthStandard
        }
        result = self.collection.insert_one(student_data)
        student_data['_id'] = str(result.inserted_id)

        # Save the resume file to GridFS with student ID as filename
        resume_id = self.fs.put(resume_file, filename=id)

        # Add the resume file ID to student data
        student_data['resume_id'] = str(resume_id)
        print("student signup",student_data)
               # Send welcome email to the student
        self.send_email(name, email)

        # Return a success message along with student data
        return {"message": "Student signup successful", "student": student_data}, 201