# Team API Router 
import json
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from starlette_login.decorator import login_required
from decoRouter import Router
from modules.project import Project
from modules.employee import Employee
from config import TEMPLATES
from modules.utils import timestamp

router = Router()

# Employee Related routes  


@router.get('/employee/{id}')
async def api_get_employee(request):     
  return JSONResponse( await Employee().get_worker(id=request.path_params.get('id')))


@router.get('/employee_by_name/{name}')
async def api_get_employee_by_name(request):  
  #index = await Employee().get_name_index()
  return JSONResponse( await Employee().get_by_name(name=request.path_params.get('name')))



@router.get('/employee_name_index')
async def employee_name_index(request):  
  return JSONResponse( await Employee().get_name_index())

