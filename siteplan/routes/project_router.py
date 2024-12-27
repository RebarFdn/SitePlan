## Project router
# This route handles all project related requests 
import datetime
from datetime import datetime
import json
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette_login.decorator import login_required
from starlette.background import BackgroundTask
from decoRouter import Router
from box import Box
from modules.project import get_project, update_project, all_projects, save_project
from modules.employee import all_workers, get_worker, update_employee
from modules.rate import all_rates, rate_categories, get_industry_rate
from modules.utils import timestamp, exception_message
from modules.unit_converter import convert_price_by_unit
from modules.mapper import Mapper
from printer.project_documents import printJobQueue, printMetricJobQueue, printImperialJobQueue
from config import TEMPLATES

router = Router()

async def update_projectrates_task(id:str=None):
    project = await get_project(id=id)
    try:
        for rate in project.get('rates', []):
            price_convert = json.loads(json.dumps(convert_price_by_unit(unit=rate.get('metric').get('unit'), value=float(rate.get('metric').get('price', 0.01)))))
            rate['imperial']['unit'] = price_convert.get('unit')
            rate['imperial']['price'] = price_convert.get('value') 
        project['activity_log'].append(
            {
                "id": timestamp(),
                "title": f"Auto Update to Project Rates",
                "description": f"""Project rate imperial unit and price fields were updated to reflect a ballance with the metric counterparts by SYSTEM_AUTO_UPDATE """
            }
        ) 
        await update_project(data=project)
    except Exception as e:
        print(f"update projectrates task has failed ---> {str(e)}")
    finally:
        print(f"Done updating Project {project.get('name')} rates Fields.")


@router.POST('/new_project')
@login_required
async def new_project(request):    
    username =  request.user.username        
    async with request.form() as form:
        data = {
            "name": form.get('name'),
            "category": form.get('category'),
            "standard": form.get('standard'),
            "address": {
                "lot": form.get('lot'), 
                "street": form.get('street'), 
                "town": form.get('town'),
                "city_parish": form.get('city_parish'),
                "country": form.get('country', "Jamaica") 
            },
            "owner": {
            "name": form.get('owner'),
            "contact": None,
            "address": {"lot": None, "street": None, "town": None,"city_parish": None,"country": None, }
            },
            "admin": {
                "leader": form.get('lead'),
                "staff": {
                "accountant": None,
                "architect": None,
                "engineer":None,
                "quantitysurveyor": None,
                "landsurveyor": None,
                "supervisors": []
                }
            }
            

        }   
    project = await save_project(data=data, user=username) 
    try:     
        return RedirectResponse(url=f'/project/{project.get("_id")}', status_code=303)
    except Exception as e:
        return HTMLResponse(exception_message(message=str(e)))
    finally:
        del(username)
        del(project)
        del(data)


@router.GET('/projects')
@login_required
async def get_projects(request):    
    username:str =  request.user.username        
    projects:list = await all_projects()        
    projects:list = [project for project in projects if project.get('value').get("meta_data", {}).get("created_by") == username]
    try:
        return TEMPLATES.TemplateResponse('/project/projectsIndex.html',{
            'request': request,
            'projects': projects
        })
    except Exception as e:
        return HTMLResponse(exception_message(message=str(e)))
    finally:
        del(username)        
        del(projects)


