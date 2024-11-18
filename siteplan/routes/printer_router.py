# printer_router.py

from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse
from starlette_login.decorator import login_required
from starlette.background import BackgroundTask
from decoRouter import Router
from box import Box
from modules.project import get_project
from modules.employee import all_workers, get_worker, update_employee
from modules.rate import all_rates, rate_categories, get_industry_rate
from modules.utils import timestamp, exception_message
from modules.unit_converter import convert_price_by_unit
from printer.project_documents import printJobQueue, printMetricJobQueue, printImperialJobQueue, print_project_rates
from config import TEMPLATES


router:Router = Router()


@router.get("/print_project_rates/{id}/{filter}")
async def print_projectrates(request):
    id:str = request.path_params.get('id')
    filter:str = request.path_params.get('filter')
    project:dict = await get_project(id=id)
    if filter == 'all' or filter == None:
        rates = project.get('rates')
    else: rates = [rate for rate in project.get('rates') if rate.get('category') == filter]
    data = {
        'id': id,
        'name': project.get('name'),
        'rates': rates,
        'filter': filter
    }
    report = Box(print_project_rates(data=data))

    try:  return HTMLResponse(exception_message(f"""<a href="{report.get('url')}" target="_blank">{report.get('file')}</a>"""))
    except Exception: return HTMLResponse(exception_message(Exception))
    finally: del(id); del(filter); del(rates); del(project); del(data)



@router.get('/print_jobs_tasks_report/{id}/{flag}')
async def print_jobs_report(request):
    id = request.path_params.get('id')
    flag = request.path_params.get('flag')
    project = await get_project(id=id)
    data = {
        'id': id,
        'name': project.get('name'),
        'jobs': project.get('tasks')
    }
    if flag == 'metric':
        report = Box(printMetricJobQueue(project_jobs=data))
    elif flag == 'imperial':
        report = Box(printImperialJobQueue(project_jobs=data))
    else:
        report = Box(printJobQueue(project_jobs=data))
    return HTMLResponse(f"""
        <div class="uk-alert-primary" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
                        <a href="{report.url}" target="blank">Open Document</a>
            <p> {report.file}</p>
        </div>
    """)
