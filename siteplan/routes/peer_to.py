from starlette.websockets import WebSocket, WebSocketDisconnect
from modules.project import get_project
from modules.employee import get_worker, get_worker_by_name
from modules.rate import get_industry_rate
from modules.supplier import get_supplier
from modules.accumulator import accumulate

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
            print(msg)
        ws._raise_on_disconnect(msg)
        await ws.close()
            
    except WebSocketDisconnect:
        pass
    