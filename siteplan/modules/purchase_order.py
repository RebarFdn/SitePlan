from typing import List
from time import sleep
from pydantic import BaseModel
from tinydb import TinyDB, Query
from flagman import Flagman
from modules.utils import timestamp, generate_id 
from config import DATA_PATH

# Database Config

def purchase_order_database(db_name:str=None)->str:
    return TinyDB(DATA_PATH / db_name)    

database = purchase_order_database(db_name="purchase_order.json")

# Models 
class PurchaseItem(BaseModel):
    """Represents an item on a materials list or purchase order"""
    item_no: int
    description:str
    quantity: float
    unit: str


class PurchaseOrder(BaseModel):
    id:str = generate_id(name="Purchase Order")
    title: str = "Purchase Order"
    site: str | None = None
    location: str | None = None
    date: int = timestamp()
    __items: List[PurchaseItem] = []
    resolved: bool = False
    
    @property
    def items(self)->list:
        """Material items to be purchased

        Returns:
            list: List of dictionary with material description, 
            amount, and unit of measurement
        """
        return list(self.__items)
    

    def add_item(self, item:PurchaseItem )->None:
        """Add an item to the purchases list 

        Args:
            item (PurchaseItem): A dictionary with Fields [ item_no,
            description, quantity, unit]

        """
        if self.resolved:
            Flagman(title='Closed Order', message='Sorry, The Purchase Order is Closed!').send
            print('Sorry, The Purchase Order is Closed!')
            return False
        else:
            try:
                item.item_no = self.__items.__len__() + 1
                self.__items.append(item)
                return True
            except:
                return False
            
    
    def get_item(self, item_no: int)->PurchaseItem:
        """Get a single item from the Purchase order

        Args:
            item_no (int): Assigned item number on The purchase order list0

        Returns:
            PurchaseItem: _description_
        """
        return [item for item in self.items if item.item_no == item_no][0]
    

    def update_item(self, 
            item_no:int, 
            description:str=None,
            quantity:float=None,
            unit:str=None)->PurchaseItem:    
        if self.resolved:
            Flagman(title='Update Purchase Item', message='Sorry, You cannot operate on a closed Purchase Order !').send
        else:
            try:
                record = self.get_item(item_no)
                if description:
                    record.description = description
                elif quantity:
                    record.quantity = quantity
                elif unit:
                    record.unit = unit
                else:
                    pass
                return record
            except Exception as e:
                Flagman(title='Update Purchase Item', message=str(e)).send
      

    def delete_item(self, item_no:int):
        if self.resolved:
            Flagman(title='Delete Purchase Item', message='Sorry, You cannot operate on a closed Purchase Order !').send
        else:
            try:
                for item in self.__items:
                    if item.item_no == item_no:
                        self.__items.remove(item)
            except Exception as e:
                Flagman(title='Delete Purchase Item', message=str(e)).send    
            
    @property
    def close(self)->None:
        """Resolves the Purchase Order 
        preventing further addition to its contents

        """
        self.resolved = True
        self.__items = tuple(self.__items)

    @property
    def open(self)->None:
        """Opens a Resolved Purchase Order
        for modification in change order situations
        """
        if not self.resolved:
            Flagman(title='Open Order', message='The Purchase Order is already Open to Modification!').send
        else:
            self.resolved = False
            self.__items = list(self.__items)

    
    @property
    def __repr__(self):
        data = self.model_dump()        
        try:
            data['items'] = self.items
            return data
        finally:
            del data

    
    @property
    def __json__(self):
        data = self.model_dump()        
        try:
            data['items'] = [ item.model_dump() for item in self.items ]
            return data
        finally:
            del data


# Data Processors 
def processOrder(purchase_order:dict)->PurchaseOrder:
    """Converts a purchaseorder dictionary and its 
        items to a PurchaseOrder Model Object 
    """
    order_items:list = purchase_order.get('items')
    #print('ORDER_ITEMS', order_items)
    if order_items.__len__() > 0:
        
        __items = [PurchaseItem(**item) for item in order_items]# convert items 
        del purchase_order['items']
        payload = PurchaseOrder(**purchase_order)
        if payload.resolved:
            payload.open
            for item in __items:
                payload.add_item(item)   
            payload.close
        else:
            for item in __items:
                payload.add_item(item)
    else:
        del purchase_order['items']
        payload = PurchaseOrder(**purchase_order)
       
    return payload


# CRUD 
def all_order(db:TinyDB=database):
    return db.all()


def save_order(data:dict=None, db:TinyDB=database):   
    if data:
        db.insert(data)        
        return all_order()              
    else: return all_order() 

    
def get_order(id:str=None, db:TinyDB=database): 
    order:Query = Query()
    try:
        payload:list = db.search(order.id == id)  
        payload:dict = payload[0]       
        return processOrder(purchase_order=payload)
    except:
        return {}
    finally:
        del(order)


def delete_order(id:str=None, db:TinyDB=database): 
    order:Query = Query()    
    ids = [ item.doc_id for item in  db.search(order.id == id) ]
    try:              
        result = db.remove(doc_ids=ids)
        return all_order() 
    except:
        return all_order() 
    finally:
        del(order)
        del(ids)         



       
def update_order(data:dict=None, db:TinyDB=database):   
    try:
        delete_order(id=data.get('id'))
        sleep(1)
        save_order(data=data)
        return all_order()             
    except: 
        return all_order() 