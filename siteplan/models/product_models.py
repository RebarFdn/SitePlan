from datetime import date
from enum import Enum
from uuid import UUID, uuid4
from typing import List
from pydantic import BaseModel, EmailStr


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


if __name__ == '__main__':
    

    print('texts')