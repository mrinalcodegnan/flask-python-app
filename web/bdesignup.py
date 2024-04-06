from flask import request
from flask_restful import Resource
from pymongo import MongoClient
import uuid
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class BdeSignup(Resource):
    def __init__(self, client, db, collection):
        super().__init__()
        self.client = client
        self.db_name = db
        self.collection_name = collection
        self.db = self.client[self.db_name]
        self.collection = self.db[self.collection_name]

    def send_email(self, name, email):
        # Email content in HTML format
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Welcome to Codegnan Placements!</title>
            <style>
                /* Global styles */
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 600px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #ffffff;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    border-radius: 10px;
                }}
                .content {{
                    text-align: center;
                }}
                h1, p {{
                    margin-bottom: 20px;
                }}
                .button {{
                    display: inline-block;
                    padding: 10px 20px;
                    background-color: #FFA500;
                    color: #ffffff;
                    text-decoration: none;
                    border-radius: 5px;
                    transition: background-color 0.3s ease;
                }}
                .button:hover {{
                    background-color: #FFD700;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    <h1>Welcome to Codegnan Placements!</h1>
                    <p>Hello, {name},</p>
                    <p>Congratulations on joining our team as a Business Development Executive!</p>
                    <p>We are excited to have you on board and look forward to working together to achieve great success.</p>
                    <p>Explore our website to learn more about our services and offerings.</p>
                    <a href="https://www.codegnan.com" class="button">Explore Now</a>
                </div>
            </div>
        </body>
        </html>
        """

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
        msg.attach(MIMEText(html_content, 'html'))

        # Send email using SMTP (for Gmail)
        smtp_server = smtplib.SMTP('smtp.gmail.com', 587)  # Update SMTP server details for Gmail
        smtp_server.starttls()
        smtp_server.login(sender_email, 'Codegnan@0818')  # Update sender's email and password
        smtp_server.sendmail(sender_email, recipient_email, msg.as_string())
        smtp_server.quit()

    def post(self):
        # Extract data from the request
        data = request.get_json()
        id = str(uuid.uuid4())
        
        timestamp = datetime.now().isoformat()
        name = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        if self.db_name not in self.client.list_database_names():
            self.client[self.db_name]

        # Check if the collection exists, if not, create it
        if self.collection_name not in self.db.list_collection_names():
            self.db.create_collection(self.collection_name)

        # Check if all required fields are present
        if not (name and email and password):
            return {"error": "Missing required fields"}, 400

        # Check if the email already exists in the collection
        if self.collection.find_one({"email": email}):
            return {"error": "Email already exists"}, 400

        # Insert BDE signup data into MongoDB
        bde_data = {
            "id": id,
            "timestamp": timestamp,
            "name": name,
            "email": email,
            "password": password,
        }
        result = self.collection.insert_one(bde_data)
        bde_data['_id'] = str(result.inserted_id)

        # Send welcome email to the BDE
        self.send_email(name, email)

        # Return a success message along with BDE data
        return {"message": "BDE signup successful", "bde": bde_data}, 201
