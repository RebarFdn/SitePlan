## Project router
# This route handles all project related requests 
import datetime
from datetime import datetime
import json
from asyncio import sleep
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from starlette_login.decorator import login_required
from starlette.background import BackgroundTask
from decoRouter import Router
from modules.project import Project
from modules.employee import Employee
from modules.rate import Rate
from modules.utils import today, timestamp, to_dollars, convert_timestamp
from modules.unit_converter import convert_unit, convert_price_by_unit
from config import TEMPLATES


router = Router()

# Output:
# October 11, 2022
async def update_projectrates_task(id:str=None):
    p = await Project().get(id=id)
    try:

        for rate in p.get('rates', []):
            price_convert = json.loads(json.dumps(convert_price_by_unit(unit=rate.get('metric').get('unit'), value=float(rate.get('metric').get('price', 0.01)))))
            rate['imperial']['unit'] = price_convert.get('unit')
            rate['imperial']['price'] = price_convert.get('value')
            
        
        p['activity_log'].append(
            {
                "id": timestamp(),
                "title": f"Auto Update to Project Rates",
                "description": f"""Project rate imperial unit and price fields were updated to reflect a ballance with the metric counterparts by SYSTEM_AUTO_UPDATE """
            }

        ) 
        await Project().update(data=p)
    except Exception as e:
        print(f"update projectrates task has failed ---> {str(e)}")
    finally:
        print(f"Done updating Project {p.get('name')} rates Fields.")



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
                "street": form.get('standard'), 
                "town": form.get('standard'),
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
            },
            "created_by": username
            

        }   
    p = Project(data=data)
    p.setup()
    p.runsetup() 
    new_project = await p.save()    
    return RedirectResponse(url=f'/project/{new_project.get("_id")}', status_code=303)
   

@router.GET('/projects')
@login_required
async def get_projects(request):    
    username =  request.user.username        
    p = await Project().all()        
    projects = [project for project in p.get('rows', []) if project.get('value').get("meta_data", {}).get("created_by") == username]
    return TEMPLATES.TemplateResponse('/project/projectsIndex.html',{
        'request': request,
        'projects': projects
    })