@router.get('/project/{id}')
@login_required
async def get_one_project(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    try:
        return TEMPLATES.TemplateResponse('/project/projectPage.html', 
            {
                "request": request, 
                "id": id,
                "project": {
                    "_id": project.get("_id"),
                    "name": project.get("name"),
                    "category": project.get("category"),
                    "standard": project.get("standard"),
                    "owner": project.get("owner"),
                    "address": project.get("address"),
                    "admin": project.get("admin"),
                    "meta_data": project.get("meta_data"),}
            })
    except Exception as e:
        return HTMLResponse(exception_message(message=str(e)))
    finally:
        del(id)        
        del(project)


@router.get('/project_home/{id}')
@login_required
async def project_home(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    try:
        return TEMPLATES.TemplateResponse('/project/projectHome.html', 
            {
                "request": request, 
                "id": id,                                           
                "project": {
                    "_id": project.get("_id"),
                    "name": project.get("name"),
                    "category": project.get("category"),
                    "standard": project.get("standard"),
                    "owner": project.get("owner"),
                    "address": project.get("address"),
                    "admin": project.get("admin"),
                    "meta_data": project.get("meta_data"),}
                })
    except Exception as e:
        return HTMLResponse(exception_message(message=str(e)))
    finally:
        del(id)        
        del(project)


@router.get('/project_api/{id}')
async def project_api(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    return JSONResponse(project)


# Project State 
@router.get('/project_state/{id}')
@router.post('/project_state/{id}')
async def get_project_state(request):
    id = request.path_params.get('id')
    idd = id.split('-')      
    project = await get_project(id=idd[0])
    if request.method == 'GET':
        project_ = {
                "_id": project.get('_id'),
                "name": project.get('name'),
                "state": project.get('state',{}),
                "event": project.get('event',{})
            }
    if request.method == 'POST':  
        state = idd[1]         
        if state == 'activate':
            project['state'] = {'active': True, 'completed': False, 'paused': False, 'terminated': False}
            project['event']['started'] = timestamp()
        elif state == 'complete':
            project['state'] = {'active': False, 'completed': True, 'paused': False, 'terminated': False}
            project['event']['completed'] = timestamp()
        elif state == 'pause':
            project['state'] = {'active': False, 'completed': False, 'paused': True, 'terminated': False}
            project['event']['paused'].append(timestamp())
        elif state == 'resume':
            project['state'] = {'active': True, 'completed': False, 'paused': False, 'terminated': False}
            project['event']['restart'].append(timestamp())
        elif state == 'terminate':
            project['state'] = {'active': False, 'completed': False, 'paused': False, 'terminated': True}
            project['event']['terminated'] = timestamp()
        else:
            pass        
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Update Project State",
                        "description": f"""Project State was set to {state}d by {request.user.username} """
                    }

                )
        await update_project(data=project)
        return RedirectResponse(url=f"/project_state/{project.get('_id')}-state", status_code=302)
    return TEMPLATES.TemplateResponse(
        "/project/projectState.html", 
        {
            "request": request,
            "project": project_
        }
        
        )
                          

# Project Events 
@router.get('/project_event/{id}')
@router.post('/project_event/{id}')
async def get_project_event(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    if request.method == 'GET':
        project_ = {
                    "_id": project.get('_id'),
                    "name": project.get('name'),                
                    "event": project.get('event',{})
                }
    if request.method == 'POST':
        event = ''
        async with request.form() as form:
            for key, value in form.items():
                event = key
                if key == 'paused':
                    project['event'][key].append(timestamp(value))
                elif key == 'restart':
                    project['event'][key].append(timestamp(value))
                else:
                    project['event'][key] = timestamp(value)                
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Update Project Event State",
                        "description": f"""Project Event {event} was updated to {value} by {request.user.username} """
                    }
                )            
        await update_project(data=p)
        res = HTMLResponse(f"""<div class="uk-alert-primary" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{event}</p>
        </div>
        """)
        return RedirectResponse(url=f"/project_event/{project.get('_id')}", status_code=302)
    return TEMPLATES.TemplateResponse(
        "/project/projectEvent.html", 
        {
            "request": request,
            "project": project_
        })


