#modeler.py
import json
import typing
from database import Recouch, local_db
try:
    from modules.utils import timestamp, load_metadata, set_metadata
    from modules.utils import generate_id
except Exception as e:
    from utils import timestamp,load_metadata, set_metadata
    from utils import generate_id

databases = { # Employee Databases
            "local":"site-workers", 
            "local_partitioned": False,
            "slave":"site-workers", 
            "slave_partitioned": False
            
            }


# connection to site-workers database 
db_connection:typing.Coroutine = local_db(db_name=databases.get('local'))   

def employee_model(key:str=None):
    EMPLOYEE_TEMPLATE = {
    "_id": None,  
    "name": "Site Worker",
    "oc": None,
    "sex": None,
    "dob": "",
    "height": None,
    "identity": None,
    "id_type": None,
    "trn": None,
    "occupation": None,
    "rating": None,
    "imgurl": None,
    "address": {
        "lot": None,
        "street": None,
        "town": None,
        "city_parish": None
    },
    "contact": {
        "tel": None,
        "mobile": None,
        "email": None
    },
    "account": {
        "bank": {
        "name": None,
        "branch": None,
        "account": "",
        "account_type": None
        },
        "payments": [],
        "loans": []
    },
    "nok": {
        "name": None,
        "relation": None,
        "address": None,
        "contact": None
    },
    "tasks": [],
    "jobs": [],
    "days": [],
    "state": {
        "active": False,
        "onleave": False,
        "terminated": False
    },
    "event": {
        "started": None,
        "onleave": [],
        "restart": [],
        "terminated": None,
        "duration": 0
    },
    "reports": [],
    
    }
    if key: return EMPLOYEE_TEMPLATE.get(key)
    else: return EMPLOYEE_TEMPLATE
    

#@lru_cache(maxsize=360)
async def all_employees(conn:typing.Coroutine=db_connection)->dict:   
    """_summary_
    Args:
        conn (typing.Coroutine, optional): _description_. Defaults to db_connection.
    Returns:
        dict: _description_
    """
    try:
        return await conn.get(_directive="_all_docs") 
    except Exception as e:
        return {"error": str(e)}   


#@lru_cache
async def all_workers(conn:typing.Coroutine=db_connection)->list:
    """_summary_
    Args:
        conn (typing.Coroutine, optional): _description_. Defaults to db_connection.
    Returns:
        list: _description_
    """
    data = await conn.get(_directive="_design/workers/_view/name-index") 
    try:
        return data.get('rows')
    except Exception as e:
        return {"error": str(e)}
    finally: del data


async def get_worker( id:str=None, conn:typing.Coroutine=db_connection )->dict: 
    """Get a single Employee record by quering the database with employee's _id
    Args:
        id (str, optional): The employee's _id . Defaults to None.
        conn (typing.Coroutine, optional): database connection object. Defaults to db_connection.
    Returns:
        dict: key value store of employee's record.
    """               
    return await conn.get(_directive=id) 


async def get_worker_name_index()->list:   
    workers = await all_workers() 
    try: return [{"name": item.get('value').get('name'), "id": item.get('id')} for item in  workers ]   
    finally: del workers

        
async def get_worker_by_name( name:str=None, conn:typing.Coroutine=db_connection ) -> dict:
    index = await get_worker_name_index()
    id = [item.get('id') for item in index if item.get('name') == name]
    try:
        if len(id) > 0:
            id=id[0]
        return await get_worker(id=id)
    except Exception as e:
        return {"error": str(e)}
    finally:
        del index
        del(id)
        
 
           
# CRUD Functions

async def save_employee(data:dict=None, user:str=None, conn:typing.Coroutine=db_connection ):        
    try:
        data["_id"] = generate_id(name=data.get('name'))
        data['imgurl'] = f"static/imgs/workers/{data.get('_id')}.png" 
        new_employee = employee_model() | data
        new_employee['meta_data'] = load_metadata(property='created', value=timestamp(), db=databases)        
        new_employee['meta_data'] = set_metadata(property='created_by', value=user, metadata=new_employee.get('meta_data'))
        await conn.post( json=new_employee)            
        return new_employee
    except Exception as e:
        return {"error": str(e)}
    

