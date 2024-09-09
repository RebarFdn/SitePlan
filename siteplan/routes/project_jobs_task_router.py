## Project router
# This route handles all project related requests 
import hashlib 
import datetime
from json import ( loads, dumps )
from asyncio import sleep
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from starlette_login.decorator import login_required
from decoRouter import Router
from modules.project import Project
from modules.employee import Employee
from modules.utils import today, timestamp, to_dollars
from modules.unit_converter import convert_unit, convert_price_by_unit
from config import TEMPLATES
from database import RedisCache


router = Router()

# Output:
# jul 30 2024

@router.get('/update_project_job_state/{id}/{state}')
@login_required
async def update_project_job_state(request):
    id = request.path_params.get('id')
    status = request.path_params.get('state')
    idd = id.split('-')
    current_paybill =  await RedisCache().get(key="CURRENT_PAYBILL")
    categories = set()
    roles = set()
    p = await Project().get(id=idd[0])

    for task_rate in p.get("rates"): # Loads job categories
        categories.add(task_rate.get('category'))

    for worker in p.get("workers"): # Loads job roles
        roles.add(worker.get('value').get('occupation'))

    jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}

    crew_members = len(job.get('crew').get('members'))
    project_phases = Project().projectPhases.keys()

    def set_state(state):
        if state == None:
            pass
        elif state == "active":
            job['state'] = {'active': True, 'complete': False, 'pause': False, 'terminate': False}
            job['event']['started'] = timestamp()            
        elif state == "completed":
            job['state'] = {'active': False, 'complete': True, 'pause': False, 'terminate': False}
            job['event']['completed'] = timestamp()
            job['progress'] = 100
        elif state == "paused":
            job['state'] = {'active': False, 'complete': False, 'pause': True, 'terminate': False}
            job['event']['paused'].append(timestamp())
        elif state == "resume":
            job['state'] = {'active': True, 'complete': False, 'pause': False, 'terminate': False}
            job['event']['restart'].append(timestamp())

        elif state == "terminated":
            job['state'] = {'active': False, 'complete': False, 'pause': False, 'terminate': True}
            job['event']['terminated'] = timestamp()
        else:
            pass

        result = {
            "active": f"""<span class="badge badge-success">Active {job['event']}</span>""",
            "completed": f"""<span class="badge badge-primary">Completed {job['event']}</span>""",
            "paused": f"""<span class="badge badge-secondary">Paused {job['event']}</span>""",
            "resume": f"""<span class="badge badge-success">Restarted {job['event']}</span>""",

            "terminated": f"""<span class="badge badge-error">Terminated {job['event']}</span>""",

        }        
        return result.get(state)
    job_state = set_state(status)
    await Project().update(data=p)
    def test_func(a:str=None):
        return f"tested {a}"
    data = {
            "request": request, 
            "p": {
                "name": p.get('name'),
                "rates": p.get('rates'),
                "workers": p.get('workers')

            }, 
            "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill,          
            "test_func": test_func,
            "categories": list(categories),
            "job_roles": list(roles)

        }
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobPage.html', 
        {
            "request": request, 
            "p": {
                "name": p.get('name'),
                "rates": p.get('rates'),
                "workers": p.get('workers')

            }, 
            "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill,          
            "test_func": test_func,
            "categories": list(categories),
            "job_roles": list(roles)

        }) 



@router.get('/project_job/{id}')
async def project_job(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = Project()
    current_paybill =  await RedisCache().get(key="CURRENT_PAYBILL")
    categories = set()
    roles = set()
    
    p = await project.get(id=idd[0])

    for task_rate in p.get("rates"): # Loads job categories
        categories.add(task_rate.get('category'))

    for worker in p.get("workers"): # Loads job roles
        roles.add(worker.get('value').get('occupation'))
    

    jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    crew_members = len(job.get('crew').get('members'))
    job_progress = sum([ float(task.get('progress')) for task in job.get('tasks', []) ])
    project_phases = project.projectPhases.keys()
    if len(job.get('tasks')) > 0:
        job['progress'] = round(job_progress / len(job.get('tasks')), 2)
    else:
        pass
    p['activity_log'].append(
                                {
                                    "id": timestamp(),
                                    "title": f"Auto Update to Job {job.get('_id')}",
                                    "description": f"""Job {job.get('title')} Progress was automatically updated to {job.get('progress') }% by SYSTEM_AUTO_UPDATE """
                                }

                            )   
    await Project().update(data=p)
    def test_func(a:str=None):
        return f"tested {a}"
    
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobPage.html', 
        {
            "request": request, 
            "p": {
                "name": p.get('name'),
                "rates": p.get('rates'),
                "workers": p.get('workers')

            }, 
            "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill,          
            "test_func": test_func,
            "categories": list(categories),
            "job_roles": list(roles)

        }) 




