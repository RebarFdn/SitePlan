#rate.py

import json
import typing
import datetime
from logger import logger
from functools import lru_cache
from modules.utils import timestamp,  to_dollars
from database import Recouch, local_db

databases = { # Employee Databases
            "local":"rate-sheet", 
            "local_partitioned": False,
            "slave":"rate-sheet", 
            "slave_partitioned": False            
            }

# connection to site-projects database 
db_connection:typing.Coroutine = local_db(db_name=databases.get('local'))  


def rate_categories():
    return {
            "excavation": "Excavation",
            "steelwork": "Steelwork",
            "masonry": "Masonry",
            "carpentry": "Carpentry",
            "joinery": "Joinery",
            "painting": "Painting",
            "plumbing": "Plumbing",
            "scaffolding": "Scaffolding",
            "tiling": "Tiling",
            "welding": "Welding",
            "electrical": "electrical"
    }


async def all_rates_ref(conn:typing.Coroutine=db_connection)->list:
    rates:dict = await conn.get(_directive = "_all_docs")   
    try:            
        return  rates.get('rows')        
    except Exception as e: logger().exception(e)
    finally: del rates


async def all_rates(conn:typing.Coroutine=db_connection)->list: 
        '''Retreives a list of rate data.
        ''' 
        r = None      
        def processrates(rate):
            return rate['value']            
        try:
            r = await conn.get(_directive="_design/index/_view/document")
            return list(map(processrates,  r.get('rows', []) ))
        except Exception as e: logger().exception(e)
        finally: del(r)

 

async def get_industry_rate(id:str, conn:typing.Coroutine=db_connection)->dict:
    rate = await conn.get(_directive=id) 
    try:
        return rate
    except Exception: logger().exception(Exception)
    finally: del rate
    
#@profile(precision=2, stream=fp)
async def save_rate(data:dict=None, conn:typing.Coroutine=db_connection):      
    '''Stores a Rate Item Permanently on the Platform.'''  
    return await conn.post(json=data) 
        
#@profile(precision=2, stream=fp)
async def update_rate(data:dict=None, conn:typing.Coroutine=db_connection):
    '''Updates a Rate Item with data provided.
    --- Footnote:
            enshure data has property _id
    extra:
        updates the objects meta_data property 
        or create and stamp the meta_data field
        if missing                 
    '''
    if '_rev' in list(data.keys()): del(data['_rev'])      
    try: return await conn.put(json=data)            
    except Exception as e: logger().exception(e)
        

#@profile(precision=2, stream=fp)
async def delete_rate(id:str=None, conn:typing.Coroutine=db_connection):
        '''Permanently Remove a Rate Item from the Platform.
        ---Requires:
            name: _id
            value: string 
            inrequest_args: True
        '''        
        try: return await conn.delete(_id=id)
        except Exception as e: logger().exception(e)


