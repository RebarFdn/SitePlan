# products.py

from starlette.responses import JSONResponse, PlainTextResponse
from decoRouter import Router

from modules.utils import timestamp
from modules.project import logger
from database import Recouch


class Product:        
    products:list=[]    
    meta_data:dict = {
        "created": 0, 
        "database": {"name":"products-log", "partitioned": False},              
    }

    def __init__(self, data:dict=None):               
        self.conn = Recouch(local_db=self.meta_data.get('database').get('name'))
        self.index:set = set()      
        if data:
            self.meta_data["created"] = timestamp()  
            self.meta_data['properties'] = list(data.keys())          
            self.data = data
            self.data["meta_data"] = self.meta_data
            
    
    ## CRUD OPERATIONS
    async def all(self):
        try:
            r = await self.conn.get(_directive="_design/product/_view/index") 
            return r.get('rows')           
        except Exception as e:
            return str(e)
        finally: del(r)

    async def nameIndex(self):
        def processIndex(p):
            return  p.get('value')
        try:
            r = await self.all() 
            return list(map( processIndex, r))            
        except Exception as e:
            return str(e)
        finally: del(r)


    async def get(self, id:str=None):
        r = None
        try:
            r = await self.conn.get(_directive=id)
            logger.info(f'Request for Product {r.get("_id")} Completed sucessfully.')
            return r
        except Exception as e:
            logger.error(str(e))
            return str(e)
        finally: del(r)  


    async def save(self, data:dict=None):       
        logger.info('New product created ')
        return await self.conn.post( json=data )       
        

    async def update(self, data:dict=None):
        try:
            logger.info(f'Product {data.get("_id")} updated.')
            return await self.conn.put( json=data)            
        except Exception as e:
            logger.error(str(e))
            return str(e)
        

    async def delete(self, id:str=None):
        status = None
        try:
            status = await self.conn.delete(_id=id)
            return {"status": status}
        except Exception as e:
            return str(e)
        finally:
            del(status)


router = Router()


@router.post('/product')
async def newProduct(request): 
    payload = await request.json()   
    pr = Product()
    try:
        return JSONResponse( await pr.save(data=payload))
    except Exception as e:
        return JSONResponse(str(e))
    

@router.put('/product/')
async def updateProduct(request): 
    payload = await request.json()   
    pr = Product()
    try:
        old = await pr.get(id=payload.get('_id'))
        updated = old | payload
        return JSONResponse( await pr.update(data=updated))
    except Exception as e:
        return JSONResponse(str(e))
    

@router.get('/products')
async def getProductsList(request):
    pr = Product()
    try:
        return JSONResponse( await pr.all())
    except Exception as e:
        return JSONResponse(str(e))
    

@router.get('/product/{id}')
async def getProduct(request):
    id = request.path_params.get('id')
    pr = Product()
    try:
        return JSONResponse( await pr.get(id=id))
    except Exception as e:
        return JSONResponse(str(e))
    

@router.delete('/product/{id}')
async def deleteProduct(request):
    id = request.path_params.get('id')
    pr = Product()
    try:
        return JSONResponse( await pr.delete(id=id))
    except Exception as e:
        return JSONResponse(str(e))
    

@router.get('/productnames')
async def getProductNames(request):
    pr = Product()
    try:
        return JSONResponse( await pr.nameIndex())
    except Exception as e:
        return JSONResponse(str(e))
    

    
    