async def update_employee(data:dict=None, conn:typing.Coroutine=db_connection ):   
    payload =  await conn.put( json=data)   
    try:           
        return payload
    except Exception as e:
        return {"error": str(e)}
    finally: 
        del payload


async def add_job_task(id:str=None, data:dict=None)->dict: 
    """_Assign a task from a job to a worker_
    Args:
        id (str, optional): _employee's id_. Defaults to None.
        data (dict, optional): _description_. Defaults to None.

    Returns:
        dict: _Returns a dictionary with worker identification, 
        job identification and an updated jobtasks list_
    """        
    try:        
        #get the worker's data
        worker = await get_worker(id=id)                   
        worker['tasks'].append(data)                   
        await update_employee(data=worker) 
        idds = data.split('-')                    
        def process_job_tasks(item):
            if f"{idds[0]}-{idds[1]}" in item:
                return item
        jobtasks = list(map(process_job_tasks, worker.get('tasks')))
        return {"worker": id, "job": f"{idds[0]}-{idds[1]}", "tasks": jobtasks}            
    except Exception as ex:
        return {"status": str(ex)}


async def submit_day_work(eid:str=None, data:dict=None)-> list:
    '''Returns the list of days worked'''
    e = await get_worker(id=eid)
    try:
        e['days'].append(data)
        await update_employee(data=e)
        return e.get('days')
    except Exception as e:
        print({'function': 'submitDayWork', 'exception': str(e)}) # Log this
        return e.get('days')
    finally:
        del e


async def get_worker_info( id:str=None):
    worker = await get_worker(id=id) 
    worker = json.loads(json.dumps(worker))
    try: 
        loans =   worker.get('account').get('loans', [])     
        worker["account"] = json.loads(json.dumps({"loans": loans  }))
        worker["loans"] = len(worker.get('account').get('loans', []))
        worker["tasks"] = len(worker["tasks"])
        if "jobs" in worker.keys():
            worker["jobs"] = len(worker["jobs"])
        else:
            worker["jobs"] = 0
            # Fix missing key bug
            #worker["jobs"] = []
        await save_employee(data=worker)
        worker["days"] = len(worker["days"])
        worker["reports"] = len(worker["reports"])
            #self.processAccountTotals 
        return worker
    finally: del(worker)

       
async def process_days_work(name:str=None, date_id:str=None, paid:bool=False, amount:float=None):        
    employee = await get_worker_by_name(name=name)
    for daywork in employee.get('days'):
        if daywork.get('id') == date_id:
            daywork['payment']['amount'] = amount
            daywork['payment']['paid'] = paid
    await update_employee(data=employee)
        

async def process_account_totals(id:str=None):
    #function to process employee pay 
    def processPay(p):
        return p['total']
    worker = await get_worker(id=id)
    worker['account']['totals_payments'] = list(map(processPay, worker['account']['payments']))   
    worker['account']['total'] = sum(worker['account']['totals_payments'])   


async def add_pay( id=None, data=None):       
    try:        
        #get the worker's data
        worker = await get_worker(id=id)        
        worker['account']['payments'].append(data) 
        process_account_totals(id=id)       
        await update_employee(data=worker)
        return worker.get('account').get('payments')           
    except Exception as ex: 
        return {"status": str(ex)}
        

async def delete_pay( id:str=None, data:dict=None):
    worker = await get_worker(id=id)
    try:
        worker['account']['payments'].remove(data)
        await update_employee(data=worker)
        return worker.get('account').get('payments') 
    except Exception as e:
        return str(e)


