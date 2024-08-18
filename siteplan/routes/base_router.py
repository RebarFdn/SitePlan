# Base Router 
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from starlette_login.decorator import login_required
from decoRouter import Router
from modules.rate import Rate
from modules.supplier import Supplier
from modules.equipment import Equipment
from modules.project import Project
from modules.utils import timestamp
from config import TEMPLATES




router = Router()

# Employee Related routes  

 

@router.post('/new_rate')
@login_required
async def new_industry_rate(request):
    rate = Rate().model
    username = request.user.username
    async with request.form() as form:
        rate['title'] = form.get('title')
        rate['description'] = form.get('description')
        rate['category'] = form.get('category')
        rate['metric']['unit'] = form.get('metric_unit')
        rate['metric']['price'] = float(form.get('metric_price'))
        rate['imperial']['unit'] = form.get('imperial_unit')
        rate['imperial']['price'] = float(form.get('imperial_price'))
        rate['output']['metric'] = float(form.get('metric_output'))
        rate['output']['imperial'] = float(form.get('imperial_output'))
    
    new_rate = Rate(data=rate)
    new_rate.data['metadata']['created_by'] = username
    await new_rate.save()
    return RedirectResponse(url=f"/industry_rates/{rate.get('category')}", status_code=302)



@router.get('/rates_html_table/')
async def rates_html_table(request):
    return StreamingResponse(Rate().html_table_generator(), media_type="text/html")

@router.get('/industry_rates/{filter}')
async def industry_rates(request):
    store_room = request.app.state.STORE_ROOM
    filter = request.path_params.get('filter')
    rates = await Rate().all_rates()
    categories = {rate.get('category') for rate in rates }
    if filter:
        store_room['filter'] = filter
        if filter == 'all' or filter == 'None':            
            filtered = rates
        else:
            filtered = [rate for rate in rates if rate.get("category") == filter]
    return TEMPLATES.TemplateResponse('/rate/industryRates.html', {
        "request": request,
        "filter": filter,
        "rates": rates,
        "categories": categories,
        "filtered": filtered,
        "store_room":  store_room

    }
                                      )


@router.get('/rates_html_index/')
async def get_rates_html_index(request):    
    return StreamingResponse(Rate().html_index_generator(), media_type="text/html")


@router.get('/rates_html_index/{filter}')
async def get_filtered_rates_html_index(request):
    filter_request = request.path_params.get('filter')
    return StreamingResponse(Rate().html_index_generator(filter=filter_request), media_type="text/html")

@router.get('/rate/{id}')
async def get_rate(request):
    
    projects = await Project().all()
    id = request.path_params.get('id')
    rate = await Rate().get(id=id)
    try:
        return TEMPLATES.TemplateResponse('/rate/industryRate.html', {
            "request": request, 
            "rate": rate, 
            "task": rate,
            "projects": projects.get('rows')
            } )
    except Exception as e:
        return HTMLResponse(f"""
            <div class="uk-alert-danger" uk-alert>
                <a href class="uk-alert-close" uk-close></a>
                <p>{ str(e) }</p>
            </div>""")
    finally:
        del(rate)
        del(id)
        del(projects)
        

    

@router.post('/add_industry_rate/{id}')
@login_required
async def add_industry_rate(request):
    from modules.project import Project
    id = request.path_params.get('id')
    idds = set()
    
    async with request.form() as form:
        rate_id = form.get('rate').strip()
    
    project = await Project().get(id=id)
    rate = await Rate().get(id=rate_id)
    rate['_id'] = f"{id}-{rate_id}"
    
    try:
            for item in project.get('rates'):
                idds.add(item.get('_id'))
            if rate.get('_id') in list(idds):
                return HTMLResponse(f"""
                    <div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p>{ rate.get('title') } is already added to {project.get('name')}</p>
                    </div>""")
            else:
                project['rates'].append(rate)
                project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Add Industry Rate to Project",
                        "description": f"""{rate.get('title')} was added to Project by {request.user.username} """
                    }

                )
                await Project().update(data=project)
                message = f"""
                    <div class="uk-alert-success" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p>{ rate.get('title') } has been added to {project.get('name')}</p>
                    </div>"""
                return RedirectResponse( url=f"/project_rates/{project.get('_id')}", status_code=302 )

    except Exception as e:
            try:
                return HTMLResponse(f"""
                    <div class="uk-alert-danger" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p>{ str(e) }</p>
                    </div>""")
            finally:
                del(e)
    finally:
            del(rate)
            del(id)
            del(idds)
            del(project)
            del(Project)
            del(form)
            del(rate_id)
            del(item)
    
            



