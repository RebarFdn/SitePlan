import asyncio
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.staticfiles import StaticFiles
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import HTMLResponse, StreamingResponse, RedirectResponse
from starlette_htmx.middleware import HtmxMiddleware
from starlette_login.backends import SessionAuthBackend
from starlette_login.login_manager import LoginManager
from starlette_login.decorator import login_required
from starlette_login.middleware import AuthenticationMiddleware
from config import (
    DEBUG, SECRET_KEY, HOST, PORT, TEMPLATES,
    SERVER_LOG_PATH
    )
from modules.zen import zen_now
from routes.auth_router import router as auth_routes, loadusers
from routes.project_router import router as p_router
from routes.project_accounting_router import router as accounting_router
from routes.project_jobs_task_router import router as project_jobstask_router
from routes.team_router import router as team_router
from routes.base_router import router as base_router
from routes.supplier_router import router as supplier_router 
from routes.printer_router import router as printer_router
from routes.estimator_router import router as estimate_router
from api.team_api import router as employee_api
from modules.platformuser import user_list
from modules.decorator import admin_only


login_manager = LoginManager(redirect_to='login', secret_key=SECRET_KEY)
login_manager.set_user_loader(user_list.user_loader)

async def get_users():
    users = loadusers()    
    yield '<ul class="mx-10 p-2">'
    for user in users:
        yield f"""<li><div class="ml-3">
        <p 
        class="text-sm font-medium text-gray-900 cursor-pointer"
        hx-get="/user/{user.get('username')}"        
        hx-trigger="click"
        hx-target="#user"
        ><span class="text-xs font-bold text-indigo-500">User</span> {user.get("username")}</p>
        
        
      </div></li>"""
        await asyncio.sleep(0.015)
    yield '</ul>'


@login_required
async def get_user(request):
    name = request.path_params.get('name')
    store = loadusers({"name": "Haley", "age": 29 })
    search = [user for user in store if user.get('name') == name][0]
    return HTMLResponse(f"""<p class="mx-5 p-2">{search.get("name")}</p><p 
        class="text-sm text-gray-500"
        >Age { search.get("age") }</p>"""
        )


async def home(request):    
    if request.user.is_authenticated:
        #content = f'You are logged in as {request.user.username}'
        return RedirectResponse(url='/dash', status_code=303)
    else:
        content = 'You are not logged in'
        return TEMPLATES.TemplateResponse('/intro/intro.html', {
            'request': request,
            'content': content
            })
    

async def loading(request):      
    return HTMLResponse(f""" <div class="spinner-dot-pulse">
	<div class="spinner-pulse-dot"></div>
</div>""")


@login_required
async def users(request):
    generator = get_users()
    return StreamingResponse(generator, media_type='text/html')


@login_required
async def dashboard(request):    
    
    return TEMPLATES.TemplateResponse('/dash.html', {
            'request': request,
            'session': request.user,
            

            })
    


async def uikit(request):
    return TEMPLATES.TemplateResponse('/test.html', {'request': request})


async def zenNow(request):
    return HTMLResponse(f"""        
        <p class="text-xs font-bold bg-gray-100 py-2 px-4 rounded w-96">{zen_now()}</P> 

        """)


@login_required
async def get_logs(request):
    context = {"title": "FastAPI Streaming Log Viewer over WebSockets", "log_file": SERVER_LOG_PATH,}
    return TEMPLATES.TemplateResponse("logs.html", {"request": request, "context": context})       


async def log_reader(n=5):
    log_lines = []
    with open(SERVER_LOG_PATH, "r") as file:
        for line in file.readlines()[-n:]:
            if line.__contains__("ERROR"):
                log_lines.append(f'<span class="text-red-400">{line}</span><br/>')
            elif line.__contains__("WARNING"):
                log_lines.append(f'<span class="text-orange-300">{line}</span><br/>')
            else:
                log_lines.append(f'<span class="text-sm text-gray-600">{line}</span><br/>')
        return log_lines
    
  
@login_required
@admin_only
async def adminPage(request):
    return TEMPLATES.TemplateResponse('/adminPage.html', {'request': request})

async def ai_assistant(request):
   # assistant = AiAssistant().send_message(role='user', content='where is the deepest part of the earth ?')
    return HTMLResponse(f"""<div>Sorry Our Ai Assistant is currently undergoing maintenance. Please try the service later.</div""")

routes =[
    Route('/', endpoint=home), 
    Route('/admin', adminPage, name='admin'),
    Route('/ai_assistant', endpoint=ai_assistant, name='ai_assistant'),
    Route('/uikit', endpoint=uikit), 
    Route('/dash', endpoint=dashboard),    
    Route('/loading', endpoint=loading),  
    Route('/users', endpoint=users), 
    Route('/logs', endpoint=get_logs),  
    Route('/user/{name}', endpoint=get_user),  
    Route('/zen', endpoint=zenNow), 
    Mount('/static', StaticFiles(directory='static'))
]

routes.extend([route for route in auth_routes])
routes.extend([route for route in p_router])
routes.extend([route for route in accounting_router])
routes.extend([route for route in project_jobstask_router])
routes.extend([route for route in team_router])
routes.extend([route for route in base_router])
routes.extend([route for route in supplier_router])
routes.extend([route for route in estimate_router])
routes.extend([route for route in printer_router])
routes.extend([route for route in employee_api])




def startApp():
    print('Starting SiteApp Servers ')
   
    


def shutdownApp():
    print('Application setup was Successfull ... !')

app = Starlette(
    debug=DEBUG, 
    middleware=[
        Middleware(HtmxMiddleware),
        Middleware(SessionMiddleware, secret_key=SECRET_KEY),
        Middleware(
            AuthenticationMiddleware,
            backend=SessionAuthBackend(login_manager),
            login_manager=login_manager,
            allow_websocket=False,
        ),
        
        ],
    routes=routes,
    on_startup= startApp(),
    on_shutdown= shutdownApp()
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
    allow_origin_regex=None,
    expose_headers=[
        "Access-Control-Allow-Origin",
        "Access-Control-Allow-Cedentials",
        "Access-Control-Allow-Expose-Headers",
    ],
    max_age=3600,
)
app.state.login_manager = login_manager
app.state.ADMIN_EMAIL = 'admin@siteplaner.org'
app.state.STORE_ROOM = {"admin": "Ian Moncrieffe"}

@app.websocket_route('/ws')
async def websocket_endpoint(websocket):
    await websocket.accept()
    
    try:
        while True:
            await asyncio.sleep(1)
            await websocket.send_text(f"""<form ><input type="text" placeholder="Wall Length" name="length">
                                      </form>""")
    except Exception as e:
            print(e)
    finally:
        await websocket.close()


def run_http():   

    from uvicorn import run
    run(
        app,
        host=HOST,
        port= PORT     )
    
run_http()