class Rate:
    _id:str = None    
    meta_data:dict = {
        "created":timestamp(), 
        "created_by": None,
        "database": {"name": "rate-sheet", "partioned": False},
        }
    index:set = set()
    rate:dict = {}
    rates:list = []


    #@profile(precision=1, stream=fp)    
    def __init__(self, data:dict=None) -> None:
        self.conn = Recouch(local_db=self.meta_data.get('database').get('name'))        
        if data:
            self.data = data
            if self.data.get("_id"): self._id = self.data.get("_id")
            else: self.generate_id()
            self.meta_data.update(self.meta_data | {"_id": self._id})
            self.data['metadata'] = self.meta_data

    @property
    def model(self):
        return {
            "_id": None,            
            "title": None,
            "description": None,
            "metric": {
                "unit": None,
                "price": 0,
                "quantity":0,
                "total": 0
            },
            "imperial": {
                "unit": None,
                "price": 0,
                "quantity": 0,
                "total": 0
            },
            "state": {
                "active": False,
                "complete": False,
                "pause": False,
                "terminate": False
            },
            "event": {
                "started": None,
                "completed": None,
                "paused": [],
                "restart": [],
                "terminated": None
            },
            "assigned": False,
            "assignedto": None,
            "phase": None,
            "paid": None,
            "timestamp": 0,
            "comments": [],
            "progress": 0,
            "output": {
                "metric": 0,
                "imperial": 0
            },
            "category": None
            
            }

    #@profile(precision=1, stream=fp)
    def mount(self, data:dict=None) -> None:        
        if data:
            self.data = data
            if self.data.get("_id"): self._id = self.data.get("_id")
            else: self.generate_id()
            self.meta_data.update(self.meta_data | {"_id": self._id})
            self.data['metadata'] = self.meta_data

    # Depricated for external function all_rates_ref
    #@profile(precision=2, stream=fp)
    async def all(self):
        try:            
            return await self.conn.get(_directive = "_all_docs")            
        except Exception as e:
            return str(e)
        
    # Depricated for external function all_rates
    #@profile(precision=2, stream=fp)
    async def all_rates(self): 
        '''Retreives a list of rate data.
        ''' 
        r = None      
        def processrates(rate):
            return rate['value']            
        try:
            r = await self.conn.get(_directive="_design/index/_view/document")
            return list(map(processrates,  r.get('rows', []) ))
        except Exception as e: return str(e)
        finally: del(r)
             
    #@profile(precision=2, stream=fp)
    async def get(self, id:str=None):
        '''Retreives an indivual rate item by its Id.
        '''
        return await self.conn.get(_directive=id) 
    
    #@profile(precision=2, stream=fp)
    async def save(self):      
        '''Stores a Rate Item Permanently on the Platform.
        '''  
        return await self.conn.post(json=self.data) 
        
    #@profile(precision=2, stream=fp)
    async def update(self, data:dict=None):
        '''Updates a Rate Item with data provided.
        --- Footnote:
                enshure data has property _id
            extra:
                updates the objects meta_data property 
                or create and stamp the meta_data field
                if missing                 
        '''
        if '_rev' in list(data.keys()): del(data['_rev'])      
        try: return await self.conn.put(json=data)            
        except Exception as e: return {'error': str(e)}
        

    #@profile(precision=2, stream=fp)
    async def delete(self, id:str=None):
        '''Permanently Remove a Rate Item from the Platform.
        ---Requires:
            name: _id
            value: string 
            inrequest_args: True
        '''        
        try: return await self.conn.delete(_id=id)
        except Exception: return {"status": str(Exception)}
        

    #@profile(precision=2, stream=fp)
    async def get_elist(self):
        self.rates = await self.all()
        return self.rates

    #@profile(precision=2, stream=fp)
    def generate_id(self):
        ''' Generates a unique rate id, also updates the rate data'''        
        from modules.utils import GenerateId       
        gen = GenerateId() 
        try: self._id =  gen.name_id(ln=self.data.get('title').split(' ')[1], fn=self.data.get('title'))            
        except: self._id = gen.name_id('P', 'T')
        finally:
            self.data['_id']=self._id
            del(gen)
            del(GenerateId) # clean up
            return self._id

    #@profile(precision=2, stream=fp)
    def update_index(self, rate_id:str) -> None:
        '''Expects a unique id string ex. JD33766'''        
        self.index.add(rate_id) 

    #@profile(precision=2, stream=fp)
    @property 
    def list_index(self) -> list:
        ''' Converts set index to readable list'''
        return [item for item in self.index]
    

    async def html_table_generator(self, filter:str=None):
        rates = await self.all_rates()
        categories = {rate.get('category') for rate in rates }
        if filter:
            if filter == 'all' or filter == 'None':            
                filtered = rates
            else:
                filtered = [rate for rate in rates if rate.get("category") == filter]

            yield f"""
            <div class="flex flex-row bg-gray-300 py-3 px-4 items-inline text-center rounded">
                <span class="cursor-pointer" uk-toggle="target: #new-rate-modal"uk-icon="plus"></span>
                    <p class="mx-5">Industry Rates Index</>                
                    <span class="bg-gray-50 py-1 px-2 border rounded-full">{len(filtered)}<span>   
                      <a href><span uk-drop-parent-icon></span></a>
                    <div uk-dropdown="pos: bottom-center">
                    <ul class="uk-nav uk-dropdown-nav">
                     <li class="uk-nav-header">Filter Rates</li>
                     <li><a 
                                href="#"
                                hx-get="/rates_html_table/{'all'}"
                                hx-target="#dash-content-pane"
                                hx-trigger="click"                                 
                                >All Categories</a>
                        </li>
                        """

            for item in categories:
                yield f""" <li>
                                <a 
                                href="#"
                                hx-get="/rates_html_table/{item}"
                                hx-target="#dash-content-pane"
                                hx-trigger="click"                                 
                                >{item}</a></li>"""
                       
                        
            yield f""" </ul></div>
                    </div>
                <table class="uk-table uk-table-small uk-table-hover uk-table-divider text-teal-800">
                <thead>
                    <tr class="uk-text-primary">
                        <th>Id</th>
                        <th>Category</th>
                        <th>Title</th>
                        
                        <th>Metric Unit</th>
                        <th>Metric Rate</th>
                        <th>Imperial Unit</th>
                        <th>Imperial Rate</th>
                    </tr>
                </thead>
                <tbody> """
            for rate in filtered:
                yield f"""<tr
                            hx-get="/rate/{rate.get('_id')}"
                            hx-target="#dash-content-pane"
                            hx-trigger="click"
                            >
                        <td>{rate.get('_id')}</td>
                        <td>{rate.get('category')}</td>
                        <td>{rate.get('title')}</td>                   
                        <td>{rate.get('metric').get('unit')}</td>
                        <td class="text-blue-700">{to_dollars(rate.get('metric').get('price'))}</td>
                        <td>{rate.get('imperial').get('unit')}</td>
                        <td class="text-blue-700"> {to_dollars(rate.get('imperial').get('price'))}</td>
                    </tr>             
                    """
            yield """</tbody></table>"""
            del(filtered)
        else:
            yield f"""
            <div class="flex flex-row bg-gray-300 py-3 px-4 items-inline text-center rounded">
                <span class="cursor-pointer" uk-toggle="target: #new-rate-modal"uk-icon="plus"></span>
                    <p class="mx-5">Industry Rates Index</>                
                    <span class="bg-gray-50 py-1 px-2 border rounded-full">{len(rates)}<span>   
                      <a href><span uk-drop-parent-icon></span></a>
                    <div uk-dropdown="pos: bottom-center">
                    <ul class="uk-nav uk-dropdown-nav">
                     <li class="uk-nav-header">Filter Rates</li>
                     <li><a 
                                href="#"
                                hx-get="/rates_html_table/{'all'}"
                                hx-target="#dash-content-pane"
                                hx-trigger="click"                                 
                                >All Categories</a>
                        </li>
                    """

            for item in categories:
                yield f""" <li>
                                <a 
                                href="#"
                                 hx-get="/rates_html_table/{item}"
                                hx-target="#dash-content-pane"
                                hx-trigger="click"                                 
                                >{item}</a></li>"""
                       
                        
            yield f""" </ul></div>                  
                        
                    </div>

                <table class="uk-table uk-table-small uk-table-hover uk-table-divider text-teal-800">
                <thead>
                    <tr class="uk-text-primary">
                        <th>Id</th>
                        <th>Category</th>
                        <th>Title</th>
                        
                        <th>Metric Unit</th>
                        <th>Metric Rate</th>
                        <th>Imperial Unit</th>
                        <th>Imperial Rate</th>
                    </tr>
                </thead>
                <tbody> """
            for rate in rates:
                yield f"""<tr
                            hx-get="/rate/{rate.get('_id')}"
                            hx-target="#dash-content-pane"
                            hx-trigger="click"
                            >
                        <td>{rate.get('_id')}</td>
                        <td>{rate.get('category')}</td>
                        <td>{rate.get('title')}</td>                   
                        <td>{rate.get('metric').get('unit')}</td>
                        <td class="text-blue-700">{rate.get('metric').get('price')}</td>
                        <td>{rate.get('imperial').get('unit')}</td>
                        <td class="text-blue-700"> {rate.get('imperial').get('price')}</td>
                    </tr>             
                    """
            yield """</tbody></table>"""        
            del(rates)
            


    async def html_index_generator(self, filter:str=None):
        rates = await self.all_rates()
        categories = {rate.get('category') for rate in rates }
        if filter:
            if filter == 'all' or filter == 'None':            
                filtered = rates
            else:
                filtered = [rate for rate in rates if rate.get("category") == filter]

            yield f"""
                <div>
                <div class="flex flex-row bg-gray-300 py-3 px-4 items-inline text-center rounded relative">
                <span class="cursor-pointer" uk-toggle="target: #new-rate-modal"uk-icon="plus"></span>
                    <p class="mx-10">Industry Rates Index</p>                
                    <span class="uk-badge">{len(filtered)}</span>
                       <a href class="absolute right-0">Filter <span uk-drop-parent-icon></span></a>
                    <div uk-dropdown="pos: bottom-center">
                    <ul class="uk-nav uk-dropdown-nav">
                     <li class="uk-nav-header">Filter Rates</li>
                     <li><a 
                                href="#"
                                hx-get="/rates_html_index/{'all'}"
                                hx-target="#dash-left-pane"
                                hx-trigger="click"                                 
                                >All Categories</a>
                        </li>
                    """

            for item in categories:
                yield f""" <li>
                                <a 
                                href="#"
                                hx-get="/rates_html_index/{item}"
                                hx-target="#dash-left-pane"
                                hx-trigger="click"                                 
                                >{item}</a></li>"""
                       
                        
            yield f""" </ul>
                </div>                 
                       
                    </div>
                <ul class="uk-list uk-list-striped h-96 p-2 overflow-y-auto">
                """
        
            for rate in filtered:
                yield f"""<li>
                <div class="flex flex-col text-sm bg-gray-300 py-2 px-3 my-2 border rounded cursor-pointer hover:bg-gray-100"
                    hx-get="/rate/{rate.get('_id')}"
                    hx-target="#dash-content-pane"
                    hx-trigger="click"
                >
                <h1>{rate.get('_id')} <span class="mx-2">{rate.get('title')}</span></h1>
                <span 
                    class="inline-flex items-center gap-x-1.5 py-1 px-2 rounded-full text-xs w-auto max-w-32 font-medium bg-blue-300 text-gray-600"
                    >{rate.get('category')}
                </span></div></li>             
                """
            yield """</ul></div>       
                
                            <!-- New Rate modal -->
                <div id="new-rate-modal" uk-modal>
                    <div class="uk-modal-dialog uk-modal-body">
                        <h2 class="uk-modal-title">New Industry Rate</h2>
                        <form>

                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-large" type="text" placeholder="Rate Title" aria-label="Small" name="title">
                            </div>

                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-medium" type="text" placeholder="Description" aria-label="Medium" name="Description">
                            </div>

                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-small" type="text" placeholder="Small" aria-label="Small">
                            </div>

                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-xsmall" type="text" placeholder="X-Small" aria-label="X-Small">
                            </div>

                        </form>
                        
                        <p class="uk-text-right">
                            <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                            <button class="uk-button uk-button-primary" type="button">Save</button>
                        </p>
                    </div>
                </div>
            
            """
        else:            
            yield f"""
                <div>
                <div class="flex flex-row bg-gray-300 py-3 px-4 items-inline text-center rounded relative">
                <span class="cursor-pointer" uk-toggle="target: #new-rate-modal"uk-icon="plus"></span>
                    <p class="mx-5">Industry Rates Index</>               
                    
                     <span class="uk-badge">{len(rates)}</span>
                    <a href class="absolute right-0">Filter <span uk-drop-parent-icon></span></a>
                    <div uk-dropdown="pos: bottom-center">
                    <ul class="uk-nav uk-dropdown-nav">
                     <li class="uk-nav-header">Filter Rates</li>
                     <li><a 
                                href="#"
                                hx-get="/rates_html_index/{'all'}"
                                hx-target="#dash-left-pane"
                                hx-trigger="click"                                 
                                >All Categories</a>
                        </li>
                    """

            for item in categories:
                yield f""" <li>
                                <a 
                                href="#"
                                hx-get="/rates_html_index/{item}"
                                hx-target="#dash-left-pane"
                                hx-trigger="click"                                 
                                >{item}</a></li>"""
                       
                        
            yield f""" </ul>
                </div>                        
                        
                    </div>
                <ul class="uk-list uk-list-striped h-96 p-2 overflow-y-auto">
                """
        
            for rate in rates:
                yield f"""<li>
                <div class="flex flex-col text-sm bg-gray-300 py-2 px-3 my-2 border rounded cursor-pointer hover:bg-gray-100"
                    hx-get="/rate/{rate.get('_id')}"
                    hx-target="#dash-content-pane"
                    hx-trigger="click"
                >
                <h1>{rate.get('_id')} <span class="mx-2">{rate.get('title')}</span></h1>
                <span 
                    class="inline-flex items-center gap-x-1.5 py-1 px-2 rounded-full text-xs w-auto max-w-32 font-medium bg-blue-300 text-gray-600"
                    >{rate.get('category')}
                </span></div></li>             
                """
            yield """</ul></div>       
                
                            <!-- New Rate modal -->
                <div id="new-rate-modal" uk-modal>
                    <div class="uk-modal-dialog uk-modal-body">
                        <h2 class="uk-modal-title">New Industry Rate</h2>
                        <form>

                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-large" type="text" placeholder="Rate Title" aria-label="Small" name="title">
                            </div>

                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-medium" type="text" placeholder="Description" aria-label="Medium" name="Description">
                            </div>

                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-small" type="text" placeholder="Small" aria-label="Small">
                            </div>

                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-xsmall" type="text" placeholder="X-Small" aria-label="X-Small">
                            </div>

                        </form>
                        
                        <p class="uk-text-right">
                            <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                            <button class="uk-button uk-button-primary" type="button">Save</button>
                        </p>
                    </div>
                </div>
            
            """
       

    @property
    def categories(self):
        return {
            "excavation": "Excavation",
            "steelwork": "Steelwork",
            "masonry": "Masonry",
            "carpentry": "Carpentry",
            "joinery": "Joinery",
            "painting": "Painting",
            "plumbing": "Plumbing",
            "scaffolding": "Scaffolding",
            "tiling": "Tiling",
            "welding": "Welding",
            "electrical": "electrical"
        }

