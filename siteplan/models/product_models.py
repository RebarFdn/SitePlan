from datetime import date
from enum import Enum
from uuid import UUID, uuid4
from typing import List
from pydantic import BaseModel, EmailStr
from collections import namedtuple


class Supplier(BaseModel):
    name:str


class InventoryItem(BaseModel):   
    ref:str=None
    name:str
    amt:int
    unit:str
    stocking_date:date = None
    supplier:Supplier

class Inventory(BaseModel): 
    id:UUID = uuid4()
    name:str
    items:list = []
    dispenced:list = []
    
    @property
    def stocking(self):
        stocking_:list = [item.get('amt') for item in self.items ]
        return stocking_
    
    @property
    def stock(self):        
        return sum(self.stocking)
    
    @property
    def stock_usage(self):       
        store = 0
        if len(self.dispenced) > 0:
            for item in self.dispenced:
                store += item[1]                
        else: pass
        return store
    
    @property
    def available_stock(self):       
        return self.stock - self.stock_usage



if __name__ == '__main__':
    

    print('texts')