#Recouch 1.0.2 Rebar Database Adaptor Service database.py 
#Apache CouchDb Handler and Controller
#author: Tan Moncrieffe
#date Nov 23 2022
#couchdb cookie value = 299C5A4368900F0F038E528974770DC4
#Dependencies
import httpx
import asyncio
import aioredis

from modules.utils import timestamp

class Recouch:
    local_database:str = None
    base_url:str = None
    local_url:str = None
    slave_database:str = None
    slave_url:str = None

    def __init__(self, local_db:str = None):
        '''Apache Couchdb async Client 
        ---
            
        '''
        from config import (DB_ADMIN, ADMIN_ACCESS)   
        self.base_url = f"http://{DB_ADMIN}:{ADMIN_ACCESS}@localhost:5984/"
        self.slave_url = self.base_url               
        if local_db:
            self.local_database = local_db  
            self.local_url = f"{self.base_url}{self.local_database}/"
        else:
            pass 
    
       
    def resolve_url_path(self, db:str=None, _directive:str=None ):
        '''Resolves the database query url string.
        ---
        defaults to the database server connection handle if called
        without arguments. 
        db shall be the slave database used for a partuclar request
        _directive can be any of the following: 
        [an items _id "", "_all_docs", "_design/xxxx/_view/xx"]
        '''
        def reset_slave_url():
            self.slave_url = self.base_url

        url_path:str = None
        try:
            reset_slave_url()            
            # Case-1 database and directive
            if db and _directive: 
                self.slave_database = db # assign slave 
                self.slave_url = f"{self.slave_url}{self.slave_database}/" # construct url                
                url_path = f"{self.slave_url}{_directive}"                
            # Case-2 directive without database but a local database exist         
            elif self.local_database and _directive and not db:
                url_path = f"{self.local_url}{_directive}"
            # Case-3 database without directive
            elif db and not _directive:
                self.slave_database = db # assign slave 
                self.slave_url = f"{self.slave_url}{self.slave_database}/" # construct url
                url_path = f"{self.slave_url}"
            # Case-4 no database no directive
            elif self.local_database and not _directive and not db:
             url_path = self.local_url # return the database connector 
             # Case-5 no database no directive
            else: url_path = self.base_url # return the database connector
            return url_path
        except:            
            return self.base_url
        finally: del url_path


    async  def create_database(self, dbname:str=None, partitioned:bool=False):
        ''' Creates a new database '''
        try:
            async with httpx.AsyncClient() as client:
                r = await client.put(self.resolve_url_path(db=dbname))
            return r.json()
        except Exception: return {"status": str(Exception)}
        finally: #close connection and clean up
            await r.aclose()
            del(r)


    async  def check_for_database(self, dbname:str=None):
        ''' Checks if database exists.'''
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(self.resolve_url_path(db=dbname))
            return r.json()
        except Exception: return {"status": str(Exception)}
        finally: #close connection and clean up
            await r.aclose()
            del(r)



    async def get(self, db:str=None, _directive:str=None):
        '''Retreives a single item or a list of items based on the given directive
        ---
            applied directives: 
                _id:  retreive the item by its id 
                _all_docs: retreives an index list of items 
                _design/xx/_view/aview: retreive a list of documents by design
        '''
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(self.resolve_url_path(db=db, _directive=_directive))
            return r.json()
        except Exception: return {"status": str(Exception)}
        finally: #close connection and clean up
            await r.aclose()
            del(r)


    async def post(self, db:str=None, json:dict=None):  
        '''Create a new resource in storage.
        ---
        requires a data ditionary object with key _id
        ''' 
        r = None              
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(self.resolve_url_path(db=db), json=json)
            return r.json()
        except Exception: return {"status": str(Exception)}
        finally: 
            await r.aclose()
            del(r) #close connection and clean up

    
    async def put(self, db:str=None, json:dict=None): 
        '''Updates a resource with data provided 
        ---
        requires a data ditionary object with key _id
        ''' 
        r = None
      
        old_data = await self.get(db=db, _directive=json.get("_id"))         
        old_data.update(old_data | json)   
        
        if old_data.get("meta_data"): old_data["meta_data"]["updated"] = timestamp()
        else: pass     
        try:
            async with httpx.AsyncClient() as client:
                r = await client.put(self.resolve_url_path(db=db, _directive=f"{json.get('_id')}") , json=old_data)
            return r.json()
        except Exception: return {"status": str(Exception)}        
        finally: #close connection and clean up
            await r.aclose()
           
            del(r) 
            del(old_data)


    async def delete(self, db:str=None, _id:str=None): 
        '''Permanently removes a resource from storage.
        ---
            requires the resource _id 
        '''  
        r = None       
        data = await self.get(db=db, _directive=_id)
        try:
            async with httpx.AsyncClient() as client:
                r = await client.delete(url=self.resolve_url_path(db=db, _directive=f"{_id}?rev={data.get('_rev')}") )            
            return r.json()
        except Exception as ex:
            return {"status": str(ex)}
        finally: #close connection and clean up
            await r.aclose()
            del(r)
            del(data)

    def exit(self):
        from sys import exit
        try:
            exit()
        except Exception as e:
            return {'status': str(e)}
        finally: del(exit)
            

class RecouchManager():
    def __init__(self, local_db=None):
        self.db = local_db
        self.handler = None

    def __enter__(self):
        self.handler = Recouch(local_db=self.db)
        return self.handler

    def __exit__(self, exc_type, exec_value, exec_traceback):
        self.handler.exit()


class RedisCache():
    def __init__(self, db=None):
        self.db = db
        self.redis = aioredis.from_url("redis://localhost", encoding="utf-8", decode_responses=True) 


    async def set(self, key:str=None, val=None):
        try:
            if key and val:
                await self.redis.set(key, val, ex=60*60)
            else:
                pass
        except Exception as e:
            return str(e)
        finally:
            await self.redis.close()


    async def get(self, key:str=None):
        try:
            if key:
                value = await self.redis.get(key)
                return value
        except Exception as e:
            return str(e)
        finally:
            await self.redis.close()


    async def delete(self, key:str=None):
        try:
            if key:
                value = await self.redis.delete(key)
                return value
        except Exception as e:
            return str(e)
        finally:
            await self.redis.close()


    async def test(self):        
        await self.set("CURRENT_PAYBILL", "DDXXX-Bill-13")
        value = await self.get("CURRENT_PAYBILL")
        return value


recouch = Recouch(local_db=None)
