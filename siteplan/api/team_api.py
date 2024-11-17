# Team API Router 
import json
from starlette.responses import JSONResponse
from decoRouter import Router
from modules.employee import Employee

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

