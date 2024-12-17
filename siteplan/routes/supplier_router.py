# Team Router 
import json
from starlette.responses import JSONResponse, StreamingResponse, RedirectResponse
from starlette_login.decorator import login_required
from decoRouter import Router
from modules.project import get_project
from modules.supplier import Supplier, supplier_model, all_suppliers, get_supplier, supplier_name_index, supplier_invoice_id_index, save_supplier
from config import TEMPLATES

router = Router()


@router.post('/supplier')
@login_required
async def createSupplier(request ):    
    '''Create a new Supplier .POST '''    
    data = supplier_model()     
    async with request.form() as form:
        data['name'] = form.get('name')
        data['taxid'] = form.get('taxid')
        # Address Info
        data['address']['lot'] = form.get('lot')
        data['address']['street'] = form.get('street')
        data['address']['town'] = form.get('town')
        data['address']['city_parish'] = form.get('city_parish')
        data['address']['country'] = form.get('country')
        # Contact Info
        data['contact']['tel'] = form.get('tel')
        data['contact']['mobile'] = form.get('mobile')
        data['contact']['email'] = form.get('email')
        # Banking Info
        data['account']['bank']['branch'] = form.get('branch')
        data['account']['bank']['name'] = form.get('bank')
        data['account']['bank']['account'] = form.get('account_no')
        data['account']['bank']['account_type'] = form.get('account_type')
    try:
        await save_supplier(data=data, user=request.user.username)
        return RedirectResponse(url='/suppliers_html_index/all', status_code=302)
    except Exception as e: 
        return JSONResponse({'error', str(e)})
    finally: 
        del(data)
        
    
        

@router.get('/suppliers')
async def get_suppliers(request ):    
    '''Returns a list of Suppliers  .GET ''' 
    try: res = await all_suppliers()
    except Exception as e: res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res)
    

@router.get('/supplier/{id}')
async def get_one_supplier(request ):    
    '''Returns a Single Supplier  .GET '''        
    try: res = await get_supplier(id=request.path_params.get('id'))
    except Exception as e: res = {'error', str(e)}
    finally: 
        del(sp)
        return JSONResponse(res)
    

@router.get('/supplier_html/{id}')
async def get_supplier_html(request ):    
    '''Returns a Html Component with Supplier' info  .GET '''    
    supplier:dict = await get_supplier(id=request.path_params.get('id'))    
    total_transactions = 0.0
    if supplier["account"]["transactions"]:
        for t in supplier.get("account", {}).get("transactions", []):
            if t.get("amt", 0):
                total_transactions += float(t.get("amt", 0))
            else:
                pass
    else:
        pass
    return TEMPLATES.TemplateResponse('/supplier/supplierPage.html', {
        'request': request,
        'supplier': supplier,
        'total_transactions': total_transactions
        })       


@router.get('/suppliers_index')
async def suppliers_names_index(request):
    '''Returns a list of Suppliers  name and tax_id '''    
    try: res = await supplier_name_index()
    except Exception as e: res = {'error', str(e)}
    finally: return JSONResponse(res)


@router.get('/suppliers_html_index')
async def html_index(request):
    '''Returns a list of Suppliers  name and tax_id '''     
    filter = None    
    suppliers = await supplier_name_index()
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
    suppliers = await supplier_name_index()
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
    try:
        res = await supplier_invoice_id_index()
        res = res[0]
    except Exception as e:  res = {'error', str(e)}
    finally: return JSONResponse(res) 


@router.post('/checkinvoice')
@login_required
async def checkInvoice(request):
    '''Validate and invoice'''
    tocheck = await request.json()
    project:dict = await get_project(tocheck.get('project_id'))
    #suppliers = set()
    #invoice_nos = set()
    invrec = []    
    for item in project.get('account').get('records').get('invoices'):
        #suppliers.add(item.get('supplier').get('name'))
        #invoice_nos.add(item.get('invoiceno'))
        invrec.append({'supplier': item.get('supplier').get('name'),'invoiceno': item.get('invoiceno') })
    
    #result = { 'result':  tocheck.get('supplier') in suppliers and tocheck.get('invoiceno') in invoice_nos }

    resultant = { 'result':  {'supplier':tocheck.get('supplier'), 'invoiceno': tocheck.get('invoiceno')} in invrec
         } 
    try:
        return JSONResponse( resultant ) 
    except Exception as e: JSONResponse( {"exception": str(e)} ) 
    finally:
        del(tocheck)
        del(project)
        del(invrec)
        del(item)
        del(resultant)


       