# Project Events 
@router.get('/project_activity/{id}')
async def get_project_activity(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    return TEMPLATES.TemplateResponse(
        "/project/activityLog.html", 
        {"request": request, "activity_log": project.get('activity_log')}
    )


## Project Jobs
@router.get('/project_jobs/{id}')
@login_required
async def get_project_jobs(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    jobs = project.get('tasks')
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobsIndex.html', 
        { "request": request, "p": project, "jobs": jobs }
        )


# jobs_report/{{p._id}}"
@router.get('/jobs_report/{id}')
@login_required
async def get_jobs_report(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    jobs = project.get('tasks')
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobsReport.html', 
        { "request": request, "p": {"_id": project.get('_id'), "name": project.get('name')}, "jobs": jobs }
        )


# jobs_report/{{p._id}}"
@router.get('/jobs_tasks_report/{id}')
@login_required
async def get_jjobs_tasks_report(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    jobs = project.get('tasks')
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobsTasksReport.html', 
        { 
            "request": request, 
            "p": {"_id": project.get('_id'), "name": project.get('name')}, 
            "jobs": jobs 
        }
    )


@router.get('/project_workers/{id}/{filter}')
async def get_project_workers(request):
    id = request.path_params.get('id')
    filter = request.path_params.get('filter')
    project = await get_project(id=id)
    employees = await all_workers()
    workers = project.get('workers')
    categories = { worker.get('value').get('occupation') for worker in workers }
    employee_categories = { employee.get('value').get('occupation') for employee in employees}
    if filter:
        if filter == 'all' or filter == 'None':            
            filtered = workers 
        else:
            filtered = [worker for worker in workers if worker.get("value").get("occupation") == filter]
    return  TEMPLATES.TemplateResponse('/project/projectWorkers.html', 
                                       {
                                           "request": request,
                                           "id": id,
                                           "p": project,
                                           "employees": employees,
                                           "workers": workers,
                                           "categories": categories,
                                           "filter" : filter,
                                           "filtered": filtered,
                                           "employee_categories": employee_categories

                                           
                                        })


# Employees Pool | Filtered
@router.get('/employee_pool/{project_id}/{filter}')
async def filter_employee_pool(request):
    '''Returns a Filtered list of employees'''
    project_id = request.path_params.get('project_id')
    filter = request.path_params.get('filter')
    employees = await all_workers()
    print(employees[0])
    if filter == 'all' or filter == 'None':
        return  TEMPLATES.TemplateResponse('/project/projectEmployeesPool.html', 
                                       {
                                           "request": request,
                                           "p": { "_id": project_id},
                                           "employees": employees 
                                           
                                        })
    else:
        filtered = [worker for worker in employees if worker.get("value").get("occupation") == filter]
        return  TEMPLATES.TemplateResponse('/project/projectEmployeesPool.html', 
                                       {
                                           "request": request,
                                           "p": { "_id": project_id},
                                           "employees": [worker for worker in employees if worker.get("value").get("occupation") == filter]
                                           
                                        })
        

   



# PROCESS RATES
@router.get('/project_rates/{id}')
async def get_project_rates(request):
    id = request.path_params.get('id')           
    industry_rates = await all_rates()
    project = await get_project(id=id)
    categories = set()
    rates_category =  [rate.get('category') for rate in industry_rates]
    for rate in rates_category:
        categories.add(rate)
    task = BackgroundTask(update_projectrates_task, id=id)   
    return TEMPLATES.TemplateResponse('/project/rates/projectRates.html', 
        {
            "request": request,
            "p": {
                "_id": project.get('_id'),
                "name": project.get('name'),
                "rates": project.get('rates', []),
                "categories": list( categories)
            },
            "industry_rates": industry_rates
        }, background=task)


# PROCESS RATES
@router.get('/project_rates_filtered/{id}')
async def get_project_rates_filtered(request):
    idd:str = request.path_params.get('id')
    idd:list = idd.split('_')    
    project:dict = await get_project(id=idd[0])   
    if idd[1] == 'all' or idd[1] == None:
        filtered_rates:list = project.get('rates', [])
    else: filtered_rates:list = [ rate for rate in project.get('rates', []) if rate.get('category') == idd[1]]
    return TEMPLATES.TemplateResponse('/project/rates/projectRatesTable.html', 
        {
            "request": request,
            "p": {
                "_id": project.get('_id'),
                "name": project.get('name'),
                "rates": filtered_rates,
                "categories": [rate.get('category') for rate in project.get('rates', [])],
                "filter": idd[1]
            }
        })


@router.get('/add_industry_rates/{filter}')
async def add_industry_rates(request):
    store_room = request.app.state.STORE_ROOM
    filter = request.path_params.get('filter').split('_')
    rates = await all_rates()
    categories = {rate.get('category') for rate in rates }
    get_industry_rate = rate_categories()
    if filter[1]:
        store_room['filter'] = filter[1]
        if filter[1] == 'all' or filter[1] == 'None':            
            filtered = rates
        else:
            filtered = [rate for rate in rates if rate.get("category") == filter[1]]
    return TEMPLATES.TemplateResponse('/project/rates/addIndustryRates.html', {
        "p": {"_id": filter[0]},
        "request": request,
        "filter": filter[1],
        "industry_rates": rates,
        "categories": categories,
        "filtered": filtered,
        "store_room":  store_room,
        "rate_categories": list(rate_categories())

    }
                                      )


@router.post('/add_project_rate/{rate_id}')
@login_required
async def add_project_rate(request):
    """Add Project Rate """
   
    rate = await get_industry_rate(id=request.path_params.get('rate_id'))    
    rates_ids = set() #to validate against
    message = None
    async with request.form() as form:
        project = await get_project(id=form.get("project_id"))
    for item in project.get('rates'): # add existing project rates ids to valid set
        rates_ids.add(item.get('_id'))
    try:
        rate['_id'] = f"{project.get('_id')}-{rate.get('_id')}"
        if rate.get('_id') in rates_ids:
            message = f"{rate.get('_id')} already exists in {project.get('name')} Rates Index."
        else:
            project['rates'].append(rate)
            message = f"{rate.get('title')} has been added to {project.get('name')} Rates Index."
            project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Add Industry Rate to Project",
                        "description": f"""{rate.get('title')} was added to Project by {request.user.username} """
                    }

                )
            await update_project(data=project)
        return HTMLResponse(
            f"""<div class="uk-alert-success" uk-alert>
                    <a href class="uk-alert-close" uk-close></a>
                    <p>{rate.get('title')} was added to {project.get('name')}'s Rates Index </p>
                </div> """
        )
    except Exception as e:
        return HTMLResponse(
            f"""<div class="uk-alert-danger" uk-alert>
                    <a href class="uk-alert-close" uk-close></a>
                    <p>{str(e)}</p>
                </div> """
        )


