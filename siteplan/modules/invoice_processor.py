# invoice_processor.py
from shutil import rmtree
from os import mkdir, rmdir, system
from time import sleep
from tinydb import TinyDB, Query
from pydantic import BaseModel
from pathlib import Path
from config import DATA_PATH
from modules.utils import generate_id, timestamp
from models.product_models import InvoiceItem
# Database 
def invoice_database(db_name:str=None)->str:
    return TinyDB(Path.joinpath(DATA_PATH, 'temp_invoice', f'{db_name}.json'))
    



def get_invoice_items(inv_no:str=None):
    db:TinyDB=invoice_database(db_name=inv_no)
    return db.all()


def save_invoice_item(inv_no:str=None, data:dict=None):  
    try:
        db:TinyDB=invoice_database(db_name=inv_no)
        if data:
            inv_item = InvoiceItem(**data)
            db.insert(inv_item.model_dump())        
        return db.all()              
    except Exception as e:
        return [str(e)]
    

def reset_invoice_repo()->None:
    """ Creates or overwrites the temporary invoice folder
    """
    repo_path = Path.joinpath(DATA_PATH, 'temp_invoice')
    try: mkdir(repo_path) 
    except FileExistsError: rmtree(repo_path)
    finally: mkdir(repo_path) 

    
def test_inv_process():
    invoice_item = InvoiceItem(
            itemno = 1,
            description = 'Portland Cement',
            quantity = 50,
            unit = "bag",
            price = 1525.20
    )
            
    invoiceno = '24090'
    items = save_invoice_item(inv_no=invoiceno, data=invoice_item.model_dump())
    print(items)

     
    
    

    

