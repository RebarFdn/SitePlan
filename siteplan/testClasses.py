import asyncio
import os
#from pympler import asizeof
from modules.utils import generate_id
from modules.project import Project
from modules.employee import all_employees, all_workers, get_worker, get_worker_name_index, get_worker_by_name, generate_id

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



async def main():      
    print('WARNING!  Data will Disappear in 15 seconds intervals....')
    print()

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
    #await asyncio.sleep(5)
    #os.system('clear')
    


if __name__ == '__main__':
    asyncio.run(
    main()    
    )
    

