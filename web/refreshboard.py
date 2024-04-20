
import pandas as pd
from flask_restful import Resource

class GoogleSheetReader(Resource):
    def __init__(self):
        super

    def get(self):
        data = pd.read_csv('assets/homepage.csv')
        branch_list = data['Branch'].to_list()
        companies = data['Company Name'].to_list()
        colleges_list  = data['College'].to_list()
        yops = data['YOP'].to_list()

        branch_list_map = {}
        companies_map = {}
        colleges_list_map = {}
        yops_list = {}

        for branch in branch_list:
            if branch in branch_list_map:
                branch_list_map[branch] += 1
            else:
                if branch is not "Nan":
                    branch_list_map[branch] = 1

        for company in companies:
            if company in companies_map:
                companies_map[company] += 1
            else:
                if company is not "Nan":
                    companies_map[company] = 1

        for colleges in colleges_list:
            if colleges in colleges_list_map:
                colleges_list_map[colleges] += 1
            else:
                if colleges is not "Nan":
                    colleges_list_map[colleges] = 1

        for yop in yops:
            if yop in yops_list:
                yops_list[yop] += 1
            else:
                if yop is not "Nan":
                    yops_list[yop] = 1

        yops_list = dict(sorted(yops_list.items(), key=lambda x: x[1], reverse=True))

        companies_map = dict(sorted(companies_map.items(), key=lambda x: x[1], reverse=True))

        colleges_list_map = dict(sorted(colleges_list_map.items(), key=lambda x: x[1], reverse=True))

        branch_list_map = dict(sorted(branch_list_map.items(), key=lambda x: x[1], reverse=True))

        FINAL_LIST = {
            "YOP_DICT" : yops_list,
            "COMPANIES" : companies_map,
            "COLLEGES_LIST" : colleges_list_map,
            "BRANCH_LIST" : branch_list_map
        }

        return FINAL_LIST
