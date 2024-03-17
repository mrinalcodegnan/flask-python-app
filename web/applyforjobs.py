from flask import request
from pymongo import MongoClient
from flask_restful import Resource

class ApplyForJob(Resource):
    def __init__(self) -> None:
        super().__init__()