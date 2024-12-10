from datetime import date
from enum import Enum
from uuid import UUID, uuid4
from typing import List
from pydantic import BaseModel, EmailStr
from collections import namedtuple
from modules.utils import generate_id
from models.human_resource_models import Supplier



class InvoiceItem(BaseModel):
    itemno:int
    description:str
    quantity:float
    unit:str
    price:float


class Invoice(BaseModel):
    supplier:Supplier
    invoiceno:str
    datetime:str
    items:List[InvoiceItem]
    tax:float
    total:float
    billed:bool = False


class InventoryItem(BaseModel):   
    ref:str=None
    name:str
    amt:int
    unit:str
    stocking_date:str = None
    supplier:Supplier


class Inventory(BaseModel): 
    id:UUID = uuid4()
    name:str
    items:list = []
    dispenced:list = []
    
    @property
    def stocking(self)->list:
        stocking_:list = [item.get('amt') for item in self.items ]
        return stocking_
    
    @property
    def stock(self):        
        return sum(self.stocking)
    
    @property
    def stock_usage(self)->int:           
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