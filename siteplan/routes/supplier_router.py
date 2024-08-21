# Team Router 
import json
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from starlette_login.decorator import login_required
from decoRouter import Router
from modules.project import Project
from modules.supplier import Supplier
from config import TEMPLATES
from modules.utils import timestamp

router = Router()



@router.post('/supplier')
@login_required
async def createSupplier(request ):    
    '''Create a new Supplier .POST '''    
    data = await request.json() 
    sp = Supplier(data=data)
    try:
        res = await sp.save()
        #print(res)
       
        return JSONResponse(sp.data)
    except Exception as e: 
        return JSONResponse({'error', str(e)})
    finally: 
        del(data)
        del(sp)
    
        

@router.get('/suppliers')
async def get_suppliers(request ):    
    '''Returns a list of Suppliers  .GET '''     
    sp = Supplier()
    try: res = await sp.all()
    except Exception as e: res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res)

@router.get('/supplier/{id}')
async def get_supplier(request ):    
    '''Returns a Single Supplier  .GET '''   
    id = request.path_params.get('id')    
    sp = Supplier()
    try: res = await sp.get(id=id)
    except Exception as e: res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res)

@router.get('/supplier_html/{id}')
async def get_supplier_html(request ):    
    '''Returns a Html Component with Supplier' info  .GET '''   
    id = request.path_params.get('id')  
    generator = Supplier().supplier_html_generator(id=id)  
    return StreamingResponse(generator, media_type="text/html")       


@router.get('/suppliers_index')
async def suppliers_name_index(request):
    '''Returns a list of Suppliers  name and tax_id ''' 
    sp = Supplier()
    try: res = await sp.nameIndex()
    except Exception as e: res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res)


@router.get('/suppliers_html_index')
async def html_index(request):
    '''Returns a list of Suppliers  name and tax_id '''     
    filter = None    
    suppliers = await Supplier().nameIndex()
    locations = {supplier.get("address").get("city_parish") for supplier in suppliers }
    response = {
            "request": request, 
            "filter": filter,
            "suppliers": suppliers,
            "locations": locations,
            
        }  
    if filter:
        if filter == 'all' or filter == 'None':            
            filtered = suppliers
        else:
            filtered = [supplier for supplier in suppliers if supplier.get("address").get("city_parish") == filter]
        response["filtered"] = filtered
    
    return TEMPLATES.TemplateResponse('/supplier/suppliersIndex.html', response )


@router.get('/suppliers_html_index/{filter}')
async def html_index_filtered(request):
    '''Returns an Html  list of Suppliers  name and tax_id ''' 
    filter = request.path_params.get('filter')    
    suppliers = await Supplier().nameIndex()
    locations = {supplier.get("address").get("city_parish") for supplier in suppliers }
    response = {
            "request": request, 
            "filter": filter,
            "suppliers": suppliers,
            "locations": locations,
            
        }  
    if filter:
        if filter == 'all' or filter == 'None':            
            filtered = suppliers
        else:
            filtered = [supplier for supplier in suppliers if supplier.get("address").get("city_parish") == filter]
        response["filtered"] = filtered
    
    return TEMPLATES.TemplateResponse('/supplier/suppliersIndex.html', response )


@router.get('/invoices')
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


@router.post('/checkinvoice')
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


       
