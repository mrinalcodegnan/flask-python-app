
import pymongo
from flask_restful import Resource, reqparse

class StudentLogin(Resource):
    def __init__(self) -> None:
        super().__init__()