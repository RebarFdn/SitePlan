#encoding=utf-8
#supplier.py
from modules.utils import timestamp
from modules.project import Project
from database import Recouch
from starlette.responses import JSONResponse, HTMLResponse, StreamingResponse
from starlette_login.decorator import login_required
from modules.utils import to_dollars

class Supplier:    
    suppliers:list=[]
    meta_data:dict = {
        "created": 0, 
        "database": {"name":"site-suppliers", "partitioned": False},
        }    
    def __init__(self, data:dict=None) -> None:
        self.conn = Recouch(local_db=self.meta_data.get('database').get('name'))
        self._id:str = None 
        self.data:dict = None   
        self.index:set = set()        
        if data:
            self.data = data
            if self.data.get("_id"): pass
            else: self.generate_id()

    def mount(self, data:dict=None) -> None:        
        if data:
            self.data = data
            if self.data.get("_id"): pass
            else: self.generate_id()

    async def all(self):
        try:
            r = await self.conn.get(_directive="_all_docs") 
            return r            
        except Exception as e: return str(e)
        finally: del(r)

    async def nameIndex(self):
        def processIndex(p): return p.get('key')
        try:
            r = await self.conn.get(_directive="_design/suppliers/_view/name-index") 
            return list(map( processIndex,  r.get('rows')))            
        except Exception as e: return str(e)
        finally: del(r)

    async def invoiceIdIndex(self):
        def processIndex(p): return  p.get('key')
        try:
            r = await self.conn.get(_directive="_design/project-index/_view/invoice-id") 
            return list(map( processIndex,  r.get('rows')))            
        except Exception as e: r = {'error': str(e)}
        finally: del(r)

    async def get(self, id:str=None):
        try:
            r = await self.conn.get(_directive=id) 
            return r  
        except Exception as e: return {'error': str(e)}
        finally: del(r)

    async def save(self):
        self.meta_data["created"] = timestamp()
        self.data['meta_data'] = self.meta_data
        try: return await self.conn.post( json=self.data)                        
        except Exception as e: return {'error': str(e)}
        

    async def update(self, data:dict=None):
        payload = None
        supplier = await self.get(id=data.get('_id'))        
        try:
            payload = supplier | data
            await self.conn.put(json=payload) 
            return payload           
        except Exception as e: return {'error': str(e)}
        finally: 
            del(payload)
            del(supplier)

    async def delete(self, id:str=None):
        try: return await self.conn.delete(_id=id)           
        except Exception as e: response = {'error': str(e)}
        finally:
            del(supplier)
            return response

    async def get_elist(self):
        try: s = await self.all()            
        except Exception as e: s = {'error': str(e)}
        finally: return s

    def generate_id(self):
        ''' Generates a unique supplier id, also updates the supplier data''' 
        from modules.utils import GenerateId       
        gen = GenerateId()
        ln = None 
        try:
            ln = self.data.get('name').split(' ')
            self._id =  gen.name_id(ln=ln[1], fn=self.data.get('name'))            
        except: self._id = gen.name_id('C', 'P')
        finally:
            self.data['_id']=self._id
            del(ln)
            del(gen)
            del(GenerateId)
            return self._id


    def update_index(self, data:str) -> None:
        '''  Expects a unique id string ex. JD33766'''        
        self.index.add(data) 


    @property 
    def list_index(self) -> list:
        ''' Converts set index to readable list'''
        return [item for item in self.index]
    

    async def html_index_generator(self, filter:str=None):
        suppliers = await self.nameIndex()
        locations = {supplier.get("address").get("city_parish") for supplier in suppliers }
       
        if filter:
            if filter == 'all' or filter == 'None':            
                filtered = suppliers
            else:
                filtered = [supplier for supplier in suppliers if supplier.get("address").get("city_parish") == filter]
            yield f"""
                <div>
                <div class="flex flex-row bg-gray-300 py-3 px-4 items-inline text-center rounded relative">
                <span class="cursor-pointer" uk-toggle="target: #new-supplier-modal" uk-icon="plus"></span>
                    <p class="mx-5">Suppliers Index</>                
                    <span class="uk-badge mx-5">{len(filtered)}</span> 
                    <a href class="absolute right-0">Filter <span uk-drop-parent-icon></span></a>
                    <div uk-dropdown="pos: bottom-center">
                        <ul class="uk-nav uk-dropdown-nav">
                            <li class="uk-nav-header">Filter By Location</li>
                            <li>
                                <a href="#"
                                    hx-get="/suppliers_html_index/{'all'}"
                                    hx-target="#dash-left-pane"
                                    hx-trigger="click"                                 
                                >
                                    All Parishes
                                </a>
                            </li>
                        """
            for item in locations:
                yield f"""<li><a href="#"
                                hx-get="/suppliers_html_index/{item}"
                                hx-target="#dash-left-pane"
                                hx-trigger="click"                                 
                                >{item}</a>
                            </li>
                        """ 
            yield f""" </ul></div>
                    </div>
                <ul class="uk-list uk-list-striped h-96 p-2 overflow-y-auto">
                """
            for supplier in filtered:
                yield f"""<li>
                <div class="flex flex-col text-sm bg-gray-300 py-2 px-3 my-2 border rounded cursor-pointer hover:bg-gray-100"
                    hx-get="/supplier_html/{supplier.get('_id')}"
                    hx-target="#dash-content-pane"
                    hx-trigger="click"
                >
                <h1>{supplier.get('_id')} <span class="mx-2">{supplier.get('name')}</span></h1>
                <span 
                    class="inline-flex items-center gap-x-1.5 py-1 px-2 rounded-full text-xs w-auto max-w-48 font-medium bg-blue-300 text-gray-600"
                    >{supplier.get("address").get("town")}|{supplier.get("address").get("city_parish")}
                </span></div></li>             
                """
            yield """</ul></div> """
        else:
            yield f"""
            <div>
            <div class="flex flex-row bg-gray-300 py-3 px-4 items-inline text-center rounded relative">
               <span class="cursor-pointer" uk-toggle="target: #new-supplier-modal" uk-icon="plus"></span>
                <p class="mx-5">Suppliers Index</>                
                <span class="uk-badge mx-5">{len(suppliers)}</span> 
                <a href class="absolute right-0">Filter <span uk-drop-parent-icon></span></a>
                <div uk-dropdown="pos: bottom-center">
                    <ul class="uk-nav uk-dropdown-nav">
                        <li class="uk-nav-header">Filter By Location</li>
                        <li>
                            <a href="#"
                                hx-get="/suppliers_html_index/{'all'}"
                                hx-target="#dash-left-pane"
                                hx-trigger="click"                                 
                            >
                                All Parishes
                            </a>
                        </li>
                    """
            for item in locations:
                yield f"""<li><a href="#"
                                hx-get="/suppliers_html_index/{item}"
                                hx-target="#dash-left-pane"
                                hx-trigger="click"                                 
                                >{item}</a>
                            </li>
                        """ 
            yield f""" </ul></div>
                    </div>
                <ul class="uk-list uk-list-striped h-96 p-2 overflow-y-auto">
                """
            for supplier in suppliers:
                yield f"""<li>
                <div class="flex flex-col text-sm bg-gray-300 py-2 px-3 my-2 border rounded cursor-pointer hover:bg-gray-100"
                    hx-get="/supplier_html/{supplier.get('_id')}"
                    hx-target="#dash-content-pane"
                    hx-trigger="click"
                >
                <h1>{supplier.get('_id')} <span class="mx-2">{supplier.get('name')}</span></h1>
                <span 
                    class="inline-flex items-center gap-x-1.5 py-1 px-2 rounded-full text-xs w-auto max-w-48 font-medium bg-blue-300 text-gray-600"
                    >{supplier.get("address").get("town")}|{supplier.get("address").get("city_parish")}
                </span></div></li>             
                """
            yield """</ul></div> 
                
                                <!-- modal -->
                <div id="new-supplier-modal" uk-modal>
                    <div class="uk-modal-dialog uk-modal-body">
                        <h2 class="uk-modal-title">New Supplier Registration</h2>
                        <form>
                            <div class="uk-margin">
                                <input class="uk-input uk-form-width-large" type="text" placeholder="Supplier's Name" aria-label="Small" name="name">
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



    async def supplier_html_generator(self, id:str=None):
        sp = await self.get(id=id)
        total_transactions = 0
        try:        
            yield f"""<div class="uk-container uk-container-large">
                <div class="uk-card uk-card-large uk-card-default">
                <div class="uk-card-header">
                    <div class="uk-grid-small uk-flex-middle" uk-grid>
                        <div class="uk-width-auto">
                            
                        </div>
                        <div class="uk-width-expand">
                            <h3 class="uk-card-title uk-margin-remove-bottom">{sp.get("name")}</h3>
                            <p class="uk-text-meta uk-margin-remove-top">{sp.get("address").get("town")}| {sp.get("address").get("city_parish")}</p>
                            <p class="uk-text-meta uk-margin-remove-top">Tel: {sp.get("contact").get("tel")} | Mobile: {sp.get("contact").get("mobile")} | Email: {sp.get("contact").get("email")}</p>
                            
                        </div>
                        <div class="uk-width-auto">
                        Tax Id  <span class="uk-badge">{sp.get("taxid", "")}</span>
                        </div>
                    </div>
                </div>
                <div class="uk-card-body">
                    <ul uk-accordion>
                        <li>
                            <a class="uk-accordion-title" href>Banking Info</a>
                            <div class="uk-accordion-content">
                                <p>{sp.get("account", {}).get('bank')}</p>
                            </div>
                        </li>
                        <li>
                            <a class="uk-accordion-title" href>Transaction Records</a>
                            <div class="uk-accordion-content">
                  <div class="h-96 overflow-y-auto">           
                <table class="uk-table uk-table-small uk-table-divider">
                <caption>Purchasing Activity</caption>
                <thead>
                    <tr>
                        <th>Id</th>
                        <th>Refference</th>
                        <th>Date</th>
                        <th>Amount</th>
                    </tr>
                </thead>
                <tbody>"""
            for t in sp.get("account", {}).get("transactions", []):
                total_transactions += float(t.get("amt", 0))
            
                yield f"""<tr>
                        <td>{t.get("id")}</td>
                        <td>{t.get("ref")}</td>
                        <td>{t.get("date")}</td>
                        <td>{to_dollars(t.get("amt", 0))}</td>
                    </tr>"""
                
            yield f"""  <tr><td>Transactions Total</td><td></td><td></td><td>{to_dollars(total_transactions)} </td> </tr>
            
            </tbody></table></div>  
                            </div>
                        </li>
                </ul>
                </div>
                <div class="uk-card-footer">
                    <a href="#" class="uk-button uk-button-text">More</a>
                    <p class="text-xs">Created {sp.get("meta_data", {}).get("created")}</p>
                    <p class="text-xs">Database  {sp.get("meta_data", {}).get("database")}</p>
                    
                </div>
                
                </div>
            </div>"""

            
        except Exception as e:
            yield f"""<div class="container text-sm text-center ">{str(e)}</div>"""
        finally: 
            del(sp)
            


## ROUTERS
from decoRouter import Router

supplier_router = Router()


@supplier_router.post('/supplier')
@login_required
async def createSupplier(request ):    
    '''Create a new Supplier .POST '''    
    data = await request.json() 
    sp = Supplier(data=data)
    try:
        res = await sp.save()
        print(res)
       
        return JSONResponse(sp.data)
    except Exception as e: 
        return JSONResponse({'error', str(e)})
    finally: 
        del(data)
        del(sp)
    
        

@supplier_router.get('/suppliers')
async def get_suppliers(request ):    
    '''Returns a list of Suppliers  .GET '''     
    sp = Supplier()
    try: res = await sp.all()
    except Exception as e: res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res)

@supplier_router.get('/supplier/{id}')
async def get_supplier(request ):    
    '''Returns a Single Supplier  .GET '''   
    id = request.path_params.get('id')    
    sp = Supplier()
    try: res = await sp.get(id=id)
    except Exception as e: res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res)

@supplier_router.get('/supplier_html/{id}')
async def get_supplier_html(request ):    
    '''Returns a Html Component with Supplier' info  .GET '''   
    id = request.path_params.get('id')  
    generator = Supplier().supplier_html_generator(id=id)  
    return StreamingResponse(generator, media_type="text/html")       


@supplier_router.get('/suppliers_index')
async def suppliers_name_index(request):
    '''Returns a list of Suppliers  name and tax_id ''' 
    sp = Supplier()
    try: res = await sp.nameIndex()
    except Exception as e: res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res)



@supplier_router.get('/suppliers_html_index')
async def html_index(request):
    '''Returns a list of Suppliers  name and tax_id '''     
    return StreamingResponse(Supplier().html_index_generator(), media_type="text/html")

@supplier_router.get('/suppliers_html_index/{filter}')
async def html_index_filtered(request):
    '''Returns an Html  list of Suppliers  name and tax_id ''' 
    filter = request.path_params.get('filter')    
    return StreamingResponse(Supplier().html_index_generator(filter=filter), media_type="text/html")


@supplier_router.get('/invoices')
async def invoiceIdIndex(request):
    '''Returns a list of invoice numbers and Suppliers  name'''    
    sp = Supplier()
    try:
        res = await sp.invoiceIdIndex()
        res = res[0]
    except Exception as e:  res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res) 


@supplier_router.post('/checkinvoice')
@login_required
async def checkInvoice(request):
    '''Validate and invoice'''
    tocheck = await request.json()
    p = await Project().get(tocheck.get('project_id'))
    #suppliers = set()
    #invoice_nos = set()
    invrec = []
    
    for item in p.get('account').get('records').get('invoices'):
        #suppliers.add(item.get('supplier').get('name'))
        #invoice_nos.add(item.get('invoiceno'))
        invrec.append({'supplier': item.get('supplier').get('name'),'invoiceno': item.get('invoiceno') })
    
    #result = { 'result':  tocheck.get('supplier') in suppliers and tocheck.get('invoiceno') in invoice_nos }

    resultant = { 'result':  {'supplier':tocheck.get('supplier'), 'invoiceno': tocheck.get('invoiceno')} in invrec
         }  
    
    return JSONResponse( resultant ) 


       