@router.post('/add_worker_to_project')
@login_required
async def add_worker_to_project(request):
    """Add Worker to The Projects Employees List

        Requires a concatenated sting with the project id 
        and the employee's id supplied by the request form.
        Example Request Form:
         String: 'PID2987_EID3023         
    
    """
    async with request.form() as form:
        data = form.get('employee') 
    idd = data.split('-')
    project = await get_project(id=idd[0])
    workers = [worker.get('key') for worker in project.get('workers')]
    employees = await all_workers()
    employee = [e for e in employees if e.get('id') == idd[1]][0]
    if employee.get('id') in workers:
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Add Worker to Project Failure",
                        "description": f"""Employee {employee.get('value').get('name')} is already a member of {p.get("name")}'s work Team.  User {request.user.username}"""
                    }
                )
    else:
        employee['id'] = data
        project['workers'].append(employee)
        e = await get_worker(id=idd[1])
        if idd[0] in e.get('jobs'):
            pass
        else:
            e['jobs'].append(idd[0])
            await update_employee(data=e)
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Add Worker to Project",
                        "description": f"""Employee {employee.get('value').get('name')} was added to Project by {request.user.username} """
                    }
                )
    await update_project(project)    
    return RedirectResponse(url=f"""/project_workers/{project.get('_id')}/all""", status_code=302)


@router.get('/remove_worker_from_project/{id}')
@login_required
async def remove_worker_from_project(request):
    """Removes a Worker from The Projects Employees List
        and deletes refference to the project in the employee's Jobs list.

        Request Parameter is a concatenated sting with the project id 
        and the employee's id.
        Example Request:
         String: '/remove_worker_from_project/PID2987_EID3023         
    
    """
    idd = request.path_params.get('id')
   
    idd = idd.split('-')
    project = await get_project(id=idd[0])
    for worker in project.get('workers'):
        if worker.get('key') == idd[1]:
            p['workers'].remove(worker)
    employee = await get_worker(id=idd[1])

    for job in employee.get('jobs'):
        if job == idd[0]:
            employee['jobs'].remove(job)
    project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Remove Worker from Project",
                        "description": f"""Employee {employee.get('name')} was removed from Project {idd[0]} by {request.user.username} """
                    }
                )
    await update_employee(data=employee)
    await update_project(data=p)    
    return RedirectResponse(url=f"""/project_workers/{project.get('_id')}/all""", status_code=302)


