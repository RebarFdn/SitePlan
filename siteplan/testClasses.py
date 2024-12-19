import asyncio
import os
#from pympler import asizeof
from modules.utils import generate_id,timestamp
from modules.project import Project
from modules.employee import all_employees, all_workers, get_worker, get_worker_name_index, get_worker_by_name, generate_id
from modules.inventory import  InventoryItem, test_inventory
from modules.invoice_processor import get_invoice_items, reset_invoice_repo, test_inv_process
from datetime import date
from box import Box
from modules.supplier import supplier_model
from modules.rate import all_rates, all_rates_ref
from modules.purchase_order import PurchaseItem, PurchaseOrder

from modules.dropbox import Dropbox

inventory:dict = {}

async def test_get_worker(id='JC53253'):
    employee = await get_worker(id=id)
    try: print(employee)
    finally: del employee


async def test_all_workers():
    all_es = await all_workers()
    try: print(all_es[0])
    finally: del all_es


async def test_all_employees():
    all_es = await all_employees()
    try: print(all_es)
    finally: del all_es


async def test_get_worker_name_index():
    data = await get_worker_name_index()
    try: print(data)
    finally: del data

## test get_worker_by_name
async def test_get_worker_by_name():
    data = await get_worker_by_name('Anuk Moncrieffe')
    try: print(data)
    finally: del data

async def test_dropbox():
    dropbox:Dropbox = Dropbox()
    print(dropbox)
    print(dropbox.contents)


async def main():   
    interval = 20   
    print(f'WARNING!  Data will Disappear in { interval } seconds intervals....')
    purchase1 = PurchaseItem(item_no=12, description='wire nails', quantity=10.5, unit='lb')
    purchase2 = PurchaseItem(item_no=162, description='Concrete nails', quantity=30.5, unit='lb')
    order = PurchaseOrder(
        id='PO445',
        title="Perliminary Materials List", 
        site='D Daniels Dwelling', 
        location='89 Atrium Housing Development, Bushy Pk. St Catherine.',
        date=123495
        
        )
    
    order.add_item(purchase1)
    #print(order.model_dump())  
    print('closing order') 
    order.close
   # await asyncio.sleep(1)
   # print(order.items)
    order.open
    #print('opening order') 
    order.add_item(purchase2)
    #order.items.append(purchase2)
    await asyncio.sleep(1)
    #print('repr', order.__repr__())
    order.close
    
    Item = order.get_item(2)
    
    #print('Order Item', order.get_item(2))
    order.delete_item(2)
    print('repr', order.__repr__)

    #rates = await all_rates()
    #rate:dict = rates[0]
    #del rate['_rev']
    #print('From all_rates', rates.__len__(), rate)
    #await test_dropbox()
    #print(supplier_model())
    #make_invoice_repo()
    #print(test_inv_process())

    #await test_get_worker_by_name() 
    #await asyncio.sleep(10)
    #os.system('clear')

    #await test_get_worker_name_index()
    #await asyncio.sleep(10)
    #os.system('clear')

    #await test_worker() 
    #await asyncio.sleep(10)
    #os.system('clear')

    #await test_all_workers() 
    #await asyncio.sleep(5)
    #os.system('clear')

    #await test_employees()
    #await asyncio.sleep(5)
    #os.system('clear')

    #print(generate_id(name='Dave Brown'))
    
    #print(timestamp('2024-10-24'))
    #await asyncio.sleep(10)
    #os.system('clear')
    #test_inventory()
    
    await asyncio.sleep(interval)
    os.system('clear')
    


if __name__ == '__main__':
    asyncio.run(
    main()    
    )
    