@router.get('/project_job_home/{id}')
async def project_job_home(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = Project()
    current_paybill =  await RedisCache().get(key="CURRENT_PAYBILL")
    categories = set()
    roles = set()
    
    p = await project.get(id=idd[0])

    for task_rate in p.get("rates"): # Loads job categories
        categories.add(task_rate.get('category'))

    for worker in p.get("workers"): # Loads job roles
        roles.add(worker.get('value').get('occupation'))
    

    jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    crew_members = len(job.get('crew').get('members'))
    job_taskscost = []
    for task in job.get('tasks', []):
        # convert imperial units and quantities
        converter = convert_unit(unit=task.get('metric').get('unit'), value=task.get('metric').get('quantity'))
        price_converter = loads(dumps(convert_price_by_unit(unit=task.get('metric').get('unit'), value=float(task.get('metric').get('price', 0.01)))))
        task['imperial']['unit'] = converter.get('unit')
        task['imperial']['quantity'] = converter.get('value')
        task['imperial']['price'] = price_converter.get('value')
        #TODO set a price converter as per unit
        task['imperial']['total'] = task.get('imperial').get('quantity', 0) * task.get('imperial').get('price', 0)

        if task.get('metric').get('total'):
            job_taskscost.append(float(task.get('metric').get('total')) )
        else: 
            pass
    project_phases = project.projectPhases.keys()
    job['cost']['task'] = sum(job_taskscost)
    job['cost']['contractor'] = job['cost']['task'] * (int(job.get('fees').get('contractor')) / 100)
    job['cost']['misc'] = job['cost']['task'] * (int(job.get('fees').get('misc')) / 100)
    job['cost']['insurance'] = job['cost']['task'] * (int(job.get('fees').get('insurance')) / 100)
    job['cost']['overhead'] = job['cost']['task'] * (int(job.get('fees').get('overhead')) / 100)
    job_fees = [job['cost']['contractor'], job['cost']['misc'], job['cost']['insurance'],
                job['cost']['overhead']]
    job['cost']['total']['fees'] = sum(job_fees)
    job['cost']['total']['metric'] = sum(job_fees) +  job['cost']['task']
    p['activity_log'].append(
                                {
                                    "id": timestamp(),
                                    "title": f"Auto Update to Job {job.get('_id')}",
                                    "description": f"""Job {job.get('title')} Costs fields were automatically updated 
                                    to {job.get('cost') } Job Tasks Imperial fields [unit, quantity, price, total] were also 
                                    updated by SYSTEM_AUTO_UPDATE """
                                }

                            ) 
    await Project().update(data=p)
    return TEMPLATES.TemplateResponse(
        '/project/job/jobHomeConsole.html',
        {
            "request": request, 
            "p": {
                "name": p.get('name'),
                "rates": p.get('rates'),
                "workers": p.get('workers')

            }, 
            "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill, 
            "categories": list(categories),
            "job_roles": list(roles),
            "job_taskscost": job_taskscost 

        }) 


@router.get('/project_job_tasks/{id}')
async def project_job_tasks(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = Project()
    current_paybill =  await RedisCache().get(key="CURRENT_PAYBILL")
    categories = set()
    roles = set()
    
    p = await project.get(id=idd[0])

    for task_rate in p.get("rates"): # Loads job categories
        categories.add(task_rate.get('category'))

    for worker in p.get("workers"): # Loads job roles
        roles.add(worker.get('value').get('occupation'))
    

    jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    crew_members = len(job.get('crew').get('members'))
    project_phases = project.projectPhases.keys()
    #generator = Project().html_job_page_generator(id=id)
    def test_func(a:str=None):
        return f"tested {a}"
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobTasks.html',
        {
            "request": request, 
            "p": {
                "name": p.get('name'),
                "rates": p.get('rates'),
                "workers": p.get('workers')

            }, 
            "job": job, 
            "crew_members": crew_members,
            "project_phases": project_phases,  
            "current_paybill": current_paybill,          
            "test_func": test_func,
            "categories": list(categories),
            "job_roles": list(roles)

        }) 



@router.get('/project_jobcrew/{id}')
async def project_jobcrew(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = await Project().get(id=idd[0])
    

    jb = [j for j in  project.get('tasks') if j.get('_id') == id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    crew_ratings_tally = sum( [ int(member.get('value', {}).get('rating', 0)) for member in job.get('crew', {}).get('members', [])])
    crew_members = len(job.get('crew', {}).get('members', []))
    job['crew']['rating'] = round(crew_ratings_tally / crew_members, 2)


    return TEMPLATES.TemplateResponse(
        '/project/job/projectJobCrew.html', 
        {
            "request": request,             
            "job": job, 
            "crew": job.get('crew', {}), 
            "crew_members": crew_members  

        }) 



@router.delete('/jobcrew_member/{id}')
async def delete_jobcrew_member(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    job_id = idd[0]
    crew_id = idd[1]
    project = await Project().get(id=id.split('-')[0])    
    index = 0
    jb = [j for j in  project.get('tasks') if j.get('_id') == job_id ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    for member in job.get('crew').get('members'):
        if member.get('id') == crew_id:
            index = job.get('crew').get('members').index(member)
    del(job['crew']['members'][index])
    project['activity_log'].append(
            {
                "id": timestamp(),
                "title": f"Remove Member From Job Crew",
                "description": f"""Crew member {crew_id} was removed from the crew of Job {job.get('title')} by {request.user.username} """
            }

    ) 
    await Project().update(data=project)
    res = HTMLResponse(f"""<div>{id}---{index}</div>""")
    return RedirectResponse(url=f'/project_jobcrew/{ job_id }', status_code=302)




@router.post('/add_project_job/{id}')
async def add_project_job(request):
    id = request.path_params.get('id')
    job = {"project_id": id}
    try:
        async with request.form() as form:    
            job["title"] = form.get("title")    
            job["description"] = form.get("description")    
            job["projectPhase"] = form.get("project_phase")    
            job["crew"] = {
                    "name": form.get("crew_name"),
                    "rating": 0,
                    "members": [],
                    "event": {
                    "created": form.get("date"),
                    "activated": None,
                    "terminated": None
                    },
                    "state": {
                    "enabled": True,
                    "active": False,
                    "terminated": False
                    }
                }
            job["worker"] = form.get("worker")
            job["tasks"] = []
            job["event"] = {
                    "started": 0,
                    "completed": 0,
                    "paused": [],
                    "restart": [],
                    "terminated": 0,
                    "created": form.get("date")
                }
            job["state"] =  {
                    "active": False,
                    "completed": False,
                    "paused": False,
                    "terminated": False
                }
            job["fees"] = {
                    "contractor": form.get("fees_contractor"),
                    "misc": form.get("fees_misc"),
                    "insurance": form.get("fees_insurance"),
                    "overhead": form.get("fees_overhead"),
                    "unit": "%"
                }
            job["cost"] = {
                    "task": 0,
                    "contractor": 0,
                    "misc": 0,
                    "insurance": 0,
                    "overhead": 0,
                    "total": {
                    "metric": 0,
                    "imperial": 0
                    },
                    "unit": "$"
                }
            job["result"] = {
                    "paid": False,
                    "payamount": 0,
                    "paydate": None
                }
            job["progress"] =  0

        await Project().addJobToQueue(id=id, data=job)
        
        return RedirectResponse( url=f"/project_jobs/{id}", status_code=302 )
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        project = await Project().get(id=id)
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "New Job",
                        "description": f"""New Job {job.get('title')} was created by {request.user.username}."""
                    }

                )
        await Project().update(data=project)


# JOB TASKS
@router.get('/jobtasks/{id}')
async def get_jobtasks(request):
    id = request.path_params.get('id')
    idd = id.split('-')
   
    p = await Project().get(id=idd[0])
    
    jb = [j for j in p.get('tasks') if j.get('_id') == id] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    
    return TEMPLATES.TemplateResponse('/project/jobTasks.html',
        {"request": request, "job": job, "standard": p.get('standard')})



@router.delete('/jobtask/{id}')
@login_required
async def delete_jobtask(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    job['tasks'].remove(task)
    await Project().update(data=p)
    return HTMLResponse(f"<div>{ task.get('title')} was Removed from Job {job.get('title')}</div>")
    


@router.get('/edit_jobtask/{id}')
@login_required
async def edit_jobtask(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ] 
    if len(task) > 0 :
        task = task[0]
    test_keys = task.get("event").keys()
    if "started" in test_keys:
        pass
    else: task["event"]["started"] = None
    if "completed" in test_keys:
        pass
    else: task["event"]["completed"] = None
    if "completion" in test_keys:
        pass
    else: task["event"]["completion"] = None
    if "terminated" in test_keys:
        pass
    else: task["event"]["terminated"] = None
    if "duration" in test_keys:
        pass
    else: task["event"]["duration"] = None
    if "paused" in test_keys:
        pass
    else: task["event"]["paused"] = []
    if "restart" in test_keys:
        pass
    else: task["event"]["restart"] = []

   
    contact = request.app.state
    display = {
        "metric": True,
        "imperial": True
    }
    p['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Task Event Fields Update",
                        "description": f"""Job Task  {task.get('title')} Event properties  were updated by SYSTEM_AUTO_UPDATES."""
                    }

                )
    await Project().update(data=p)
    return TEMPLATES.TemplateResponse('/project/jobTask.html',
        {
            "request": request, 
            "display": display ,
            "task": task, 
            "standard": p.get('standard'), 
            "job_id": job.get('_id'), 
            "crew": job.get('crew').get('members'),
            "contact": contact})


@router.post('/assign_task/{id}')
@login_required
async def assign_task(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    try:
        async with request.form() as form:
            crew_member = form.get('crew_member')
        crew_member = crew_member.split(" ")[0]
        eid = crew_member.split('-')[1]
        #eid = eid.split(" ")[0]
        employee = await Employee().get_worker(id=eid)
        
        if task.get('assigned'):
            if type(task.get('assignedto')) == str:
                task['assignedto'] = []
            else:
                pass
            if eid in task.get('assignedto'):
                return HTMLResponse(f""" 
                    <div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">That crew mamber is already on this task.</p>
                    </div>
                    """)
            else:
                task['assignedto'].append(eid)
                if idd[1] in employee.get('tasks'):
                    pass
                else:
                    employee['tasks'].append(idd[1])
                if employee.get('jobs'):
                    if idd[0] in employee.get('jobs'):
                        pass
                    else:
                        employee['jobs'].append(idd[0])
                else:
                    employee['jobs'] = [idd[0]]


                await Project().update(data=p)
                await Employee().update(data=employee)
                return HTMLResponse(f"""
                    <div class="uk-alert-success" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">{employee.get('oc')} has been assigned to task {idd[1]}.</p>
                    </div>
                        
                        """)
        else:
            task['assignedto'] = [eid]
            task['assigned'] = True
            if idd[1] in employee.get('tasks'):
                    pass
            else:
                employee['tasks'].append(idd[1])
            if employee.get('jobs'):
                if idd[0] in employee.get('jobs'):
                    pass
                else:
                    employee['jobs'].append(idd[0])
            else:
                employee['jobs'] = [idd[0]]

            await Project().update(data=p)
            await Employee().update(data=employee)
        return HTMLResponse(f"""
                    <div class="uk-alert-success" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm"> {employee.get('oc')}  has been assigned to task {idd[1]}.</p>
                    </div>""")
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-danger" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div> """
        )


@router.post("/filter_job_rate/{id}") 
async def filter_job_rate(request):
    id = request.path_params.get('id')
    idd = id.split('-')
        
    p = await Project().get(id=idd[0])  
    async with request.form() as form:
        category = form.get('task_category')
    if category == 'all':
        rates = p.get('rates')
    else:
        rates = [ rate for rate in p.get('rates') if rate.get('category') == category]
    
    return TEMPLATES.TemplateResponse('/project/task/filteredJobRates.html', {
        "request": request,
        "rates": rates,
        "job_id": id
    }) 


@router.post('/clear_task_assignment/{id}')
@login_required
async def clear_task_assignment(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    try:
        task['assignedto'] = job.get('crew').get('name')
        await Project().update(data=p)

        return HTMLResponse(f""" <div class="bg-teal-300 py-1 px-2">{job.get('crew').get('name')}</div> """)
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-danger" uk-alert>
                <a href class="uk-alert-close" uk-close></a>
                <p>{str(e)}</p>
            </div> """
        )
    finally: # Clean up.
        del(task)
        del(job)
        del(jb)
        del(p)
        del(pid)
        del(idd)
        del(id)



@router.get('/task_properties/{id}/{flag}')
async def get_task_properties(request):
    id = request.path_params.get('id')
    flag = request.path_params.get('flag')   
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    task['metric']['total'] = float(task.get('metric').get('quantity')) * float(task.get('metric').get('price'))
    return TEMPLATES.TemplateResponse('/project/task/metricProperties.html', {
        "request": request, "job_id": idd[0], "task": task,"to_dollars": to_dollars})



@router.get('/edit_task_properties/{id}/{flag}')
@login_required
async def edit_metric_properties(request):
    id = request.path_params.get('id')
    flag = request.path_params.get('flag')
   
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    if flag == 'metric':
        return TEMPLATES.TemplateResponse('/project/task/editMetric.html', {"request": request, "job_id": idd[0],"task": task})
    else:
        return HTMLResponse("")



@router.put('/update_task_properties/{id}/{flag}')
@login_required
async def update_metric_properties(request):
    id = request.path_params.get('id')
    flag = request.path_params.get('flag')
   
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0]
    async with request.form() as form:
        total = float(form.get('quantity')) * float(form.get('price'))
        task['metric']['unit'] = form.get('unit')
        task['metric']['quantity'] = form.get('quantity')
        task['metric']['price'] = form.get('price')
        task['metric']['total'] = total
    convert = convert_unit(unit=task.get('metric').get('unit'), value=float(task.get('metric').get('quantity', 0.01)))
    price_convert = convert_price_by_unit(unit=task.get('metric').get('unit'), value=float(task.get('metric').get('price', 0.01)))
    task['imperial']['unit'] = convert.get('unit')
    task['imperial']['quantity'] = convert.get('value')
    task['imperial']['price'] = price_convert.get('value')
    task['imperial']['total'] = task.get('imperial').get('price') * task.get('imperial').get('quantity')

    p['activity_log'].append(
                {
                    "id": timestamp(),
                    "title": f"Update Task Properties",
                    "description": f"""The Metric and Imperial properties of Task {task.get('title')} 
                        on Job {job.get('_id')} were updated  by {request.user.username}."""
                }

            ) 
    

    #return TEMPLATES.TemplateResponse("/project/task/updatedMetric.html", {"request": request, "id": id, "form": form, "total":total})
    contact = request.app.state
    display = {
        "metric": True,
        "imperial": True
    }

    await Project().update(data=p)
    return TEMPLATES.TemplateResponse('/project/jobTask.html',
        {
            "request": request, 
            "display": display ,
            "task": task, 
            "standard": p.get('standard'), 
            "job_id": job.get('_id'), 
            "crew": job.get('crew').get('members'),
            "contact": contact})

    


@router.post('/update_task_progress/{id}')
@login_required
async def update_task_progress(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    pid = idd[0].split('-')[0]
    p = await Project().get(id=pid)
    
    jb = [j for j in p.get('tasks') if j.get('_id') == idd[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    task = [t for t in job.get('tasks') if t.get('_id') == idd[1] ][0] 
    try:
        async with request.form() as form:
            progress = int(form .get('task_progress'))
        if progress == 100:
            task['state'] = {'active': False, 'complete': True, 'pause': False, 'terminate': False}
            task['event']['completed'] = timestamp()
            task['progress'] = progress
            # Log this update
        else:
            task['progress'] = progress
            #log this event
        await Project().update(data=p)
        return HTMLResponse(f""" {progress}""")
    except Exception as e:
        pass


@router.post('/add_worker_to_job_crew')
@login_required
async def add_worker_to_job_crew(request):    
    async with request.form() as form:
        wid = form.get('worker')
    idds = wid.split("_")
    idd = idds[0].split("-")
    p = await Project().get(id=idd[0])
    jb = [j for j in p.get('tasks') if j.get('_id') == idds[1] ] 
    worker = [w for w in p.get('workers', []) if w.get('id') == idds[0] ] 
    if len(jb) > 0:
        job = jb[0] 
    else:
        job={}
    
    job['crew']['members'].append(worker[0])
    e = await Employee().get_worker(id=idds[0].split('-')[1])
    if idds[1] in e.get('jobs'):
        pass
    else:
        e['jobs'].append(idds[1])
        await Employee().update( data=e )
    await Project().update(data=p)


    res = HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{worker[0].get('value').get('name')} is added to Job {idds[1]}.</p>
                            <p class="text-xs">{e}</p>
                        </div>""")
    return RedirectResponse(url=f"/project_jobcrew/{ idds[1] }", status_code=302)



@router.post('/add_daywork/{id}')
@login_required
async def add_daywork(request):
    id = request.path_params.get('id')
    hash_table = await Project().daywork_hash_table(id=id)
    p = await Project().get(id=id)
   
    payload = {
        "id": timestamp(),
        "project_id": id,
        "payment": {
            "paid": False,
            "amount": 0
        }
    }
    hash_obj = {}
   
    try:
        async with request.form() as form:    
            #payload["form_data"] = form         
            for key in form.keys():
                payload[key] = form.get(key) 
                hash_obj[key] = form.get(key) 
                
        payload['hash_key'] = Project().hash_data(data=hash_obj)
        #await sleep(1)   
        if payload.get('hash_key') in list(hash_table):
            return HTMLResponse(f"""
                            
                            <div class="uk-alert-danger" uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <p>Record already exists! </p>
                        </div>
                            
                            """)
        else:
            p['daywork'].append(payload)
            p['activity_log'].append(
                        {
                            "id": timestamp(),
                            "title": "Add Days Work Record",
                            "description": f"""Day Work for {payload.get('worker_name')} on Project {p.get('name')} was recorded by {request.user.username} """
                        }

                    )
            await Project().update(data=p)         

            employee_id = payload.get("worker_name")
            employee_id = employee_id.split('-')[1]
            employee = await Employee().get_worker(id=employee_id)
            employee['days'].append(payload)
            await Employee().update(data=employee)
        
            return HTMLResponse(f"""
                                
                                <div class="uk-alert-primary" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{payload}</p>
                            </div>
                                
                                """)
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:

        del(payload)


@router.post('/add_job_task')
@login_required
async def add_job_task(request):
    async with request.form() as form:
        data = form.get('task')
    idd = data.split('-')
    p = await Project().get(id=idd[0])
    jb = [j for j in p.get('rates') if j.get('_id') == f"{idd[0]}-{idd[1]}" ] 
    if len(jb) > 0:
        task = jb[0] 
    else:
        task={}
    await Project().addTaskToJob(id=f"{idd[0]}-{idd[3]}", data=task)
    res = HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{task.get('title')} is added to Job {idd[3]}.</p>
                        </div>""")
    return RedirectResponse(url=f"/project_job_tasks/{idd[1]}", status_code=302)


@router.post('/add_job_crew')
@login_required
async def add_job_crew(request):
    async with request.form() as form:
        data = form.get('crew')
    idd = data.split('-')
    p = await Project().get(id=idd[0])
    jb = [j for j in p.get('rates') if j.get('_id') == f"{idd[0]}-{idd[1]}" ] 
    if len(jb) > 0:
        task = jb[0] 
    else:
        task={}
    await Project().addTaskToJob(id=f"{idd[0]}-{idd[3]}", data=task)
    return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{task.get('title')} is added to Job {idd[3]}.</p>
                        </div>""")



@router.post('/update_job_phase/{id}')
@login_required
async def update_job_phase(request):
    id = request.path_params.get('id')
    async with request.form() as form:
        phase_resuest = form.get('projectphase')
    job_phase = await Project().update_project_job_phase(id=id, phase=phase_resuest)
    return HTMLResponse(f""" <div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>{job_phase }.</p>
                        </div>
    """)