@router.post('/update_project_standard/{id}')
@login_required
async def update_project_standard(request):
    id = request.path_params.get('id')    
    project = await get_project(id=id)
    try:
        async with request.form() as form:
            standard = form.get('standard')
        if standard == 'on':
            project['standard'] = "metric"
            changed = "Metric"            
        else:
            project['standard'] = "imperial"
            changed = "Imperial"
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Change Project Standard",
                        "description": f"""Project Standard was changed to {changed} by {request.user.username} """
                    }
                )
        await update_project(data=p)
        return HTMLResponse(f"<p>{ changed.capitalize() }</p>")
    except:
        pass
    finally:
        del(project)        


@router.get('/project_days/{id}')
async def get_project_days(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    #e = await all_workers()
    try:
        return TEMPLATES.TemplateResponse('/project/projectDaysWorkIndex.html',
            {
                "request": request,
                "project": {
                    "_id": id,
                    "name": project.get('name'),
                    "daywork": project.get('daywork')
                },
                "workers": project.get('workers')
            })
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
                                    <a href class="uk-alert-close" uk-close></a>
                                    <p>{str(e)}</p>
                                </div>
                            """)
    finally:
        del(project)
        del(id)


# Days Work Filter
@router.post('/filter_days_work/{id}')
async def filter_days_work(request):
    def filter(date:str=None, start:str=None, end:str=None):
        day = datetime.strptime(date, "%Y-%m-%d")
        period_start = datetime.strptime(start, "%Y-%m-%d")
        period_end = datetime.strptime(end, "%Y-%m-%d")
        if day.date() >= period_start.date() and day.date() < period_end.date():
            return True
        else:
            return False
    id = request.path_params.get('id')
    project = await get_project(id=id)
    async with request.form() as form:
        start_date = form.get('filter_start')
        end_date = form.get('filter_end')
    days = [day_work for day_work in project.get('daywork', []) if filter(date=day_work.get('date'), start=start_date, end=end_date ) ]
    day_workers = set()#days = sorted(days)
    
    worker_occurence = [ item.get('worker_name') for item in days ]
    for day_worker in worker_occurence:
        day_workers.add(day_worker)
    workers = []
    for worker in list(day_workers):
        name = json.loads(json.dumps(worker.split('_')))
        workers.append({"id": name[1], "name": name[0], "days": worker_occurence.count(worker)})    
    return TEMPLATES.TemplateResponse(
        '/project/dayworkIndex.html', 
        {
            "request": request,
            "project": {
                "daywork": days,
                "start": start_date,
                "end": end_date,                
                "workers":  workers,
                "days_tally": len(worker_occurence) 
            }

        })


# Project Location and Maps
@router.post('/project_coords/{project_id}')
async def set_project_coords(request):
    id = request.path_params.get('project_id')
    project = await get_project(id=id)
    async with request.form() as form:
        coords = [float(form.get('lat')), float(form.get('lon'))]
    try:
        project['address']['coords'] = coords
        await update_project(data=project)
        return TEMPLATES.TemplateResponse('/project/addressLocation.html', {
            'request': request, 
            'project': {
                '_id': id,
                'address': project.get('address'),
            }
            
        })
    except:
        pass


async def save_map_to_img(handle:str, map:Mapper ):
    map.save_map_image(handle=handle)
    return None


@router.get('/project_location_map/{id}')
async def get_project_location_map(request):
    id = request.path_params.get('id')    
    project = await get_project(id=id)
    coords = project.get('address').get('coords')
    map:Mapper = Mapper(coords=coords)  
    try:        
       
        map.save_map(id)
        
        #map.add_draw_tools(True)  
        #map.add_minimap(True) 
        task:BackgroundTask = BackgroundTask(save_map_to_img, id, map)  
        
        
        return HTMLResponse(f""" <iframe src="/static/maps/{id}.html" width="100%" height="100%" style="border:none;">
                            </iframe>
                        """, background=task)
    except Exception as e:
        print(e)
        
    



