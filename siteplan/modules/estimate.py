# coding=utf-8
# estimate.py | 09-28-2004 | Ian Moncrieffe
# Dependents

import json
from pathlib import Path
from modules.utils import timestamp, filter_dates
from database import Recouch
from modules.project import Project
from modules.Estimate.estimate_models import EstimateModel
from config import DOCUMENT_PATH, IMAGES_PATH
from config import DATA_PATH
from logger import logger
import datetime
from tinydb import TinyDB, Query


class Estimate: 
    error_log:dict = {}
    meta_data:dict = {
        "created": 0, 
        "database": {"name":"site-estimates", "partitioned": False},              
    }
    instances = 0
    

    def __init__(self, data:dict=None): 
        Estimate.instances += 1      
        #self.conn = Recouch(local_db=self.meta_data.get('database').get('name'))
        self.db = TinyDB(Path.joinpath(DATA_PATH, "estimate.json"))
        
             
        if data :
            self.estimate = EstimateModel( **data )
            self.meta_data["created"] = timestamp()  
            self.meta_data["created_by"] = data.get('created_by')
            self.meta_data['properties'] = list(data.keys())              
            self.data = data
            self.data["meta_data"] = self.meta_data
                      
            if self.data.get("_id"):
                pass
            else:
                pass
                #self.generate_id(local=True)
        else:                     
            self.data = {"meta_data":self.meta_data}
       

    def save(self):
        if self.data:
            self.db.insert(self.estimate.model_dump())


    def all(self):
        return self.db.all()
    
    
    def get(self, project:str=None):
        result = self.collection.find_one(project=project)    