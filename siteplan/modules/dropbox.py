# Dropbox | By Ian Moncrieffe | Dec 4 2024
import os
from uuid import uuid4
from pydantic import BaseModel
from collections import OrderedDict
from config import DROPBOX_PATH


class Dropbox(BaseModel):
    location:str = DROPBOX_PATH
    url:str = 'drop_box'
    dropbox_log: list = []

    @property
    def contents(self):
        '''Lists the contents of the Dropbox'''
        items = os.listdir(self.location)
        for item in items:
            self.dropbox_log.append(OrderedDict(
                {"id": uuid4(), "item": item, 'url': f"{self.url}/{item}" }
                ))
        return self.dropbox_log
    
    def upload(self, content):
        '''saves a file in the dropbox directory
        and log a record of the event in the dropbox_log
        '''





    