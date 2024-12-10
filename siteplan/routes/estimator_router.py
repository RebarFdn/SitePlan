from starlette.responses import HTMLResponse
from decoRouter import Router
from modules.project import  project_name_index
from modules.estimate import Estimate
from modules.Estimate.walls import Wall
from modules.Estimate.opening import Opening
from modules.Estimate.structural import RCColumn, RCBeam, Foundation, Slab, ConcreteFloor
from modules.Estimate.elibrary import Library
from modules.utils import timestamp, to_dollars
from config import (TEMPLATES,LOG_PATH ,SYSTEM_LOG_PATH ,SERVER_LOG_PATH, APP_LOG_PATH, DATA_PATH)
from pathlib import Path
from tinydb import TinyDB, Query

db = TinyDB(Path.joinpath(DATA_PATH, "wall_openings.json"))

router = Router()

@router.GET('/estimate')
async def get_estimate_index(request):
    projects_index = await project_name_index()
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
    projects_index = await project_name_index()
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


@router.get('/foundation')
async def get_wall(request):
    rebar_types = Library().rebarnotes    
    concrete_types = Library().concrete_types
    concrete_types =  list(concrete_types.keys())
    concrete_types.remove('legend')
    return TEMPLATES.TemplateResponse('/estimate/foundationDataEntry.html', {
        "request": request,
        'concrete_types': concrete_types,
        'rebar_types': list(rebar_types.keys())
        }) 



@router.post('/foundation')
async def process_foundation(request):
    payload = {
        'rebars': {}
    }
    rebars = {
        'main': {},        
        'links': {}
    }
    try:
        async with request.form() as form:            
            payload['id'] = form.get('tag') 
            payload['ftn_type'] = form.get('footing_type')            
            payload['width'] = form.get('width') 
            payload['length'] = form.get('length')
            payload['depth'] = form.get('depth') 
            payload['excavation_depth'] = form.get('exc_depth') 
            payload['unit'] = form.get('unit') 
            payload['ctype'] = form.get('concrete') 
            rebars['main']['type'] = form.get('mb_type') 
            rebars['main']['amt'] = form.get('mb_amount')            
            rebars['links']['type'] = form.get('ln_type') 
            rebars['links']['spacing'] = form.get('ln_spacing') 
            
        rebars['main']['unit'] = payload.get('unit') 
        rebars['main']['length'] = payload.get('length')         
        rebars['links']['unit'] = payload.get('unit')
           
        rebars['links']["ftn_width"] = payload.get('width')
        rebars['links']["ftn_length"] = payload.get('length')
        
        payload['rebars'] = rebars
        fdn = Foundation(data=payload)    
        concrete_specs = Library().concrete_types  
        return TEMPLATES.TemplateResponse('/estimate/foundationEstimateResult.html', 
                {
                    "request": request, 
                    "foundation": fdn.report, 
                    'dataclass': fdn,
                    "payload": payload,                    
                    'concrete_specs': concrete_specs.get(payload.get('ctype'))
                    
                })
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div>
            """)

    finally:
        del(payload) 
     


@router.get('/wall')
async def cmu_wall(request):
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
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div>
            """)

   


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
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div>
            """)

    finally:
        del(payload)
        
    

@router.get('/beam')
async def get_beam(request):
    lib = Library()
    rebar_types = lib.rebarnotes    
    concrete_types = lib.concrete_types
    concrete_types =  list(concrete_types.keys())
    concrete_types.remove('legend')
    try:
        return TEMPLATES.TemplateResponse('/estimate/beamDataEntry.html', {
            'request': request,
            'concrete_types': concrete_types,
            'rebar_types': list(rebar_types.keys())
            })
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div>
            """)
    

