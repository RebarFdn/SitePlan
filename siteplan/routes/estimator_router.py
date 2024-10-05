from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse
from decoRouter import Router
from modules.project import Project
from modules.estimate import Estimate,  EstimateModel

from modules.Estimate.walls import Wall
from modules.estimator.column import Column
from modules.utils import timestamp, to_dollars
from config import (TEMPLATES,LOG_PATH ,SYSTEM_LOG_PATH ,SERVER_LOG_PATH, APP_LOG_PATH )





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
        print(form)    
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
            payload['walltag'] = wall_tag         
            payload['tag'] = form.get('otag')           
            payload['unit'] = form.get('ounit') 
            payload['height'] = (form.get('oheight'))
            payload['width'] = (form.get('owidth'))
            payload['amt'] = (form.get('oamt'))
        print(payload)
        return HTMLResponse(f"""
                            <div class="uk-alert-success" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{payload}</p>
                            </div>
                            """)
    except Exception as e:
        return HTMLResponse(f"""
                            <div class="uk-alert-warning" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{str(e)}</p>
                            </div>
                            """)


@router.get('/column')
async def get_column(request):
    try:
        html = await Column().html_ui()
        return HTMLResponse( html )
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(html)


@router.post('/column')
async def process_column(request):
       
    payload = {}
    try:
        async with request.form() as form:            
            for key in form:
                payload[key] = form.get(key) 
        column = Column(data=payload)        
        report = await column.html_report()       
        return HTMLResponse(report)
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(payload)
        
    

@router.get('/beam')
async def get_beam(request):
    return HTMLResponse(f"""<div class="text-xl font-semibold bg-gray-300 mb-1">Beam Estimator</div>
                        <section class="bg-gray-2 rounded-xl">
                        <ul class="uk-subnav uk-subnav-pill" uk-switcher>
                            <li><a href="#">Data</a></li>
                            <li><a href="#">Reinforcement</a></li>
                            
                        </ul>

                        <div class="uk-switcher uk-margin">
                            <div class="p-5 shadow-lg">
                                <form 
                                    class="space-y-4 uk-form-stacked" 
                                   
                                >
                                    <div class="w-full">
                                        <label class="sr-only uk-form-label" for="tag">Tag</label>
                                        <input class="input input-solid max-w-full" placeholder="Beam Tag" type="text" id="tag" name="tag" />
                                    </div>
                                    <div class="w-full">
                                        <label class="sr-only uk-form-label" for="type">Type</label>
                                        <input class="input input-solid max-w-full" placeholder="Beam  Type" type="text" id="type" name="type" />
                                    </div>


                                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                        <div>
                                            <label class="sr-only" for="unit">Unit</label>
                                            <input class="input input-solid" placeholder="Unit of measurement" type="text" id="unit" name="unit" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="thickness">Bredth</label>
                                            <input class="input input-solid" placeholder="Bredth of the Beam " type="number" step="0.1" id="bredth" name="bredth" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="length">Length</label>
                                            <input class="input input-solid" placeholder="Length of the Column" type="number" step="0.1" id="length" name="length" />
                                        </div>

                                        <div>
                                            <label class="sr-only" for="depth">Depth>
                                            <input class="input input-solid" placeholder="Depth of the Column" type="number" step="0.1" id="depth" name="depth" />
                                       </div>
                                    </div>

                                    <div class="w-full">
                                        <label class="sr-only" for="message">Message</label>

                                        <textarea class="textarea textarea-solid max-w-full" placeholder="Message" rows="3" id="message" name="message"></textarea>
                                    </div>

                                    <div class="mt-4">
                                        <button 
                                        type="button" 
                                        class="rounded-lg btn btn-primary btn-block"
                                         hx-post="/column"
                                        hx-target="#e-content"
                                        >Send Enquiry</button>
                                    </div>
                                </form>
                            </div>
                            <div>
                        
                        <form class="uk-form-stacked">

    <div class="uk-margin">
        <label class="uk-form-label" for="form-stacked-text">Text</label>
        <div class="uk-form-controls">
            <input class="uk-input" id="form-stacked-text" type="text" placeholder="Some text...">
        </div>
    </div>

    <div class="uk-margin">
        <label class="uk-form-label" for="form-stacked-select">Select</label>
        <div class="uk-form-controls">
            <select class="uk-select" id="form-stacked-select">
                <option>Option 01</option>
                <option>Option 02</option>
            </select>
        </div>
    </div>

    <div class="uk-margin">
        <div class="uk-form-label">Radio</div>
        <div class="uk-form-controls">
            <label><input class="uk-radio" type="radio" name="radio1"> Option 01</label><br>
            <label><input class="uk-radio" type="radio" name="radio1"> Option 02</label>
        </div>
    </div>

</form>
                        
                        </div>
                            
                        </div>
                            
                        </section>
                        
                        """)

