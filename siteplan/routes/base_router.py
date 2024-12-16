# Base Router 
from starlette.responses import HTMLResponse, RedirectResponse, StreamingResponse
from starlette_login.decorator import login_required
from decoRouter import Router
from modules.rate import all_rates, get_industry_rate, rate_categories, rate_model, delete_rate, rate_index_generator, save_rate
from modules.project import update_project, all_projects, get_project
from modules.utils import timestamp
from config import TEMPLATES

router = Router()

# About Industry Rate
@router.get('/about_rate')
async def about_rate(request):
    return TEMPLATES.TemplateResponse('/rate/aboutRate.html',{'request': request})


# Employee Related routes
@router.post('/new_rate')
@login_required
async def new_industry_rate(request):
    rate = rate_model()
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
    await save_rate(data=rate, user=username)    
    return RedirectResponse(url=f"/industry_rates/{rate.get('category')}", status_code=302)


@router.post('/clone_rate')
@login_required
async def clone_industry_rate(request):
    rate = rate_model()
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
    new_rate = await save_rate(data=rate, cloned=form.get('_id'), user=username) 
    try:   
        return RedirectResponse(url=f"/industry_rates/{rate.get('category')}", status_code=302)
    finally:
        del(rate)
        del(username)
        del(new_rate)
        del(form)


@router.get('/industry_rates/{filter}')
async def industry_rates(request):
    store_room = request.app.state.STORE_ROOM
    filter = request.path_params.get('filter')
    rates = await all_rates()
    categories = {rate.get('category') for rate in rates }
    r_categories = rate_categories()
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
        "store_room":  store_room,
        "rate_categories": list(r_categories.keys())

    }
    )


@router.get('/rates_html_index/')
async def get_rates_html_index(request):    
    return StreamingResponse(rate_index_generator(filter='all'), media_type="text/html")


@router.get('/rates_html_index/{filter}')
async def get_filtered_rates_html_index(request):
    filter_request = request.path_params.get('filter')    
    rates = await all_rates()
    categories = {rate.get('category') for rate in rates }
    if filter_request:
        if filter_request == 'all' or filter_request == 'None':            
            filtered = rates
        else:
            filtered = [rate for rate in rates if rate.get("category") == filter]
    return TEMPLATES.TemplateResponse('/rate/ratesIndex.html',
        {
            'request': request,
            'filter': filter_request,
            'filtered': filtered,
            'rates': rates,
            'categories': categories
        })


@router.get('/rate/{id}')
async def get_rate(request):    
    projects = await all_projects()
    id = request.path_params.get('id')
    try: rate = await get_industry_rate(id=id)
    except Exception: rate = await get_industry_rate(id=id) 
    r_categories = rate_categories()
    try:
        return TEMPLATES.TemplateResponse('/rate/industryRate.html', {
            "request": request, 
            "rate": rate, 
            "task": rate,
            "projects": projects,
            "rate_categories": list(r_categories.keys())
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
        


@router.delete('/industry_rate/{id}')
async def delete_industry_rate(request): 
    try:
        await delete_rate(id=request.path_params.get('id'))
        return RedirectResponse(url=f"/industry_rates/all", status_code=302)
    except Exception as e:
        return HTMLResponse(f"""
            <div class="uk-alert-danger" uk-alert>
                <a href class="uk-alert-close" uk-close></a>
                <p>{ str(e) }</p>
            </div>""")
    

@router.post('/add_industry_rate/{id}')
@login_required
async def add_industry_rate(request):   
    id = request.path_params.get('id')
    idds = set()    
    async with request.form() as form:
        rate_id = form.get('rate').strip()    
    project = await get_project(id=id)
    rate = await get_industry_rate(id=rate_id)
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
            await update_project(data=project)            
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
            del(form)
            del(rate_id)
            del(item)
    
            



