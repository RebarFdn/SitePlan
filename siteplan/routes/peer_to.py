from starlette.websockets import WebSocket, WebSocketDisconnect
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from decoRouter import Router
from modules.project import get_project
from modules.employee import get_worker, get_worker_by_name
from modules.rate import get_industry_rate
from modules.supplier import get_supplier
from modules.accumulator import accumulate
from modules.peer_share import PeerShareData, all_peer_share, get_peer_share, save_peer_share, delete_peer_share
from config import TEMPLATES
from comms import peer_client, ConnectedDevices, get_saved_ip_list


def get_files()->list:
    return []

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

async def search_employee(protocols:list)->dict:
    if has_numbers(protocols[1]): # check if request is id or name
        return await get_worker(id=protocols[1])
    else:
        return await get_worker_by_name(name=f"{protocols[1]} {protocols[2]}")



async def peer_to_peer(ws: WebSocket):
    await ws.accept(subprotocol=None, headers=None)
    search = await accumulate()  
    validator:list = list(search.keys())  
    files:list = get_files()
    try:
        while True: 
            msg = await ws.receive_text()
            if msg in validator:
                json_data = search.get(msg) 
                await ws.send_json(json_data)
            elif msg in files:
                file = f"your file: {msg}".encode()
                await ws.send_bytes(file)
            elif 'Project' in msg or 'project' in msg or 'PROJECT' in msg:
                protocols = msg.split()
                project = await get_project(id=protocols[1])
                if protocols.__len__() > 2:
                    await ws.send_json(project.get(protocols[2]))
                else:
                    await ws.send_json(project)
            elif 'Employee' in msg or 'employee' in msg or 'worker' in msg:
                protocols = msg.split()
                employee = await search_employee(protocols)                       
                if protocols.__len__() > 3:
                    await ws.send_json(employee.get(protocols[3]))
                elif protocols.__len__() == 3:
                    if has_numbers(protocols[1]): # Request include employee id and property
                        await ws.send_json(employee.get(protocols[3]))
                    else: # Request is employee name
                        await ws.send_json(employee)
                elif protocols.__len__() == 2:# Request is employee id
                    await ws.send_json(employee)
                    
            else:
                await ws.send_text(msg)          
            
        ws._raise_on_disconnect(msg)
        await ws.close()
            
    except WebSocketDisconnect:
        pass

# Peer Interface
peer_router = Router()

@peer_router.get('/peer')
@peer_router.post('/peer')
async def peer_to_peer_client(request:Request):
    if request.method == 'POST':        
        async with request.form() as form:
            message = form.get('message')
            peer = form.get('peer')
        json_data = await peer_client(message, uri=peer)
        return HTMLResponse(f"""<div>{json_data}</div>""" )
    data:dict = {"protocol": "Peer Connection"}
    return TEMPLATES.TemplateResponse(
            '/peer/index.html',
            {
                "request": request, 
                "data": data, 
                "device_list": get_saved_ip_list(),
                "peer_share": all_peer_share()

 
            }
    )

# Data Share Interface
share_router = Router()

@share_router.get('/share/{docid}/{name}/{desc}/{user}')
async def get_share_request(request:Request):
    psd:PeerShareData = PeerShareData(
        docid=request.path_params.get('docid'),
        name=request.path_params.get('name'),
        description=request.path_params.get('desc'),
        user=request.path_params.get('user')
    )
    save_peer_share(data=psd.model_dump())
    return HTMLResponse('<span uk-icon="icon: link-external; ratio: .75"  uk-tooltip="This Item is being Shared with Peers!"></span>')



    