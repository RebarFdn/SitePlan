# peer_share.py 
from tinydb import TinyDB, Query
from pydantic import BaseModel
from config import DATA_PATH
from modules.utils import timestamp

# Database 
def peer_share_database(db_name:str=None)->str:
    return TinyDB(DATA_PATH / db_name)
    

database = peer_share_database(db_name="peer_share_db.json")


class PeerShareData(BaseModel):
    timestamp:int = timestamp() # share creation Date time stamp 
    protocol:str # The main share directive handle 
    docid:str # id of the document being shared
    name:str # name or title of the document ....
    description:str # brief description of the document ...
    user:str # the owner or the authorised user sharing the document
    peers: list = [] # consumers or peer users using the shared document
    

def all_peer_share(db:TinyDB=database):
    return db.all()


def save_peer_share(data:dict=None, db:TinyDB=database):   
    if data:
        db.insert(data)        
        return all_peer_share()              
    else: return all_peer_share() 
    
    
def get_peer_share(docid:str=None, db:TinyDB=database): 
    peer_share:Query = Query()
    try:
        return db.search(peer_share.docid == docid)  
    except:
        return {}
    finally:
        del(peer_share)


def delete_peer_share(id:str=None, db:TinyDB=database): 
    peer_share:Query = Query()    
    ids = [ item.doc_id for item in  db.search(peer_share.docid == id) ]
    try:              
        db.remove(doc_ids=ids)
        return all_peer_share() 
    except:
        return all_peer_share() 
    finally:
        del(peer_share)
        del(ids)    

def is_sharing(id:str=None)->bool:
    if get_peer_share(docid=id):
        return True
    else:
        return False      
    

def add_consumer(id:str, consumer:dict=None, db:TinyDB=database ):
    document = get_peer_share(docid=id)[0]
    peers = document.get('peers')
    peers.append(consumer)
    peer_share:Query = Query() 
    db.update({'peers': peers}, peer_share.docid == id )
    return document
    

