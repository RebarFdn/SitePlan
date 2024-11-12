import asyncio
import os
#from pympler import asizeof
from modules.utils import generate_id, generate_docid

from modules.rate import all_rates, rate_categories, get_rate, get_industry_rate, delete_rate, all_rates_ref

async def test_get_rate(id='ST29346'):
    rate = await get_rate(id=id)
    try: print(rate)
    finally: del rate

async def test_get_industry_rate(id='ST29346'):
    rate = await get_rate(id=id)
    try: print(rate)
    finally: del rate

async def test_delete_rate(id='BH38038'):
    status = await delete_rate(id=id)
    try: print(status)
    finally: del status


async def test_all_rates():
    all_es = await all_rates()
    try: print(all_es)
    finally: del all_es



async def test_rates_api():
    data = await all_rates_ref()
    try:
        print()
        print(data)
    finally: del data



async def main():      
    print('WARNING!  Data will Disappear in 15 seconds intervals....')
    print()

    #await test_all_rates() 
    #await asyncio.sleep(10)
    #os.system('clear')

   

    #await test_rates_api() 
    #await asyncio.sleep(15)
    #os.system('clear')

    #await test_get_industry_rate() 
    #await asyncio.sleep(15)
    #os.system('clear')

    #await test_delete_rate() 
    #await asyncio.sleep(5)
    #os.system('clear')
    

    print(rate_categories())
    #print(generate_docid())
    await asyncio.sleep(5)
    os.system('clear')
    


if __name__ == '__main__':
    asyncio.run(
    main()    
    )
    