@router.post('/beam')
async def process_beam(request):
    payload = {
        'rebars': {}
    }
    rebars = {
        'main': {},
        'extra': {},
        'stirup': {}
    }
    try:
        async with request.form() as form:            
            payload['id'] = form.get('tag') 
            payload['beam_type'] = form.get('beam_type')
            payload['length'] = form.get('length') 
            payload['width'] = form.get('width') 
            payload['depth'] = form.get('depth') 
            payload['amt'] = form.get('amount') 
            payload['unit'] = form.get('unit') 
            payload['ctype'] = form.get('concrete') 
            rebars['main']['type'] = form.get('mb_type') 
            rebars['main']['amt'] = form.get('mb_amount')            
            rebars['stirup']['type'] = form.get('st_type') 
            rebars['stirup']['spacing'] = form.get('st_spacing') 
            rebars['stirup']['span'] = form.get('st_span') 
            rebars['stirup']['support_spacing'] = form.get('ovr_spacing') 
            if len(form.get('xb_amount')) > 0:
                rebars['extra']['type'] = form.get('xb_type') 
                rebars['extra']['amt'] = form.get('xb_amount')
                rebars['extra']['unit'] = payload.get('unit')
                rebars['extra']['length'] = payload.get('length') 
            else:
                pass
        rebars['main']['unit'] = payload.get('unit') 
        rebars['main']['length'] = payload.get('length')         
        rebars['stirup']['unit'] = payload.get('unit')
        rebars['stirup']["clm_width"] = payload.get('width')
        rebars['stirup']["clm_bredth"] = payload.get('depth')
        rebars['stirup']["clm_height"] = payload.get('length')
        if len(rebars['stirup']['span']) > 0:
            rebars['stirup']['span'] = float(rebars['stirup']['span'])
        else:
            rebars['stirup']['span'] = None
        if len(rebars['stirup']['support_spacing']) > 0:
            rebars['stirup']['support_spacing'] = float(rebars['stirup']['support_spacing'])
        else:
            rebars['stirup']['support_spacing'] = None
        payload['rebars'] = rebars
        beam = RCBeam(data=payload)    
        concrete_specs = Library().concrete_types  
        return TEMPLATES.TemplateResponse('/estimate/beamEstimateResult.html', 
                {
                    "request": request, 
                    "beam": beam.report, 
                    'dataclass': beam,
                    "payload": payload,                    
                    'concrete_specs': concrete_specs.get(payload.get('ctype'))
                    
                })
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div>
            """)

    finally:
        del(payload) 


@router.get('/slab')
async def get_slab(request):
    rebar_types = Library().rebarnotes    
    concrete_types = Library().concrete_types
    concrete_types =  list(concrete_types.keys())
    concrete_types.remove('legend')
    return TEMPLATES.TemplateResponse('/estimate/slabDataEntry.html', {
        "request": request,
        'concrete_types': concrete_types,
        'rebar_types': list(rebar_types.keys())
        }) 



@router.post('/slab')
async def process_slab(request):
    payload = {
        'rebars': {}
    }
    rebars = {
        'main': {},        
        'dist': {},
        'omain': {},
        'odist': {}

    }
    try:
        async with request.form() as form:            
            payload['id'] = form.get('tag')                       
            payload['width'] = form.get('width') 
            payload['length'] = form.get('length')
            payload['depth'] = form.get('depth') 
            payload['notes'] = form.get('notes') 
            payload['unit'] = form.get('unit') 
            payload['ctype'] = form.get('concrete') 
            payload['span'] = form.get('span') 
            rebars['main']['type'] = form.get('mb_type') 
            rebars['dist']['type'] = form.get('db_type') 
            rebars['omain']['type'] = form.get('omb_type') 
            rebars['odist']['type'] = form.get('odb_type') 
            rebars['main']['spacing'] = form.get('mb_spacing') 
            rebars['dist']['spacing'] = form.get('db_spacing') 
            rebars['omain']['spacing'] = form.get('omb_spacing') 
            rebars['odist']['spacing'] = form.get('odb_spacing') 
            
            
        rebars['main']['unit'] = payload.get('unit') 
        rebars['dist']['unit'] = payload.get('unit') 
        rebars['omain']['unit'] = payload.get('unit') 
        rebars['odist']['unit'] = payload.get('unit') 
        # Set main and dist bar lengths
        if float(payload.get('width')) > float(payload.get('length')):
            rebars['main']['length'] = payload.get('length')  # Shortest distance  
            rebars['dist']['length'] = payload.get('width')  # longest distance     
        else:
            rebars['main']['length'] = payload.get('width')  # Shortest distance  
            rebars['dist']['length'] = payload.get('length') 
        rebars['main']['amt'] = int(float(rebars['dist']['length']) / float(rebars['main']['spacing']))
        rebars['dist']['amt'] = int(float(rebars['main']['length']) / float(rebars['dist']['spacing']))
        
        payload['rebars'] = rebars
        slab = Slab(data=payload)    
        concrete_specs = Library().concrete_types  
        return TEMPLATES.TemplateResponse('/estimate/slabEstimateResult.html', 
                {
                    "request": request, 
                    "slab": slab.report,                    
                    'dataclass': slab,
                    "payload": payload,                    
                    'concrete_specs': concrete_specs.get(payload.get('ctype'))
                    
                })
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div>
            """)

    finally:
        del(payload) 
     


