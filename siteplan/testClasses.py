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

from modules.dropbox import Dropbox

inventory:dict = {}

async def test_get_worker(id='JC53253'):
    employee = await get_worker(id=id)
    try: print(employee)
    finally: del employee


async def test_all_workers():
    all_es = await all_workers()
    try: print(all_es)
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
    interval = 10   
    print(f'WARNING!  Data will Disappear in { interval } seconds intervals....')
    print()
    await test_dropbox()
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

    #await test_workers() 
    #await asyncio.sleep(5)
    #s.system('clear')

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
    

