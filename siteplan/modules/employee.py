#modeler.py
import json
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse, StreamingResponse

from database import Recouch
try:
    from modules.utils import timestamp
except Exception as e:
    from utils import timestamp

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
                self.generate_id()

    async def all(self):
        try:
            return await self.conn.get(_directive="_all_docs") 
        except Exception as e:
            return {"error": str(e)}

    async def all_workers(self):
        try:
            return await self.slave.get(_directive="_design/workers/_view/name-index") 
        except Exception as e:
            return {"error": str(e)}

    async def get_worker(self, id:str=None):
        self.worker = await self.conn.get(_directive=id) 
        #self.processAccountTotals 
        return self.worker
    

    async def get_worker_info(self, id:str=None):
        self.worker = await self.conn.get(_directive=id) 
        worker = json.loads(json.dumps(self.worker))
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
                self.worker["jobs"] = []
                await self.save(data=self.worker)
            worker["days"] = len(worker["days"])
            worker["reports"] = len(worker["reports"])
            #self.processAccountTotals 
            return worker
        finally:
            del(worker)



    async def save(self, data:dict=None):
        self.mount(data=data)
        from asyncio import sleep
        try:
            self.data['imgurl'] = f"static/imgs/workers/{self._id}.png" 
            await self.conn.post( json=self.data)
            await sleep(1)
            self.data['_id'] = self._id                      
            await self.slave.post( json=self.data)                    
            return self.data
        except Exception:
            return {"status": str(Exception)}
        finally: del sleep


    async def update(self, data:dict=None):   
            
        try:
            payload =  await self.conn.put( json=data)
            
            return payload

        except Exception as e:
            return {"error": str(e)}
        finally: pass
        

    async def delete(self, id:str=None):
        worker = await self.get_worker(id=id)
        try:
            res = await self.conn.delete(_id=f"{id}?rev={worker.get('_rev')}")
            return res
        except Exception as e:
            return {"status": str(e)}
        finally:
            del(res); del(worker)       


    async def get_name_index(self):    
        employees =  await self.all_workers()
        employees = employees.get('rows')  
        return [{"name": item.get('value').get('name'), "id": item.get('id')} for item in employees]
        

    async def get_by_name(self, name:str=None) -> dict:
        index = await self.get_name_index()
        id = [item.get('id') for item in index if item.get('name') == name]
        if len(id) > 0:
            id=id[0]
        return await self.get_worker(id=id)
    

    def generate_id(self):
        ''' Generates a unique Worker id, also updates the worker data''' 
        from modules.utils import GenerateId       
        gen = GenerateId()
        try:
            ln = self.data.get('name').split(' ')
            self._id =  gen.name_id(ln=ln[1], fn=self.data.get('name'))   
                
            self.data['_id'] = f"{self.data.get('occupation')}s:{self._id}"    
            self.data[f"{self.data.get('occupation')}_id"] = f"{self.data.get('occupation')}s"                                
        except:
            self._id = gen.name_id('C', 'W')
                
            self.data['_id'] = f"{self.data.get('occupation')}s:{self._id}"    
            self.data[f"{self.data.get('occupation')}_id"] = f"{self.data.get('occupation')}s"
        finally:           
            del(gen)
            del(GenerateId)
    

    async def process_days_work(self, name:str=None, date_id:str=None, paid:bool=False, amount:float=None):        
        employee = await self.get_by_name(name=name)
        for daywork in employee.get('days'):
            if daywork.get('id') == date_id:
                daywork['payment']['amount'] = amount
                daywork['payment']['paid'] = paid
        await self.update(data=employee)
        



    @property
    def processAccountTotals(self):
        #function to process pay 
        def processPay(p):
            return p['total']
        self.worker['account']['totals_payments'] = list(map(processPay, self.worker['account']['payments']))   
        self.worker['account']['total'] = sum(self.worker['account']['totals_payments'])   
        

    async def addPay(self, id=None, data=None):       
        try:        
            #get the worker's data
            await self.get_worker(id=id)        
            self.worker['account']['payments'].append(data) 
            self.processAccountTotals        
            await self.update(data=self.worker)
            return self.worker.get('account').get('payments')       
            
        except Exception as ex:
            return {"status": str(ex)}
        
    async def deletePay(self, id:str=None, data:dict=None):
        await self.get_worker(id=id)
        try:
            self.worker['account']['payments'].remove(data)
            await self.update(data=self.worker)
            return self.worker.get('account').get('payments') 
        except Exception as e:
            return str(e)


    async def addJobTask(self, id=None, data=None): 
        '''Assign a task from a job to a worker
            --- Returns a list of tasks of the said job asigned to the worker'''
        
        try:        
            #get the worker's data
            await self.get_worker(id=id)                   
            self.worker['tasks'].append(data)                   
            await self.update(data=self.worker) 
            idds = data.split('-')   
                    
            def process_job_tasks(item):
                if f"{idds[0]}-{idds[1]}" in item:
                    return item
            jobtasks = list(map(process_job_tasks, self.worker.get('tasks')))
            return {"worker": id, "job": f"{idds[0]}-{idds[1]}", "tasks": jobtasks}
            
        except Exception as ex:
            return {"status": str(ex)}
        
    async def submitDayWork(self, eid:str=None, data:dict=None)-> list:
        '''Returns the list of days worked'''
        e = await self.get_worker(id=eid)
        #print(e)
        e['days'].append(data)
        await self.update(data=e)
        return e.get('days')
    
    
    # Html Responses
    async def team_index_generator(self):
        e = await self.all_workers()
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
        e = await Employee().get_worker(id=id)
    
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
        e = await Employee().get_worker(id=id)
    
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
                        







