# project_inventory_router.py
from typing import List
from starlette.responses import HTMLResponse, RedirectResponse
from starlette_login.decorator import login_required
from starlette.background import BackgroundTask
from decoRouter import Router
from modules.project import ( get_project, update_project, save_purchase_order, 
                             get_purchase_order, change_purchase_order, 
                             delete_purchase_order, get_all_purchase_orders,
                             add_purchase_order_item)
from modules.purchase_order import PurchaseItem, PurchaseOrder, processOrder
from modules.utils import timestamp, exception_message
from config import TEMPLATES
from flagman import Flagman

router = Router()

# New Orders 
@router.post('/new_purchaseorder/{id}')
async def new_purchase_order(request):
    id=request.path_params.get('id')
    async with request.form() as form:
        location = form.get('location')
        purchase_order:PurchaseOrder = PurchaseOrder(
            title= form.get('title'),
            site= form.get('site'),
            location= location.removeprefix('(').removesuffix(')'),
            date= timestamp(form.get('date'))

            )
    await save_purchase_order(id=id, purchase_order=purchase_order)
    try:
        _order = await get_purchase_order(id=id, order_id=purchase_order.id)    
    
        return TEMPLATES.TemplateResponse('/project/purchasing/purchaseOrder.html',
            {'request': request, 'project':{'_id': id},'order': _order})
    except Exception as e:
        Flagman(title='Network Get Purchaseorder', message=str(e)).send
    finally:
        del _order    


# Add Item to Order
@router.post("/add_orderitem/{project_id}/{order_id}")
async def add_order_item(request):
    project_id=request.path_params.get('project_id')
    order_id=request.path_params.get('order_id')
    async with request.form() as form:
        order_item:PurchaseItem = PurchaseItem(
            item_no= 1,
            description= form.get('description'),
            quantity= float(form.get('quantity')),
            unit= form.get('unit')
            )
    purchase_order:PurchaseOrder = await add_purchase_order_item(id=project_id, order_id=order_id, item=order_item)
    try:
        return TEMPLATES.TemplateResponse('/project/purchasing/orderItemsIndex.html',
            {'request': request, 'project': {'_id': project_id}, 'order': purchase_order,})
    except Exception as e:
        Flagman(title='Network Add Order Item', message=str(e)).send
    finally:
        del project_id
        del order_id
        del purchase_order
        del form
        




# All Orders 
@router.get('/purchaseorders/{id}')
async def get_purchaseorders(request):
    id=request.path_params.get('id')
    project_orders = await get_all_purchase_orders(id=id) 
    
    try:
        return TEMPLATES.TemplateResponse('/project/purchasing/purchaseOrderIndex.html',
            {'request': request, 'project': project_orders})
    except Exception as e:
        Flagman(title='Network Get Purchaseorder', message=str(e)).send
    finally:
        del project_orders

  
# Single Order 
@router.get('/purchaseorder/{id}/{order_id}')
async def get_purchaseorder(request):

    _order = await get_purchase_order(id=request.path_params.get('id'), order_id=request.path_params.get('order_id')) 
    
    try:
        return TEMPLATES.TemplateResponse('/project/purchasing/purchaseOrder.html',
            {'request': request, 'project':{'_id': request.path_params.get('id')},'order': _order})
    except Exception as e:
        Flagman(title='Network Get Purchaseorder', message=str(e)).send
    finally:
        del _order    


# Delete Order 
@router.delete('/purchaseorder/{id}/{order_id}')
async def delete_purchaseorder(request):
    id=request.path_params.get('id')
    await delete_purchase_order(id=id, order_id=request.path_params.get('order_id')) 
    
    try:
        project_orders = await get_all_purchase_orders(id=request.path_params.get('id')) 
        return TEMPLATES.TemplateResponse('/project/purchasing/ordersIndex.html',
            {'request': request, 'project': project_orders})
        
    except Exception as e:
        Flagman(title='Network Get Purchaseorder', message=str(e)).send
    finally:
        del id    



# Resolve Order
@router.post("/resolve_purchaseorder/{project_id}/{order_id}/{flag}")
async def resolve_purchaseorder(request):
    project_id=request.path_params.get('project_id')
    order_id=request.path_params.get('order_id')
    flag=request.path_params.get('flag')
    project:dict = await get_project(id=project_id)
    purchase_order = [item for item in project['account']['records']["purchase_orders"] if item.get('id') == order_id][0]
    if flag == 'close':
        purchase_order['resolved'] = True
    else:
        purchase_order['resolved'] = False

    await update_project(data=project)
    try:
        _order = processOrder(purchase_order)
        return TEMPLATES.TemplateResponse('/project/purchasing/purchaseOrder.html',
            {'request': request, 'project':{'_id': project_id},'order': _order})
    except Exception as e:
        Flagman(title='Network Resolve Purchaseorder', message=str(e)).send
    finally:
        del project
        del purchase_order 

