# app.py
from flask import Flask

from flask_cors import CORS
from web.refreshboard import GoogleSheetReader
from flask_restful import Api
from web.bdelogin import BdeLogin
from web.resumedownload import DownloadResume
from web.bdesignup import BdeSignup
from web.companylogin import CompanyLogin
from web.companysignup import CompanySignup
from web.jobsapplied import GetAppliedJobsList
from web.applyforjobs import JobApplication
from web.studentsapplied import GetAppliedStudentList
from web.list_openings import ListOpenings
from web.studentsignup import StudentSignup
from web.studentlogin import StudentLogin
from web.jobpostings import JobPosting  # Import JobPosting from jobpostings module
import json
import urllib.parse
from pymongo import MongoClient  # Import MongoClient from pymongo

with open('local_config.json', 'r') as config_file:
    config_data = json.load(config_file)

MONGO_CONFIG = config_data['MONGO_CONFIG']

class MyFlask(Flask):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        uri = MONGO_CONFIG['url']
        
        parsed_uri = urllib.parse.urlparse(uri)
        escaped_username = urllib.parse.quote_plus(parsed_uri.username)
        escaped_password = urllib.parse.quote_plus(parsed_uri.password)

        # Reconstruct URI with escaped username and password
        escaped_uri = uri.replace(parsed_uri.username, escaped_username).replace(parsed_uri.password, escaped_password)

        self.client = MongoClient(escaped_uri)
        self.db = self.client[MONGO_CONFIG['db_name']]
        self.collection = self.db[MONGO_CONFIG['collection_name']]

        self.bde_login_collection = MONGO_CONFIG["BDE_LOGIN"]["collection_name"]
        self.student_login_collection = MONGO_CONFIG["STUDENT_LOGIN"]["collection_name"]
        self.job_details_collection = MONGO_CONFIG["JOBS"]["collection_name"]
        self.company_login_collection = MONGO_CONFIG["COMPANY"]["collection_name"]

        self.DASHBOARDSHEET = config_data["DASHBOARD_GSHEET"]["url"]
        self.SHEET_NAME = config_data["DASHBOARD_GSHEET"]["sheetname"]

    def add_api(self):
        api = Api(self, catch_all_404s=True)
        api.add_resource(
            StudentSignup,
            "/api/v1/signup",
            resource_class_kwargs={
                'client' : self.client,
                'db' : "codegnan_prod",
                'collection' : self.student_login_collection
                }
        ),
        api.add_resource(
            StudentLogin,
            "/api/v1/studentlogin",
            resource_class_kwargs={
                'client' : self.client,
                'db' : "codegnan_prod",
                'collection' : self.student_login_collection
                }
        ),
        api.add_resource(
            BdeSignup,
            "/api/v1/bdesignup",
            resource_class_kwargs = {
                'client' : self.client,
                'db' : "codegnan_prod",
                'collection' : self.bde_login_collection
            }
        ),
        api.add_resource(
            BdeLogin,
            "/api/v1/bdelogin",
            resource_class_kwargs = {
                'client' : self.client,
                'db_name' : "codegnan_prod",
                'collection' : self.bde_login_collection
            }
        ),
        api.add_resource(
            CompanyLogin,
            "/api/v1/companylogin",
            resource_class_kwargs = {
                'client' : self.client,
                'db' : "codegnan_prod",
                'collection' : self.company_login_collection
            }
        ),
        api.add_resource(
            CompanySignup,
            "/api/v1/companysignup",
            resource_class_kwargs = {
                'client' : self.client,
                'db' : "codegnan_prod",
                'collection' : self.company_login_collection
            }
        ),
        api.add_resource(
            JobPosting,
            "/api/v1/postjobs",
            resource_class_kwargs={
                'client' : self.client,
                'db' : "codegnan_prod",
                'collection': self.job_details_collection,
                'student_collection': self.student_login_collection
            }
        ),
        api.add_resource(
            ListOpenings,
            "/api/v1/listopenings",
            resource_class_kwargs={
                'client' : self.client,
                'db' : "codegnan_prod",
                'collection': self.job_details_collection
            }
        ),
        api.add_resource(
            JobApplication,
            "/api/v1/applyforjob",
            resource_class_kwargs = {
                'client' : self.client,
                'db' : "codegnan_prod",
                'job_collection': self.job_details_collection,
                'student_collection': self.student_login_collection
            }
        ),
        api.add_resource(
            GetAppliedStudentList,
            "/api/v1/getappliedstudentslist",
            resource_class_kwargs = {
                'client' : self.client,
                'db' : "codegnan_prod",
                'job_collection': self.job_details_collection,
                'student_collection': self.student_login_collection
            }
        ),
        api.add_resource(
            GetAppliedJobsList,
            "/api/v1/getappliedjobslist",
            resource_class_kwargs = {
                'client' : self.client,
                'db' : "codegnan_prod",
                'job_collection': self.job_details_collection,
                'student_collection': self.student_login_collection
            }
        )
        api.add_resource(
            DownloadResume,
            "/api/v1/downloadresume",
            resource_class_kwargs = {
                'client' : self.client,
                'db_name': "codegnan_prod"
            }
        )
        
        api.add_resource(
            GoogleSheetReader,
            "/api/v1/refreshdashboard",
            resource_class_kwargs = {
                'url' : self.DASHBOARDSHEET,
                'sheet_name' : self.SHEET_NAME
            }
        )


app = MyFlask(__name__)
app.add_api()
CORS(app)
#app.run()
