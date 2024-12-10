# todo.py 
from os import system
from time import sleep
from tinydb import TinyDB, Query
from pydantic import BaseModel
from pathlib import Path
from config import DATA_PATH
from modules.utils import generate_id, timestamp

# Database 
def todo_database(db_name:str=None)->str:
    return TinyDB(Path.joinpath(DATA_PATH, db_name))
    

database = todo_database(db_name="todo.json")


class Todo(BaseModel):
    id:str
    date:int
    description:str
    priority:int=1
    done:bool = False




def all_todo(db:TinyDB=database):
    return db.all()


def save_todo(data:dict=None, db:TinyDB=database):   
    if data:
        db.insert(data)        
        return all_todo()              
    else: return all_todo() 
    
    
def get_todo(id:str=None, db:TinyDB=database): 
    todo:Query = Query()
    try:
        return db.search(todo.id == id)  
    except:
        return {}
    finally:
        del(todo)


def delete_todo(id:str=None, db:TinyDB=database): 
    todo:Query = Query()    
    ids = [ item.doc_id for item in  db.search(todo.id == id) ]
    try:              
        result = db.remove(doc_ids=ids)
        return all_todo() 
    except:
        return all_todo() 
    finally:
        del(todo)
        del(ids)         



       
def update_todo(data:dict=None, db:TinyDB=database):   
    try:
        delete_todo(id=data.get('id'))
        sleep(1)
        save_todo(data=data)
        return all_todo()             
    except: 
        return all_todo() 

    
def clear_screen(delay:int=5):
    sleep(delay)
    system('clear')



if __name__ == '__main__':
    todo_data = {
        "id": generate_id('to do'),
        "date": timestamp(),
        "description": 'Complete Filter for add employee to job crew',
        "done": False
    } 
    todo = Todo(**todo_data)
    try:
        #saved = save_todo(data=todo.model_dump())
        #todos = all_todo()
        #print(todos)
        print()
        #print('Delete', delete_todo(id='TD64339'))
        
    except Exception as exception: print(exception)
    #clear_screen(10)
    print(all_todo())



    #todoi =(get_todo(id='TD64339'))
    #print(todoi)
    #todo.done=True
    print(todo)
    #updated = update_todo(data=todo.model_dump())
    #print(updated)
    clear_screen(8)