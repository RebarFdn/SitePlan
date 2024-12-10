# project_inventory_router.py
from starlette.responses import HTMLResponse, RedirectResponse
from starlette_login.decorator import login_required
from starlette.background import BackgroundTask
from decoRouter import Router
from modules.project import get_project, update_project
from modules.inventory import InventoryItem, Supplier, stock_material, get_material_inventory, get_material_usage
from modules.utils import timestamp, exception_message
from config import TEMPLATES

router = Router()


@router.get('/project_inventory/{id}')
@login_required
async def get_project_inventory(request):
    id:str = request.path_params.get('id')
    project:dict = await get_project(id=id)
    invoices = project.get('account').get('records').get('invoices')
    inventory = project.get("inventory")
    if type(inventory) == list:
        project["inventory"] = {}        
    else: pass
    for item in invoices:
        supplier:Supplier = Supplier(name=item.get('supplier').get('name'))
        for inv in item.get('items'):
            p = InventoryItem(
                ref= item.get('invoiceno'),
                name=inv.get('description'), 
                amt=float(inv.get('quantity')), 
                unit= str(inv.get('unit')),
                stocking_date=str(item.get('datetime')),
                supplier=supplier)
            invts = stock_material(item=p.model_dump(), inventories=inventory)    

    try:
        await update_project(data=project)
        return TEMPLATES.TemplateResponse('/project/projectInventory.html', 
            {
                "request": request, 
                "project": {
                    "_id": project.get("_id"),
                    "name": project.get("name"),
                    "inventories": inventory,
                    "invoices": invoices
                                     
                    }
            })
    except Exception as e:
        return HTMLResponse(exception_message(message=str(e), level='warning'))
    finally:
        del(id)        
        del(project)