@router.get('/floor')
async def concrete_floor( request ):    
    concrete_types =  list(Library().concrete_types.keys())
    concrete_types.remove('legend')
    return TEMPLATES.TemplateResponse('/estimate/concreteFloorDataEntry.html', {
        "request": request,
        'concrete_types': concrete_types
        
        })


@router.post('/floor')
async def process_concrete_floor(request):
    payload = {}
    try:
        async with request.form() as form:  
            for key, value in form.items():
                payload[key] = value 
        floor = ConcreteFloor(data=payload)    
        concrete_specs = Library().concrete_types  
        return TEMPLATES.TemplateResponse('/estimate/floorEstimateResult.html', 
                {
                    "request": request, 
                    "floor": floor.report,                    
                    'dataclass': floor,
                    "payload": payload,                    
                    'concrete_specs': concrete_specs.get(payload.get('ctype'))
                    
                })
    except Exception as e:
        return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>{str(e)}</p>
            </div>
            """)
    finally:
        del(payload) 
     

@router.get('/roof')
async def timber_roof(request):
    return TEMPLATES.TemplateResponse('/estimate/roofDataEntry.html', {
        "request": request
        })

@router.get('/roof_segment/{segment}')
async def timber_roof_segment(request):
    segment = request.path_params.get('segment')
    if segment == 'hip':
        return HTMLResponse(f"""
            <div id="hip">
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div class="flex flex-col">
                    <p>Hipped End</p>
                    <div class="relative max-w-xs overflow-hidden bg-cover bg-no-repeat">                    
                        <img
                        src="/static/imgs/resource/hip.png"
                        class="max-w-xs transition duration-300 ease-in-out hover:scale-110"
                        alt="Hip" />
                    </div>
                </div>
                <div class="bg-gray-400 m-5 p-5 rounded-md">
                            <form>
                
                        <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">                           
                            <div>
                                <label class="text-xs font-semibold" for="width">Rake</label>
                                <input class="input input-solid" placeholder="Length of Rake" type="number" step="0.1" id="rake" name="rake" value="3.45"/>
                            </div>
                            <div>
                                <label class="text-xs font-semibold" for="fascia">Fascia</label>
                                <input class="input input-solid" placeholder="Length of Fascia" type="number" step="0.1" id="fascia" name="fascia" value="6.1"/>
                            </div>
                            <div>
                                <label class="text-xs font-semibold" for="hhcount">Amount </label>
                                <input class="input input-solid" placeholder="Amount" type="number" step="0.1" id="hh-count" name="hh_count" value="2"/>
                            </div>
                        </div>
                        </form>
                
                    
                </div>
            </div>
        </div>
       """)
    elif segment == 'longside':
        return HTMLResponse(f"""
            <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div class="flex flex-col">
                    <p>Long Hipped End</p>
                    <div class="relative max-w-xs overflow-hidden bg-cover bg-no-repeat mt-10">                    
                        <img
                        src="/static/imgs/resource/Trapeze.png"
                        class="max-w-xs transition duration-300 ease-in-out hover:scale-150"
                        alt="Hip" />
                    </div>
                </div>
                <div class="bg-gray-400 m-5 p-5 rounded-md">
                
                        <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">    
                            <div>
                                <label class="text-xs font-semibold" for="width">Ridge</label>
                                <input class="input input-solid" placeholder="Length of Ridge" type="number" step="0.1" id="ridge" name="ridge" value="1.85"/>
                            </div>                       
                            <div>
                                <label class="text-xs font-semibold" for="width">Rake</label>
                                <input class="input input-solid" placeholder="Length of Rake" type="number" step="0.1" id="rake" name="rake" value="3.45"/>
                            </div>
                            <div>
                                <label class="text-xs font-semibold" for="fascia">Fascia</label>
                                <input class="input input-solid" placeholder="Length of Fascia" type="number" step="0.1" id="fascia" name="fascia" value="6.1"/>
                            </div>
                            <div>
                                <label class="text-xs font-semibold" for="lhcount">Amount </label>
                                <input class="input input-solid" placeholder="Amount" type="number" step="0.1" id="lh-count" name="lh_count" value="2"/>
                            </div>
                        </div>
                
                    
                </div>
            </div>""")

   
                  
    
@router.post('/roof')
async def process_timber_roof(request):
    payload = {}
    async with request.form() as form:
        for key, value in form.items():
            payload[key] = value
    return TEMPLATES.TemplateResponse('/estimate/roofEstimateResult.html',
        {
            'request': request,
            'payload': payload 
         
         })

