#modeler.py
#import aiohttp

from starlette.responses import JSONResponse
from decoRouter import Router
try:
    from modules.utils import timestamp
except ImportError:
    from utils import timestamp

from database import Recouch

#from memory_profiler import profile

#fp=open('mem_pflr.log', 'w+')


class Session:    
    meta_data:dict = {
        "created": 0, 
        "database": {"name":"session", "partitioned": False}
              
    }
    
    def __init__(self, data:dict=None) -> None:
        self.conn = Recouch(local_db=self.meta_data.get('database').get('name'))         
        self.meta_data["created"] = timestamp()

       
    async def post(self, data:dict=None):
        r = None
        try:
            r = await self.conn.post( json=self.data )  
            return r  
        except Exception as e:
            return {'error': str(e)}
        finally: del(r)


    #@profile
    async def get(self, id:str="session"):
        r = None
        try:
            r = await self.conn.get( _directive=id) 
            return r  
        except Exception as e:
            {'error': str(e)}
        finally: del(r)

    
    #@profile
    async def update(self, data:dict=None):
        if '_rev' in list(data.keys()): del(data['_rev'])
        try: return await self.conn.put(json=data)            
        except Exception as e: return {'error': str(e)}        

    #@profile
    async def delete(self, id:str="session"):        
        try: return await self.conn.delete(_id=id)
        except Exception as e: return {'error': str(e)}     

    

# User Router
session_router = Router()

# CREATE NEW
@session_router.get('/session')
async def session( request ):
    """
    """
    s = Session()      
   
    try:
        return JSONResponse(await s.get())
    except Exception as e: return JSONResponse({"error": str(e)})

@session_router.put('/session')
async def update_session( request ):
    """
    """
    data = await request.json()
    s = Session()      
   
    try:
        return JSONResponse(await s.update(data=data))
    except Exception as e: return JSONResponse({"error": str(e)})

