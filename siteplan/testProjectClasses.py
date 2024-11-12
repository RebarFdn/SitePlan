import asyncio
import os
#from pympler import asizeof
from modules.utils import generate_id, generate_docid
from modules.project import project_phases, all_projects, project_name_index, projects_api, get_project, save_project, delete_project


async def test_get_project(id='BH38038'):
    project = await get_project(id=id)
    try: print(project)
    finally: del project

async def test_delete_project(id='BH38038'):
    status = await delete_project(id=id)
    try: print(status)
    finally: del status


async def test_all_projects():
    all_es = await all_projects()
    try: print(all_es)
    finally: del all_es



async def test_project_name_index():
    data = await project_name_index()
    try: print(data)
    finally: del data


async def test_projects_api():
    data = await projects_api()
    try:
        print()
        print(data)
    finally: del data



async def main():      
    print('WARNING!  Data will Disappear in 15 seconds intervals....')
    print()

    #await test_all_projects() 
    #await asyncio.sleep(10)
    #os.system('clear')

    #await test_project_name_index()
    #await asyncio.sleep(10)
    #os.system('clear')

    #await test_projects_api() 
    #await asyncio.sleep(15)
    #os.system('clear')

    #await test_get_project() 
    #await asyncio.sleep(15)
    #os.system('clear')

    #await test_delete_project() 
    #await asyncio.sleep(5)
    #os.system('clear')

    #print(project_phases())
    #await asyncio.sleep(10)
    #os.system('clear')

    #print(generate_id(name='Madrid Place'))
    #print(generate_docid())
    #await asyncio.sleep(5)
    #os.system('clear')
    


if __name__ == '__main__':
    asyncio.run(
    main()    
    )
    

