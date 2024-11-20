# project_inventory_router.py
from starlette.responses import HTMLResponse, RedirectResponse
from starlette_login.decorator import login_required
from starlette.background import BackgroundTask
from decoRouter import Router
from modules.project import get_project, update_project
from modules.utils import timestamp, exception_message
from config import TEMPLATES

router = Router()


@router.get('/project_inventory/{id}')
@login_required
async def get_project_inventory(request):
    id:str = request.path_params.get('id')
    project:dict = await get_project(id=id)
    inventories:dict = project.get("inventory")
    if type(inventories) == list:
        project["inventory"] = {}
        await update_project(data=project)
    else: pass

    try:
        return TEMPLATES.TemplateResponse('/project/projectInventory.html', 
            {
                "request": request,  
                "inventories": project.get("inventory"),               
                "project": {
                    "_id": project.get("_id"),
                    "name": project.get("name")                    
                    }
            })
    except Exception as e:
        return HTMLResponse(exception_message(message=str(e), level='warning'))
    finally:
        del(id)        
        del(project)




