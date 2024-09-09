# Team Router 
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

@router.post('/newworker')
@login_required
async def new_worker(request):
    payload = {}
    try:
        async with request.form() as form:            
            payload['name'] = form.get('name')
            payload['oc'] = form.get('oc')
            payload['sex'] = form.get('sex')
            payload['dob'] = form.get('dob')
            payload['height'] = form.get('height')
            payload['identity'] = form.get('identity')
            payload['id_type'] = form.get('id_type')
            payload['trn'] = form.get('trn')
            payload['occupation'] = form.get('occupation')
            payload['rating'] = form.get('rating')
            payload['imgurl'] = ""
            payload['address'] = {
                'lot': form.get('lot'),
                'street': form.get('street'),
                  'town': form.get('town'),
                   'city_parish': form.get('city_parish')
                  
                
                }
            payload['contact'] = {
                'tel': form.get('tel'),
                'mobile': form.get('mobile'),
                'email': form.get('email')
                
            }
            payload['account'] = {
                "bank": {
                "name": form.get('bank'),
                "branch": form.get('bank_branch'),
                "account": form.get('account_no'),
                "account_type": form.get('account_type')
                },
                "payments": [],
                "loans": []
                
            }
            payload["nok"] = {
                "name": form.get('kin_name'),
                "relation": form.get('kin_relation'),
                "address": form.get('kin_address'),
                "contact":  form.get('kin_contact')
            }
            payload[ "tasks"] = []
            payload["jobs"] = []
            payload["days"] =  []            
            payload["state"] = {
                "active": True,
                "onleave": False,                
                "terminated": False
            },
            payload["event"] = {
                "started": None,
                "onleave":[] ,
                "restart": [],
                "terminated": None,
                "duration": 0
            },
            payload["reports"] = []
            
        ne = await Employee().save(data = payload)   

              
        return HTMLResponse(f"""<p class="bg-blue-800 text-white text-sm font-bold py-3 px-4 mx-5 my-2 rounded-md">{ne }</p>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(payload)
        

@router.get('/team')
async def team(request): 
    return StreamingResponse(Employee().team_index_generator(), media_type="text/html")


@router.get('/team/{id}')
async def team_member(request): 
    id=request.path_params.get('id')
    e = await Employee().get_worker(id=request.path_params.get('id')) 
    jobs = []
    tasks = []
    async def get_jobs_details(job_id):
        if '-' in job_id:
            idd = job_id.split('-')
            project = await Project().get(id=idd[0])
            _job = [job for job in project.get('tasks') if job.get('_id') == job_id]
            if len(_job) > 0:
                _job = _job[0]
                _tasks = [task for task in _job.get('tasks') if task.get('_id') in e.get('tasks')]
                if len(_tasks) > 0:
                    for task in _tasks:
                        tasks.append(task)

                return  {
                        "project": project.get('name'),
                        "job_id": _job.get('_id'),
                        "title": _job.get('title')
                    }
            else:
                return None
        else:
            return None
        
    for item in e.get('jobs', []):
        jobs_item = await get_jobs_details(job_id=item)
        if jobs_item:
            jobs.append(
               jobs_item
                 
                 )
    if len(jobs) > 0:
        e['jobs'] = jobs
    
    if len(tasks) > 0:
        e['tasks'] = tasks

    return TEMPLATES.TemplateResponse(
        '/employee/employeePage.html', 
        {
            "request": request, 
            "id": id,
            "employee": await Employee().get_worker_info(id=request.path_params.get('id')) 
        })



@router.get('/project_team/{id}')
async def project_team_member(request): 
    id=request.path_params.get('id')
    e = await Employee().get_worker(id=request.path_params.get('id')) 
    jobs = []
    tasks = []
    async def get_jobs_details(job_id):
        if '-' in job_id:
            idd = job_id.split('-')
            project = await Project().get(id=idd[0])
            _job = [job for job in project.get('tasks') if job.get('_id') == job_id]
            if len(_job) > 0:
                _job = _job[0]
                _tasks = [task for task in _job.get('tasks') if task.get('_id') in e.get('tasks')]
                if len(_tasks) > 0:
                    for task in _tasks:
                        tasks.append(task)

                return  {
                        "project": project.get('name'),
                        "job_id": _job.get('_id'),
                        "title": _job.get('title')
                    }
            else:
                return None
        else:
            return None
        
    for item in e.get('jobs', []):
        jobs_item = await get_jobs_details(job_id=item)
        if jobs_item:
            jobs.append(
               jobs_item
                 
                 )
    if len(jobs) > 0:
        e['jobs'] = jobs
    
    if len(tasks) > 0:
        e['tasks'] = tasks

    return TEMPLATES.TemplateResponse(
        '/employee/projectEmployeePage.html', 
        {
            "request": request, 
            "id": id,
            "employee": await Employee().get_worker_info(id=request.path_params.get('id')) 
        })

  

@router.get('/team_json/{id}')
async def team_json(request):  
  return JSONResponse( await Employee().get_worker(id=request.path_params.get('id')))


@router.get('/team_by_name/{name}')
async def team_by_name(request):  
  #index = await Employee().get_name_index()
  return JSONResponse( await Employee().get_by_name(name=request.path_params.get('name')))



@router.get('/team_name_index')
async def team_name_index(request):  
  return JSONResponse( await Employee().get_name_index())

 
@router.get('/employee_info/{id}')
async def employee_info(request):   
    #employee = await Employee().get_worker_info(id=request.path_params.get('id')) 
   
    return TEMPLATES.TemplateResponse(
        '/employee/employeeInfo.html', 
        {
            "request": request , 
            "employee": await Employee().get_worker_info(id=request.path_params.get('id')) 
            }
    )



@router.get('/employee_jobs/{id}')
async def employee_jobs(request):   
    employee = await Employee().get_worker(id=request.path_params.get('id')) 
    jobs = []
   
    async def get_jobs_details(job_id):
        if '-' in job_id:
            idd = job_id.split('-')
            project = await Project().get(id=idd[0])
            a_job = [job for job in project.get('tasks') if job.get('_id') == job_id]
            if len(a_job) > 0:
                a_job = a_job[0]           
                return  {
                        "project": project.get('name'),
                        "job_id": a_job.get('_id'),
                        "title": a_job.get('title')
                    }
            else:
                return  {
                        "project": project.get('name'),
                        "job_id": None,
                        "title": None
                    }

        else:
            return None
        
    for item in employee.get('jobs', []):
        jobs_item = await get_jobs_details(job_id=item)
        if jobs_item:
            jobs.append(
               jobs_item
                 
                 )
    if len(jobs) > 0:
        employee['jobs'] = jobs
    
    
    return TEMPLATES.TemplateResponse(
        '/employee/employeeJobsInterface.html', 
        {"request": request , "jobs": employee.get('jobs', [])}
    )



@router.get('/employee_tasks/{id}')
async def employee_tasks(request):   
    employee = await Employee().get_worker(id=request.path_params.get('id')) 
    jobs = []
    tasks = []
    async def get_jobs_details(job_id):
        if '-' in job_id:
            idd = job_id.split('-')
            project = await Project().get(id=idd[0])
            a_job = [job for job in project.get('tasks') if job.get('_id') == job_id][0]
            e_tasks = [task for task in a_job.get('tasks') if task.get('_id') in employee.get('tasks')]
            if len(e_tasks) > 0:
                for etask in e_tasks:
                    tasks.append(etask)
           
            return  {
                    "project": project.get('name'),
                    "job_id": a_job.get('_id'),
                    "title": a_job.get('title')
                }
        else:
            return None
        
    for item in employee.get('jobs', []):
        jobs_item = await get_jobs_details(job_id=item)
        if jobs_item:
            jobs.append(
               jobs_item
                 
                 )
    if len(jobs) > 0:
        employee['jobs'] = jobs

    if len(tasks) > 0:
        employee['tasks'] = tasks
    
    
    return TEMPLATES.TemplateResponse(
        '/employee/employeeTasksInterface.html', 
        {"request": request , "tasks": employee.get('tasks', [])}
    )


@router.get('/employee_days/{id}')
async def employee_days(request):   
    employee = await Employee().get_worker(id=request.path_params.get('id')) 
    return TEMPLATES.TemplateResponse(
        "/employee/employeeDaysworkIndex.html",
        {"request": request, "employee": {"days": employee.get('days') }, "id":request.path_params.get('id')})



@router.get('/employee_account/{id}')
async def employee_account(request):   
    employee = await Employee().get_worker(id=request.path_params.get('id')) 
    account = employee.get('account', [])
    account['_id'] = request.path_params.get('id')
    return TEMPLATES.TemplateResponse(
        '/employee/employeeAccountInterface.html', 
        {
            "request": request , 
            "account": account, 
            "employee": {
                "_id": employee.get('_id')
            }
        }
    )



@router.get('/employee_reports/{id}')
async def employee_reports(request):   
    employee = await Employee().get_worker(id=request.path_params.get('id')) 
    account = employee.get('account', [])
    account['_id'] = request.path_params.get('id')
    return TEMPLATES.TemplateResponse(
        '/employee/employeeReports.html', 
        {
            "request": request , 
            "reports": employee.get('reports', []), 
            "id": request.path_params.get('id')
        }
    )



@router.post('/upload_employee_profile/{id}')
async def upload_employee_profile(request):
    from PIL import Image
    from io import BytesIO
    from config import PROFILES_PATH, Path

    id=request.path_params.get('id')
    employee = await Employee().get_worker(id=id) 
    profile_path = Path.joinpath(PROFILES_PATH, f"{id}.png")
    async with request.form() as form:
        filename = form["profile"].filename
        contents = await form["profile"].read()
    img = Image.open(BytesIO(contents))
    img.save(profile_path)
    img.close()
    
    return HTMLResponse(f"""<div  class="uk-width-auto">
                    
                    <img class="uk-border-square" width="86" height="86" src="{ employee.get('imgurl') }" alt="Avatar">
                    <span class="text-center text-xs">{ employee.get('oc')}</span>
                </div>""")


@router.get('/analytics')
async def analytics(request):
    t = f""" 
    <a class="uk-button uk-button-default" href="#modal-sections" uk-toggle>Open</a>

<div id="modal-sections" uk-modal>
    <div class="uk-modal-dialog">
        <button class="uk-modal-close-default" type="button" uk-close></button>
        <div class="uk-modal-header">
            <h2 class="uk-modal-title">Modal Title</h2>
        </div>
        <div class="uk-modal-body">
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
        </div>
        <div class="uk-modal-footer uk-text-right">
            <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
            <button class="uk-button uk-button-primary" type="button">Save</button>
        </div>
    </div>
</div>
    
    <table class="uk-table uk-table-divider">
    <thead>
        <tr>
            <th>Table Heading</th>
            <th>Table Heading</th>
            <th>Table Heading</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Table Data</td>
            <td>Table Data</td>
            <td>Table Data</td>
        </tr>
        <tr>
            <td>Table Data</td>
            <td>Table Data</td>
            <td>Table Data</td>
        </tr>
        <tr>
            <td>Table Data</td>
            <td>Table Data</td>
            <td>Table Data</td>
        </tr>
    </tbody>
</table>
"""
    return HTMLResponse(t)