@router.get('/project/{id}')
@login_required
async def get_project(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    return TEMPLATES.TemplateResponse('/project/projectPage.html', 
                                      {
                                          "request": request, 
                                          "id": id, 
                                          "project": {
                                              "_id": p.get("_id"),
                                              "name": p.get("name"),
                                              "category": p.get("category"),
                                              "standard": p.get("standard"),
                                              "owner": p.get("owner"),
                                              "address": p.get("address"),
                                              "admin": p.get("admin"),
                                              "meta_data": p.get("meta_data"),
                                                                                           
                                              
                                              }
                                          })


@router.get('/project_home/{id}')
@login_required
async def project_home(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    return TEMPLATES.TemplateResponse('/project/projectHome.html', 
                                      {
                                          "request": request, 
                                          "id": id,                                           
                                          "project": {
                                              "_id": p.get("_id"),
                                              "name": p.get("name"),
                                              "category": p.get("category"),
                                              "standard": p.get("standard"),
                                              "owner": p.get("owner"),
                                              "address": p.get("address"),
                                              "admin": p.get("admin"),
                                              "meta_data": p.get("meta_data"),
                                                                                           
                                              
                                              }
                                          })



@router.get('/project_api/{id}')
async def project_api(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    return JSONResponse(p)




# Project State 
@router.get('/project_state/{id}')
@router.post('/project_state/{id}')
async def get_project_state(request):
    id = request.path_params.get('id')
    idd = id.split('-')     
       
    p = await Project().get(id=idd[0])
    if request.method == 'GET':
        project = {
                "_id": p.get('_id'),
                "name": p.get('name'),
                "state": p.get('state',{}),
                "event": p.get('event',{})
            }
    if request.method == 'POST':  
        state = idd[1]
         
        if state == 'activate':
            p['state'] = {'active': True, 'completed': False, 'paused': False, 'terminated': False}
            p['event']['started'] = timestamp()
        elif state == 'complete':
            p['state'] = {'active': False, 'completed': True, 'paused': False, 'terminated': False}
            p['event']['completed'] = timestamp()
        elif state == 'pause':
            p['state'] = {'active': False, 'completed': False, 'paused': True, 'terminated': False}
            p['event']['paused'].append(timestamp())
        elif state == 'resume':
            p['state'] = {'active': True, 'completed': False, 'paused': False, 'terminated': False}
            p['event']['restart'].append(timestamp())
        elif state == 'terminate':
            p['state'] = {'active': False, 'completed': False, 'paused': False, 'terminated': True}
            p['event']['terminated'] = timestamp()
        else:
            pass
        
        p['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Update Project State",
                        "description": f"""Project State was set to {state}d by {request.user.username} """
                    }

                )
        await Project().update(data=p)
        return RedirectResponse(url=f"/project_state/{p.get('_id')}-state", status_code=302)
    return TEMPLATES.TemplateResponse(
        "/project/projectState.html", 
        {
            "request": request,
            "project": project
        }
        
        )
                        
                           

# Project Events 
@router.get('/project_event/{id}')
@router.post('/project_event/{id}')
async def get_project_event(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    if request.method == 'GET':
        project = {
                    "_id": p.get('_id'),
                    "name": p.get('name'),                
                    "event": p.get('event',{})
                }
    if request.method == 'POST':
        event = ''
        async with request.form() as form:
            for key, value in form.items():
                event = key
                if key == 'paused':
                    p['event'][key].append(timestamp(value))
                elif key == 'restart':
                    p['event'][key].append(timestamp(value))
                else:
                    p['event'][key] = timestamp(value)
                
        p['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Update Project Event State",
                        "description": f"""Project Event {event} was updated to {value} by {request.user.username} """
                    }

                )
            
        await Project().update(data=p)
        res = HTMLResponse(f"""<div class="uk-alert-primary" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{event}</p>
        </div>
        """)
        return RedirectResponse(url=f"/project_event/{p.get('_id')}", status_code=302)

    

    return TEMPLATES.TemplateResponse(
        "/project/projectEvent.html", 
        {
            "request": request,
            "project": project
        })


# Project Events 
@router.get('/project_activity/{id}')
async def get_project_activity(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    return TEMPLATES.TemplateResponse(
        "/project/activityLog.html", 
        {"request": request, "activity_log": p.get('activity_log')}
    )


## Project Jobs
@router.get('/project_jobs/{id}')
@login_required
async def get_project_jobs(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    jobs = p.get('tasks')
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobsIndex.html', 
        { "request": request, "p": p, "jobs": jobs }
        )


# jobs_report/{{p._id}}"
@router.get('/jobs_report/{id}')
@login_required
async def get_jobs_report(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    jobs = p.get('tasks')
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobsReport.html', 
        { "request": request, "p": {"_id": p.get('_id'), "name": p.get('name')}, "jobs": jobs }
        )


# jobs_report/{{p._id}}"
@router.get('/jobs_tasks_report/{id}')
@login_required
async def get_jjobs_tasks_report(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    jobs = p.get('tasks')
    
    return TEMPLATES.TemplateResponse(
        '/project/job/jobsTasksReport.html', 
        { 
            "request": request, 
            "p": {"_id": p.get('_id'), "name": p.get('name')}, 
            "jobs": jobs 
        }
    )



@router.get('/project_workers/{id}/{filter}')
async def get_project_workers(request):
    id = request.path_params.get('id')
    filter = request.path_params.get('filter')
    p = await Project().get(id=id)
    e = await Employee().all_workers()
    workers = p.get('workers')
    categories = { worker.get('value').get('occupation') for worker in workers }
    if filter:
        if filter == 'all' or filter == 'None':            
            filtered = workers 
        else:
            filtered = [worker for worker in workers if worker.get("value").get("occupation") == filter]
    return  TEMPLATES.TemplateResponse('/project/projectWorkers.html', 
                                       {
                                           "request": request,
                                           "id": id,
                                           "p": p,
                                           "employees": e,
                                           "workers": workers,
                                           "categories": categories,
                                           "filter" : filter,
                                           "filtered": filtered

                                           
                                        })


# PROCESS RATES
@router.get('/project_rates/{id}')
async def get_project_rates(request):
    id = request.path_params.get('id')
    from modules.rate import Rate        
    industry_rates = await Rate().all_rates()
    p = await Project().get(id=id)
    task = BackgroundTask(update_projectrates_task, id=id)
    
    
    return TEMPLATES.TemplateResponse('/project/rates/projectRates.html', 
        {
            "request": request,
            "p": {
                "_id": p.get('_id'),
                "name": p.get('name'),
                "rates": p.get('rates', [])
            },
            "industry_rates": industry_rates
        }, background=task)


@router.post('/add_project_rate/{rate_id}')
@login_required
async def add_project_rate(request):
    """Add Project Rate """
   
    rate = await Rate().get(id=request.path_params.get('rate_id'))    
    rates_ids = set() #to validate against
    message = None
    async with request.form() as form:
        project = await Project().get(id=form.get("project_id"))
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
            await Project().update(data=project)
        return RedirectResponse( url=f"/project_rates/{project.get('_id')}", status_code=302 )
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
    async with request.form() as form:
        data = form.get('employee')
    idd = data.split('-')
    p = await Project().get(id=idd[0])
    employees = await Employee().all_workers()
    employee = [e for e in employees.get('rows') if e.get('id') == idd[1]][0]
    employee['id'] = data
    p['workers'].append(employee)
    e = await Employee().get_worker(id=idd[1])
    if idd[0] in e.get('jobs'):
        pass
    else:
        e['jobs'].append(idd[0])
        await Employee().update(data=e)
    p['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Add Worker to Project",
                        "description": f"""Employee {employee.get('value').get('name')} was added to Project by {request.user.username} """
                    }

                )
    await Project().update(p)
    
    return RedirectResponse(url=f"""/project_workers/{p.get('_id')}/all""", status_code=302)



@router.post('/update_project_standard/{id}')
@login_required
async def update_project_standard(request):

    id = request.path_params.get('id')    
    p = await Project().get(id=id)
    try:
        async with request.form() as form:
            standard = form.get('standard')
        if standard == 'on':
            p['standard'] = "metric"
            changed = "Metric"
            
        else:
            p['standard'] = "imperial"
            changed = "Imperial"
        p['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Change Project Standard",
                        "description": f"""Project Standard was changed to {changed} by {request.user.username} """
                    }

                )
        await Project().update(data=p)
        return HTMLResponse(f"<p>{ changed.capitalize() }</p>")
    except:
        pass
    finally:
        del(p)
        



@router.get('/project_days/{id}')
async def get_project_days(request):
    id = request.path_params.get('id')
    p = await Project().get(id=id)
    #e = await Employee().all_workers()
    try:
        return TEMPLATES.TemplateResponse('/project/projectDaysWorkIndex.html',
            {
                "request": request,
                "project": {
                    "_id": id,
                    "name": p.get('name'),
                    "daywork": p.get('daywork')
                },
                "workers": p.get('workers')
            })
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
                                    <a href class="uk-alert-close" uk-close></a>
                                    <p>{str(e)}</p>
                                </div>
                            """)
    finally:
        del(p)
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
    p = await Project().get(id=id)
    async with request.form() as form:
        start_date = form.get('filter_start')
        end_date = form.get('filter_end')
    days = [day_work for day_work in p.get('daywork', []) if filter(date=day_work.get('date'), start=start_date, end=end_date ) ]
    day_workers = set()#days = sorted(days)
    print(days)
    worker_occurence = [ item.get('worker_name').split('_')[0] for item in days ]
    for day_worker in worker_occurence:
        day_workers.add(day_worker)
    workers = []
    for worker in list(day_workers):
        workers.append({"name": worker, "days": worker_occurence.count(worker)})

        
    
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
