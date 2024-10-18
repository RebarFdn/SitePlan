from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.project import Project
from modules.estimate import Estimate,  EstimateModel
from modules.Estimate.walls import Wall
from modules.Estimate.opening import Opening
from modules.Estimate.column import RCColumn
from modules.Estimate.elibrary import Library


from modules.estimator.column import Column

from modules.utils import timestamp, to_dollars
from config import (TEMPLATES,LOG_PATH ,SYSTEM_LOG_PATH ,SERVER_LOG_PATH, APP_LOG_PATH, DATA_PATH)


from pathlib import Path
from tinydb import TinyDB, Query

db = TinyDB(Path.joinpath(DATA_PATH, "wall_openings.json"))





router = Router()

@router.GET('/estimate')
async def get_estimate_index(request):
    projects_index = await Project().nameIndex()
    context = { 
        "title": "Siteplanner Estimator",
        "projects": projects_index,
        "estimates": Estimate().all()
        }
    return TEMPLATES.TemplateResponse("estimator.html", {"request": request, "context": context})       


@router.GET('/estimates')
async def get_estimates(request):
    
    context = { 
        "title": "Siteplanner Estimator",
        "estimates": Estimate().all()
        }
    return HTMLResponse( 
        f"""<div class="uk-alert-success" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p class="text-xs">{ context}</p>
         </div>"""
    )             


@router.GET('/estimate/{project}')
async def get_estimate(request):
    projects_index = await Project().nameIndex()
    context = { 
        "title": "Siteplanner Estimator",
        "estimate": Estimate().get(project=request.path_params.get('project'))
        }
    return HTMLResponse( 
        f"""<div class="uk-alert-success" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p class="text-xs">{ context}</p>
         </div>"""
    )       


 

@router.POST('/estimate')
async def new_estimates(request):
    data = {}
    async with request.form() as form:
        for key in form.keys():
            data[key] = form.get(key) 
            
    data['created_by'] = request.user.username
    e = Estimate( data=data )
    e.save()

    return HTMLResponse(f"""<div class="uk-alert-success" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p class="text-xs">{dict(e.estimate.model_dump())}</p>
         </div>"""
    )


@router.get('/wall')
async def get_wall(request):
    return TEMPLATES.TemplateResponse('/estimate/wallDataEntry.html', {"request": request}) 


@router.post('/wall')
async def process_wall(request):
       
    payload = {}
    rebars = {
    "v": {"type": 'm12', "spacing": 0.4, "unit": 'm'},
    "h": {"type": 'm10', "spacing": 0.6, "unit": 'm'}

    }
    try:
        async with request.form() as form:            
            payload['tag'] = form.get('tag')        
            payload['type'] = form.get('type')  
            payload['unit'] = form.get('unit') 
            payload['thickness'] = (form.get('thickness'))         
            payload['length'] = (form.get('length'))
            payload['height'] = (form.get('height'))
            rebars['v']['type'] = form.get("vbar_type")
            rebars['v']['spacing'] = (form.get("vbar_spacing"))
            rebars['v']['unit'] = payload['unit']
            rebars['h']['type'] = form.get("hbar_type")
            rebars['h']['spacing'] = (form.get("hbar_spacing"))
            rebars['h']['unit'] = payload['unit']
        payload["rebars"] = rebars
        payload['openings'] = Opening().get(wall_tag=payload.get('tag'))  
        wall = Wall(data=payload)
        
       
       
        return TEMPLATES.TemplateResponse('/estimate/wallEstimateResult.html', {"request": request, "wall": wall }) 
    except Exception as e:
        return HTMLResponse(f"""
                            <div class="uk-alert-warning" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{str(e)}</p>
                            </div>
                            """)




@router.post('/opening')
async def add_opening(request):       
    payload = {}    
    
    try:
        async with request.form() as form:  
            wall_tag = form.get('wall_tag')   
            payload['wall_tag'] = wall_tag         
            payload['tag'] = form.get('otag')           
            payload['unit'] = form.get('ounit') 
            payload['height'] = (form.get('oheight'))
            payload['width'] = (form.get('owidth'))
            payload['amt'] = (form.get('oamt'))
        opening = Opening( data=payload )
        result = opening.save        
        #alldocs = Opening().all
        
        return TEMPLATES.TemplateResponse('/estimate/wallOpenings.html', {"request": request, "openings": result}) 
    except Exception as e:
        return HTMLResponse(f"""
                            <div class="uk-alert-warning" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{str(e)}</p>
                            </div>
                            """)


@router.get('/column')
async def get_column(request):
    lib = Library()
    rebar_types = lib.rebarnotes
    
    concrete_types = lib.concrete_types
    concrete_types =  list(concrete_types.keys())
    concrete_types.remove('legend')
    

    try:
        
        return TEMPLATES.TemplateResponse('/estimate/columnDataEntry.html', {
            'request': request,
            'concrete_types': concrete_types,
            'rebar_types': list(rebar_types.keys())
            })
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

   


@router.post('/column')
async def process_column(request):
       
    payload = {
        'rebars': {}
    }
    rebars = {
        'main': {},
        'stirup': {}
    }
    try:
        async with request.form() as form:            
            payload['id'] = form.get('tag') 
            payload['height'] = form.get('height') 
            payload['width'] = form.get('width') 
            payload['bredth'] = form.get('bredth') 
            payload['amt'] = form.get('amount') 
            payload['unit'] = form.get('unit') 
            payload['ctype'] = form.get('concrete') 
            rebars['main']['type'] = form.get('mb_type') 
            rebars['main']['amt'] = form.get('mb_amount')
            rebars['stirup']['type'] = form.get('st_type') 
            rebars['stirup']['spacing'] = form.get('st_spacing') 
            rebars['stirup']['span'] = form.get('st_span') 
            rebars['stirup']['support_spacing'] = form.get('ovr_spacing') 
        rebars['main']['unit'] = payload.get('unit') 
        rebars['main']['length'] = payload.get('height') 
        rebars['stirup']['unit'] = payload.get('unit')
        rebars['stirup']["clm_width"] = payload.get('width')
        rebars['stirup']["clm_bredth"] = payload.get('bredth')
        rebars['stirup']["clm_height"] = payload.get('height')
        if len(rebars['stirup']['span']) > 0:
            rebars['stirup']['span'] = float(rebars['stirup']['span'])
        else:
            rebars['stirup']['span'] = None
        if len(rebars['stirup']['support_spacing']) > 0:
            rebars['stirup']['support_spacing'] = float(rebars['stirup']['support_spacing'])
        else:
            rebars['stirup']['support_spacing'] = None
        payload['rebars'] = rebars
        column = RCColumn(data=payload)    
        concrete_specs = Library().concrete_types    
              
        return TEMPLATES.TemplateResponse('/estimate/columnEstimateResult.html', 
                {
                    "request": request, 
                    "column": column.report, 
                    'dataclass': column,
                    'concrete_specs': concrete_specs.get(column.concrete_type)
                    
                })
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(payload)
        
    

@router.get('/beam')
async def get_beam(request):
    return TEMPLATES.TemplateResponse('/estimate/beamDataEntry.html', {'request': request})

