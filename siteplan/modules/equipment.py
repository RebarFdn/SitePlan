#modeler.py
#import aiohttp
import httpx as  requests
from starlette.responses import  JSONResponse
from modules.utils import GenerateId, timestamp


class Equipment(    
    
):
    
    equipments:list=[]
    
    def __init__(self, data:dict=None) -> None:
        self._id:str = None    
        self.meta_data:dict = {"created":timestamp(), "database": "site-tools", "img_url": ""}
        self.index:set = set()
        self.equipment:dict = {}
        if data:
            self.data = data
            if self.data.get("_id"):
                pass
            else:
                self.generate_id()
          


    async def mount(self, data:dict=None) -> None:        
        if data:
            self.data = data
            if self.data.get("_id"):
                pass
            else:
                self.generate_id()
            await self.setup


    async def all(self):
        try:
            r = requests.get(f"{self.db_con}_all_docs") 
            return r.json()            
        except Exception as e:
            return {'error': str(e)}
        finally: del(r)

    async def nameIndex(self):
        def processIndex(p):
            return  p.get('value')
        try:
            r = requests.get(f"{self.db_con}_design/equipments-index/_view/name-view") 
            return list(map( processIndex,  r.json().get('rows')))            
        except Exception as e:
            {'error': str(e)}
        finally: del(r)


    async def get(self, id:str=None):
        try:
            r = requests.get(f"{self.db_con}{id}") 
            return r.json()  
        except Exception as e:
            {'error': str(e)}
        finally: del(r)


    async def save(self):  
        await self.setup                    
        res = requests.post(f"{self.db_con}", json=self.data)
        return res.json()
        

    async def update(self, data:dict=None):
        if '_rev' in list(data.keys()):
            del(data['_rev'])
            

        equipment = requests.get(f"{self.db_con}{data.get('_id')}").json()
        payload = equipment | data
        try:
            requests.put(f"{self.db_con}{data.get('_id')}", json=payload)
            return payload
        except Exception as e:
            return {'error': str(e)}
        finally:
            del(data) ; del(equipment); del(payload)


    async def delete(self, id:str=None):
        equipment = await self.get(id=id)
        try:
            requests.delete(f"{self.db_con}{id}?rev={equipment['_rev']}")
            return {"status": f"equipment with id {id} DELETED"}
        except Exception as e:
            return {'error': str(e)}
        finally:
            del(equipment)


    async def get_elist(self):
        try:
            s = await self.all()
            return s
        except Exception as e:
            return {'error': str(e)}
        finally: del(s)


    def generate_id(self):
        ''' Generates a unique equipment id, also updates the equipment data''' 
        gen = GenerateId()
        try:
            ln = self.data.get('name').split(' ')
            self._id =  gen.name_id(ln=ln[1], fn=self.data.get('name'))
            
        except:
            self._id = gen.name_id('C', 'P')
        finally:
            self.data['_id']=self._id
            return self._id

    @property
    def db_con(self):
        return self.conn(db=self.meta_data.get('database'))


    def update_index(self, data:str) -> None:
        '''  Expects a unique id string ex. JD33766'''        
        self.index.add(data) 


    @property 
    def list_index(self) -> list:
        ''' Converts set index to readable list'''
        return [item for item in self.index]


    ## equipment ACCOUNTING 

    async def handleTransaction(self, id:str=None, data:dict=None):
        pass

    @property
    async def setup(self):
        self.data['hireage'] = []
        self.data['service'] = []
        self.data['runtime'] = {'unit': 'hrs', 'value': 0}
        if self.data.get('power') == 'petrol':
            self.data['petrol'] = '90 Gas'
        else: pass
        self.data['meta_data'] = self.meta_data

# Create     
async def newTool(request):
    try:
        data = await request.json() 
        e = Equipment(data=data)   
        res = await e.save()    
        return JSONResponse({"status": res})
    except Exception as er:
        return JSONResponse({'error': str(er)})
    finally: del(e); del(res)

# Retreive
async def getTool(request):
    try:
        id = request.path_params.get('id')
        e = Equipment()
        data = await e.get(id=id)
        return JSONResponse(data)
    except Exception as er:
        return JSONResponse({'error': str(er)})
    finally: del(id); del(e); del(data)

async def getTools(request):
    try:      
        e = Equipment()
        data = await e.nameIndex()
        return JSONResponse(data)
    except Exception as er:
        return JSONResponse({'error': str(er)})
    finally: del(e); del(data)

# Update
async def updateTool(request):
    data = await request.json()
    e = Equipment()
    try:
        res = await e.update(data=data)
        return JSONResponse(res)
    except Exception as er:
        return JSONResponse({'error': str(er)})
    finally: del(res); del(e); del(data)

# Delete
async def deleteTool(request):
    id = request.path_params.get('id')
    e = Equipment()
    try:
        res = await e.delete(id=id)
        return JSONResponse(res)
    except Exception as er:
        return JSONResponse({'error': str(er)})
    finally: del(res); del(e); del(id)
    

    



            

    



""" TEST
data = {
    "name":"90lb Jackhammer",   
    "serial":"",
    "model":"",
    "brand":"Dewalt",
    "power": "electric",


}      

p = equipment(data=data)


print()
print(p.data)

"""