# todo.py 
from tinydb import TinyDB
from pydantic import BaseModel
from config import DATA_PATH
from modules.utils import generate_id, timestamp

class Todo(BaseModel):
    id:str
    date:int
    description:str
    done:bool = False




print(DATA_PATH) 