async def add_job_task( id=None, data=None): 
    '''Assign a task from a job to a worker
            --- Returns a list of tasks of the said job asigned to the worker
    '''
    worker =  await get_worker(id=id) 
    try:        
        worker['tasks'].append(data)                   
        await update_employee(data=worker) 
        idds = data.split('-')                   
        def process_job_tasks(item):
            if f"{idds[0]}-{idds[1]}" in item:
                return item
        jobtasks = list(map(process_job_tasks, worker.get('tasks')))
        return {"worker": id, "job": f"{idds[0]}-{idds[1]}", "tasks": jobtasks}
            
    except Exception as ex:
        return {"status": str(ex)}

      
async def submit_daywork( eid:str=None, data:dict=None)-> list:
    '''Returns the list of days worked'''
    e:dict = await get_worker(id=eid)
    e['days'].append(data)
    await update_employee(data=e)
    return e.get('days')
    
    
# Html Responses
async def team_index_generator():
        e = await all_workers()
        try:
            yield f"""
                <div class="flex flex-row bg-gray-400 py-2 px-2 text-left rounded relative">
                    <p class="text-left">
                    Team Index
                     <span class="bg-gray-50 ml-10 py-1 px-2 border rounded-full">{len(e)}<span>
                      
                    </p>   
                   <a href="#new-worker" uk-toggle class="absolute right-0">Employ  .</a>
                </div>"""
            yield '<ul class="mx-2 h-96 overflow-y-auto">'
        
            for employee in e:
                yield f"""<li class="mt-2">        
                            <div
                                class="p-2 max-w-sm mx-auto bg-white rounded-lg shadow-lg flex items-center space-x-4 cursor-pointer"
                                hx-get="/team/{employee.get('id')}"
                                hx-target="#dash-content-pane"
                                hx-trigger="click"
                            >
                            <div class="shrink-0">
                                <img class="h-12 w-12 rounded-full" src="{employee.get('value').get('imgurl')}" alt="P">
                                <span class="text-xs"> {employee.get('id')}</span>
                            </div>
                            <div>
                                <div class="text-md font-medium text-gray-800"> {employee.get('value').get('name')} </div>
                                <span class="uk-badge">{employee.get('value').get('occupation')}</span>
                                
                            </div></div>
                            </li> """
            yield """<li>
            <div class="p-5 my-5 max-w-sm mx-auto bg-white rounded-lg shadow-lg flex items-center">
                <p class="text-xs">Team Index</p>
            </div>
            
            </li></ul></div>

            <!-- This is the modal -->
                        <div id="new-worker" uk-modal>
                            <div class="uk-modal-dialog uk-modal-body">
                                <h2 class="uk-modal-title">New Employee Registration </h2>

                                <form class="uk-form-stacked uk-grid-small uk-margin-top" uk-grid>

                                    <div class="uk-width-1-2">
                                     <label class="uk-form-label">Employee's Full Name</label>
                                        <input class="uk-input uk-form-width-large" type="text" name="name" placeholder="John Brown" aria-label="Large">
                                    </div>
                                   
                                    <div class="uk-width-1-2@s">
                                    <label class="uk-form-label">Employee's Alias </label>
                                        <input class="uk-input uk-form-width-medium" type="text" name="oc" placeholder="A.K.A" aria-label="Medium">
                                    </div>
                                   <hr class="uk-divider-icon">
                                    <div class="uk-width-1-4@s">
                                      <label class="uk-form-label">Sex </label>
                                        <select class="uk-select" name="sex" aria-label="Select">
                                            <option>Male</option>
                                            <option>Female</option>
                                            <option>Machine</option>
                                        </select>
                                    </div>                                    

                                    <div class="uk-width-1-4@s">
                                      <label class="uk-form-label">Date Of Birth</label>
                                        <input class="uk-input uk-form-width-small" type="date" name="dob">
                                    </div>

                                    <div class="uk-width-1-4@s">
                                      <label class="uk-form-label">Height in cm</label>
                                        <input class="uk-input uk-form-width-small" type="number" name="height" placeholder="102 cm" >
                                    </div>
                                   

                                    <div class="uk-width-1-3@s">
                                      <label class="uk-form-label">Identity</label>
                                        <input class="uk-input uk-form-width-small" type="text" name="identity">
                                    </div>

                                    <div class="uk-width-1-3@s">
                                      <label class="uk-form-label">Id Type</label>
                                        <select class="uk-select" name="id_type" aria-label="Select">
                                            <option>Passport</option>
                                            <option>Drivers License</option>
                                            <option>National</option>
                                        </select>
                                    </div>

                                     <div class="uk-width-1-3@s">
                                      <label class="uk-form-label">TRN</label>
                                        <input class="uk-input uk-form-width-small" type="text" name="trn">
                                    </div>
                                    

                                      <div class="uk-width-1-2">
                                     <label class="uk-form-label">Occupation</label>
                                        <input class="uk-input uk-form-width-large" type="text" name="occupation" placeholder="Occupation" aria-label="Large">
                                    </div>
                                   
                                    <div class="uk-width-1-2@s">
                                    <label class="uk-form-label">Rating</label>
                                        <input class="uk-input uk-form-width-medium" type="text" name="rating" placeholder="Rating" aria-label="Medium">
                                    </div>


                                    <div class="accordion-group accordion-group-bordered">
                                        <div class="accordion">
                                            <input type="checkbox" id="toggle-7" class="accordion-toggle" />
                                            <label for="toggle-7" class="accordion-title">Contact</label>
                                            <div class="accordion-content text-content2">
                                                <div class="min-h-0">
                                                <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Tel</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="tel" placeholder="876-123-4567" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Mobile</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="mobile" placeholder="Mobile" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                    <label class="uk-form-label">Email</label>
                                                        <input class="uk-input uk-form-width-medium" type="text" name="email" placeholder="email" aria-label="Medium">
                                                    </div>
                                                
                                                </div>
                                            </div>
                                        </div>
                                        <div class="accordion">
                                            <input type="checkbox" id="toggle-8" class="accordion-toggle" />
                                            <label for="toggle-8" class="accordion-title">Address</label>
                                            <div class="accordion-content">
                                                <div class="min-h-0">
                                                <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Lot</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="lot" placeholder="Lot" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Street</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="street" placeholder="Street" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Town</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="town" placeholder="Town" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">City/Parish</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="city_parish" placeholder="City or Parish" aria-label="Medium">
                                                </div>
                                                
                                                </div>
                                            </div>
                                        </div>
                                        <div class="accordion">
                                            <input type="checkbox" id="toggle-9" class="accordion-toggle" />
                                            <label for="toggle-9" class="accordion-title">Banking</label>
                                            <div class="accordion-content text-content2">
                                                <div class="min-h-0">
                                                <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Bank</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="bank" placeholder="bank" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Account No.</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="account_no" placeholder="Account No." aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                    <label class="uk-form-label">Account Type</label>
                                                        <input class="uk-input uk-form-width-medium" type="text" name="account_type" placeholder="Account Type" aria-label="Medium">
                                                    </div>
                                                
                                                </div>
                                            </div>
                                        </div>
                                        <div class="accordion">
                                            <input type="checkbox" id="toggle-10" class="accordion-toggle" />
                                            <label for="toggle-10" class="accordion-title">Next Of Kin</label>
                                            <div class="accordion-content text-content2">
                                                <div class="min-h-0">
                                                <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Name</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="kin_name" placeholder="Name" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Contact</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="kin_contact" placeholder="Contact" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                    <label class="uk-form-label">Address</label>
                                                       
                                                     <textarea class="textarea textarea-solid max-w-full" placeholder="Address" rows="4" id="kin_address" name="kin_address"></textarea>
                                                     </div>
                                                
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                <p class="uk-text-right">
                                    <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                                    <button 
                                        class="uk-button uk-button-primary" 
                                        type="button"
                                        hx-post="/newworker"
                                        hx-target="#dash_message"
                                        
                                        >Save</button>
                                </p>
                                </form>
                            </div>
                        </div>
            
            """
        except Exception as ex:
            yield f"""<div class="uk-alert-warning" uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <p>{str(ex)}</p>
                        </div>                       
                       
                        
                    """
            
        finally:
            del(e)




