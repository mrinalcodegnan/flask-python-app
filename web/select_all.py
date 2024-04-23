import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import request, render_template_string
from flask_restful import Resource
from pymongo import MongoClient
from threading import Thread

class UpdateJobApplicants(Resource):
    def __init__(self, client, db, job_collection, student_collection):
        super().__init__()
        self.client = client
        self.db_name = db
        self.job_collection_name = job_collection
        self.student_collection_name = student_collection
        self.db = self.client[self.db_name]
        self.job_collection = self.db[self.job_collection_name]
        self.student_collection = self.db[self.student_collection_name]

    def post(self):
        try:
            data = request.get_json()
            job_id = data.get('job_id')
            selected_student_ids = data.get('selected_student_ids', [])
            

            # Retrieve the job document
            job_document = self.job_collection.find_one({"id": job_id})

            if job_document:
                # Retrieve the list of applicants from the job document
                applicants_ids = job_document.get('applicants_ids', [])
                

                # Calculate the set of selected and rejected students
                selected_students = list(set(selected_student_ids))
                rejected_students = list(set(applicants_ids) - set(selected_student_ids))

                print(selected_students)
                print(rejected_students)

                # Update the job document with selected and rejected students
                update_result = self.job_collection.update_one(
                    {"id": job_id},
                    {"$set": {
                        "selected_students_ids": selected_students,
                        "rejected_students_ids": rejected_students
                    }}
                )
                
                if update_result.modified_count >= 0:
                    # Update student documents
                    self.update_student_documents(selected_students, rejected_students, job_id)

                    # Get job details for custom email
                    company_name = job_document.get('companyName')
                    job_position = job_document.get('jobRole')

                    self.send_custom_email(selected_students,rejected_students, company_name, job_position)
                    #Thread(target=self.send_custom_email, args=(selected_students, rejected_students, company_name, job_position)).start()

                    return {"message": "Job applicants and student documents updated successfully"}, 200
                else:
                    return {"error": "Failed to update job applicants"}, 500
            else:
                return {"error": "Job not found with the provided job_id"}, 404

        except Exception as e:
            return {"error": str(e)}, 500

    def update_student_documents(self, selected_students, rejected_students, job_id):
        # Update selected students

        
        for student_id in selected_students:
            self.student_collection.update_one(
                {"id": student_id},
                {"$addToSet": {"selected_jobs": job_id}},
                upsert=True
            )

        # Update rejected students
        for student_id in rejected_students:
            self.student_collection.update_one(
                {"id": student_id},
                {"$addToSet": {"rejected_jobs": job_id}},
                upsert=True
            )

    def send_custom_email(self, selected_students, rejected_students, company_name, job_position):
        for student_id in selected_students:
            student_document = self.student_collection.find_one({"id": student_id})
            if student_document:
                name = student_document.get('name')
                email = student_document.get('email')
                self.send_email(name, email, company_name, job_position, selected=True)

        for student_id in rejected_students:
            student_document = self.student_collection.find_one({"id": student_id})
            if student_document:
                name = student_document.get('name')
                email = student_document.get('email')
                self.send_email(name, email, company_name, job_position, selected=False)

    def send_email(self, name, email, company_name, job_position, selected=True):
        # Customize email content based on selected or rejected status
        subject = f"Placement Notification - {company_name}"

        if selected:
            message = render_template_string("""
                <p>Dear {{ name }},</p>
                <p>Congratulations!</p>
                <p>We are delighted to inform you that you have been selected for the next round for the position of <strong>{{ job_position }}</strong> at <strong>{{ company_name }}</strong>.</p>
                <p>Best regards,</p>
                <p>Codegnan Placements</p>
            """, name=name, job_position=job_position, company_name=company_name)
        else:
            message = render_template_string("""
                <p>Dear {{ name }},</p>
                <p>We regret to inform you that your application for the position of <strong>{{ job_position }}</strong> at <strong>{{ company_name }}</strong> has been unsuccessful.</p>
                <p>We appreciate your interest in our company and wish you all the best in your future endeavors.</p>
                <p>Thank you for your time and consideration.</p>
                <p>Best regards,</p>
                <p>Codegnan Placements</p>
            """, name=name, job_position=job_position, company_name=company_name)

        # Email configuration
        sender_email = "Placements@codegnan.com"

        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = email
        msg['Subject'] = subject

        # Attach message to email
        msg.attach(MIMEText(message, 'html'))

        # Send email using SMTP (for Gmail)
        try:
            smtp_server = smtplib.SMTP('smtp.gmail.com', 587)  # Update SMTP server details for Gmail
            smtp_server.starttls()
            smtp_server.login(sender_email, 'Codegnan@0818')  # Update sender's email and password
            smtp_server.sendmail(sender_email, email, msg.as_string())
            smtp_server.quit()
        except Exception as e:
            print("Failed to send email:", e)