class Employee:
    instances = 0
    _id:str = None   
    data:dict = {}  
    meta_data:dict = {
        "created": timestamp(),
        "database": {
            "name":"site-workers", "partitioned": False,
            "slave":"site-workers", "partitioned": False
            
            },
        "img_url": None      
    }
    index:set = set()
    worker:dict = {}
    workers:list = []

    def __init__(self, data:dict=None) -> None:
        Employee.instances += 1
        self.conn = Recouch(local_db=self.meta_data.get('database').get('name')) 
        self.slave = Recouch(local_db=self.meta_data.get('database').get('slave'))
        try:
            if not data:
                self.generate_id()
            else:
                self.data = data
                if self.data.get("_id"):
                    pass
                else: self.generate_id()
        except Exception as e:
            print(e)
    
    def mount(self, data:dict=None) -> None:        
        if data:            
            self.data = data
            if self.data.get("_id"):
                pass
            else:
                generate_id(name=self.data.get('name', 'E W'))

    
    # Html Responses
    async def team_index_generator(self):
        e = await all_workers()
        try:
            yield f"""
                <div class="flex flex-row bg-gray-400 py-2 px-2 text-left rounded relative">
                    <p class="text-left">
                    Team Index
                     <span class="bg-gray-50 ml-10 py-1 px-2 border rounded-full">{len(e.get('rows', []))}<span>
                      
                    </p>   
                   <a href="#new-worker" uk-toggle class="absolute right-0">Employ  .</a>
                </div>"""
            yield '<ul class="mx-2 h-96 overflow-y-auto">'
        
            for employee in e.get('rows', []):
                yield f"""<li class="mt-2">        
                            <div
                                class="p-2 max-w-sm mx-auto bg-white rounded-lg shadow-lg flex items-center space-x-4 cursor-pointer"
                                hx-get="/team/{employee.get('id')}"
                                hx-target="#dash-content-pane"
                                hx-trigger="click"
                            >
                            <div class="shrink-0">
                                <img class="h-12 w-12 rounded-full" src="{employee.get('value').get('imgurl')}" alt="P">
                                <span class="text-xs"> {employee.get('id')}</span>
                            </div>
                            <div>
                                <div class="text-md font-medium text-gray-800"> {employee.get('value').get('name')} </div>
                                <span class="uk-badge">{employee.get('value').get('occupation')}</span>
                                
                            </div></div>
                            </li> """
            yield """<li>
            <div class="p-5 my-5 max-w-sm mx-auto bg-white rounded-lg shadow-lg flex items-center">
                <p class="text-xs">Team Index</p>
            </div>
            
            </li></ul></div>

            <!-- This is the modal -->
                        <div id="new-worker" uk-modal>
                            <div class="uk-modal-dialog uk-modal-body">
                                <h2 class="uk-modal-title">New Employee Registration </h2>

                                <form class="uk-form-stacked uk-grid-small uk-margin-top" uk-grid>

                                    <div class="uk-width-1-2">
                                     <label class="uk-form-label">Employee's Full Name</label>
                                        <input class="uk-input uk-form-width-large" type="text" name="name" placeholder="John Brown" aria-label="Large">
                                    </div>
                                   
                                    <div class="uk-width-1-2@s">
                                    <label class="uk-form-label">Employee's Alias </label>
                                        <input class="uk-input uk-form-width-medium" type="text" name="oc" placeholder="A.K.A" aria-label="Medium">
                                    </div>
                                   <hr class="uk-divider-icon">
                                    <div class="uk-width-1-4@s">
                                      <label class="uk-form-label">Sex </label>
                                        <select class="uk-select" name="sex" aria-label="Select">
                                            <option>Male</option>
                                            <option>Female</option>
                                            <option>Machine</option>
                                        </select>
                                    </div>                                    

                                    <div class="uk-width-1-4@s">
                                      <label class="uk-form-label">Date Of Birth</label>
                                        <input class="uk-input uk-form-width-small" type="date" name="dob">
                                    </div>

                                    <div class="uk-width-1-4@s">
                                      <label class="uk-form-label">Height in cm</label>
                                        <input class="uk-input uk-form-width-small" type="number" name="height" placeholder="102 cm" >
                                    </div>
                                   

                                    <div class="uk-width-1-3@s">
                                      <label class="uk-form-label">Identity</label>
                                        <input class="uk-input uk-form-width-small" type="text" name="identity">
                                    </div>

                                    <div class="uk-width-1-3@s">
                                      <label class="uk-form-label">Id Type</label>
                                        <select class="uk-select" name="id_type" aria-label="Select">
                                            <option>Passport</option>
                                            <option>Drivers License</option>
                                            <option>National</option>
                                        </select>
                                    </div>

                                     <div class="uk-width-1-3@s">
                                      <label class="uk-form-label">TRN</label>
                                        <input class="uk-input uk-form-width-small" type="text" name="trn">
                                    </div>
                                    

                                      <div class="uk-width-1-2">
                                     <label class="uk-form-label">Occupation</label>
                                        <input class="uk-input uk-form-width-large" type="text" name="occupation" placeholder="Occupation" aria-label="Large">
                                    </div>
                                   
                                    <div class="uk-width-1-2@s">
                                    <label class="uk-form-label">Rating</label>
                                        <input class="uk-input uk-form-width-medium" type="text" name="rating" placeholder="Rating" aria-label="Medium">
                                    </div>


                                    <div class="accordion-group accordion-group-bordered">
                                        <div class="accordion">
                                            <input type="checkbox" id="toggle-7" class="accordion-toggle" />
                                            <label for="toggle-7" class="accordion-title">Contact</label>
                                            <div class="accordion-content text-content2">
                                                <div class="min-h-0">
                                                <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Tel</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="tel" placeholder="876-123-4567" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Mobile</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="mobile" placeholder="Mobile" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                    <label class="uk-form-label">Email</label>
                                                        <input class="uk-input uk-form-width-medium" type="text" name="email" placeholder="email" aria-label="Medium">
                                                    </div>
                                                
                                                </div>
                                            </div>
                                        </div>
                                        <div class="accordion">
                                            <input type="checkbox" id="toggle-8" class="accordion-toggle" />
                                            <label for="toggle-8" class="accordion-title">Address</label>
                                            <div class="accordion-content">
                                                <div class="min-h-0">
                                                <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Lot</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="lot" placeholder="Lot" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Street</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="street" placeholder="Street" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Town</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="town" placeholder="Town" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">City/Parish</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="city_parish" placeholder="City or Parish" aria-label="Medium">
                                                </div>
                                                
                                                </div>
                                            </div>
                                        </div>
                                        <div class="accordion">
                                            <input type="checkbox" id="toggle-9" class="accordion-toggle" />
                                            <label for="toggle-9" class="accordion-title">Banking</label>
                                            <div class="accordion-content text-content2">
                                                <div class="min-h-0">
                                                <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Bank</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="bank" placeholder="bank" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Account No.</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="account_no" placeholder="Account No." aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                    <label class="uk-form-label">Account Type</label>
                                                        <input class="uk-input uk-form-width-medium" type="text" name="account_type" placeholder="Account Type" aria-label="Medium">
                                                    </div>
                                                
                                                </div>
                                            </div>
                                        </div>
                                        <div class="accordion">
                                            <input type="checkbox" id="toggle-10" class="accordion-toggle" />
                                            <label for="toggle-10" class="accordion-title">Next Of Kin</label>
                                            <div class="accordion-content text-content2">
                                                <div class="min-h-0">
                                                <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Name</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="kin_name" placeholder="Name" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                <label class="uk-form-label">Contact</label>
                                                    <input class="uk-input uk-form-width-medium" type="text" name="kin_contact" placeholder="Contact" aria-label="Medium">
                                                </div>
                                                 <div class="uk-width-1-2@s">
                                                    <label class="uk-form-label">Address</label>
                                                       
                                                     <textarea class="textarea textarea-solid max-w-full" placeholder="Address" rows="4" id="kin_address" name="kin_address"></textarea>
                                                     </div>
                                                
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                <p class="uk-text-right">
                                    <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                                    <button 
                                        class="uk-button uk-button-primary" 
                                        type="button"
                                        hx-post="/newworker"
                                        hx-target="#dash_message"
                                        
                                        >Save</button>
                                </p>
                                </form>
                            </div>
                        </div>
            
            """
        except Exception as e:
            yield f"""<div class="uk-alert-warning" uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <p>{str(e)}</p>
                        </div>                       
                       
                        
                    """
            
        finally:
            del(e)


    async def html_eworker(self, id:str=None):
        e = await get_worker(id=id)
    
        return f"""
                        <div>
                        <div class="navbar">
                            <div class="navbar-start">
                                <div class="avatar">
                                    <img src="{e.get('imgurl')}" alt="avatar" />
                                </div>
                                 <a class="navbar-item">{e.get('oc')}</a>
                                 <a class="navbar-item"><span class="uk-badge">{e.get('_id')}</span></a>
                            </div>
                            <div class="navbar-end">
                                <a class="navbar-item">Home</a>
                                <a class="navbar-item">About</a>
                                <a class="navbar-item">Contact</a>
                                 <a class="navbar-item">Account</a>
                                  <a class="navbar-item">Jobs</a>
                                  <a class="navbar-item">Tasks</a>
                                  <a class="navbar-item" href="#jobs">Jobs</a>
                                  <a class="navbar-item">Days </a>


                            </div>
                        </div>

                            <div class="flex flex-row py-5 pv-5 space-y-1.5">
                            <div class="avatar avatar-xl avatar-square">
                                <img class="w-32" src="{e.get('imgurl')}" alt="avatar" />
                            </div>
                               
                                <div class="bg-gray-300 p-5 border rounded">{e.get('address')}</div>
                                </div
                                <div class="flex flex-col space-y-1.5">
                                <div id="worker-console" class="bg-gray-300 p-5 border rounded">{e}</div>
                                
                                </div>
                        </div>
                        """
                        

    async def html_worker(self, id:str=None):
        e = await get_worker(id=id)
    
        return f""" <div>
        <div class="navbar">
            <div class="navbar-start">
                <div class="avatar">
                    <img src="{e.get('imgurl')}" alt="avatar" />
                </div>
                <a class="navbar-item">{e.get('oc')}</a>
                <a class="navbar-item"><span class="uk-badge">{e.get('_id')}</span></a>
            </div>
            <div class="navbar-end">
                <ul class="uk-subnav uk-subnav-pill" uk-switcher="connect: #my-id">
    
                    <li><a href="#" class="navbar-item">Home</a></li>
                    <li><a href="#" class="navbar-item">Account</a></li>
                    <li><a href="#" class="navbar-item">Jobs</a></li>
                    <li><a href="#" class="navbar-item">Tasks</a></li>                                  
                    <li><a href="#" class="navbar-item">Days </a></li>
                </ul>
            </div>
        </div>

        <div id="my-id" class="uk-switcher uk-margin">
            <div id="home">
                <div id="worker-console" class="bg-gray-300 p-5 border rounded">
                 <div id="about">
                    <div class="bg-gray-300 p-5 border rounded">{e.get('address')}</div>
                                                
                    </div>
                    <div id="contact">
                    <div class="bg-gray-300 p-5 border rounded">{e.get('contact')}</div>
                </div>
                
                {e}
                
                </div>
                                        
            </div>
            
            <div id="account">{e.get('account')}</div>
            <div id="jobs">{e.get('jobs')}</div>
            <div id="tasks">{e.get('tasks')}</div>
            <div id="days">{e.get('days')}</div>

            
        </div>

                            

                        </div>
                        """
                        







