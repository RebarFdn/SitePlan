#coding=utf-8
#project.py


# Logging
import json

#from pympler import asizeof
from modules.utils import timestamp
from database import Recouch, RedisCache
from modules.employee import Employee
from schemas.schema_api import project_schema as schema, validate
from config import DOCUMENT_PATH, IMAGES_PATH
from config import SYSTEM_LOG_PATH as SYSTEM_LOG, APP_LOG_PATH as APP_LOG
from logger import logger
import datetime


class Project: 
    error_log:dict = {}   
    projects:list=[]    
    meta_data:dict = {
        "created": 0, 
        "database": {"name":"site-projects", "partitioned": False},              
    }
    instances = 0
    default_fees = {
        "contractor": 20,
        "insurance": 0,
        "misc": 0,
        "overhead": 0,
        "unit": "%"
    }

    def __init__(self, data:dict=None): 
        Project.instances += 1      
        self.conn = Recouch(local_db=self.meta_data.get('database').get('name'))
        self._id:str = None        
        self.index:set = set()
        self.project:dict = {}
        if data :
            self.meta_data["created"] = timestamp()  
            self.meta_data["created_by"] = data.get('created_by')
            self.meta_data['properties'] = list(data.keys())    
            del(data['created_by'])      
            self.data = data
            self.data["meta_data"] = self.meta_data
                      
            if self.data.get("_id"):
                pass
            else:
                self.generate_id(local=True)
        else:                     
            self.data = {"meta_data":self.meta_data}
        self.document = {
            "style": {
                'margin_bottom': 15,
                'text_align': 'j',
                 "page_size": "letter", 
                 "margin": [60, 50]
            },
            "formats": {
                'url': {'c': 'blue', 'u': 1},
                'title': {'b': 1, 's': 13},
                'title_header': {'b': 1, 's': 16},
                'sub_title': {'b': .5, 's': 11},
                'sub_text': {'s': 9}
            },
            "running_sections": {
                "header": {
                    "x": "left", "y": 20, "height": "top", "style": {"text_align": "r"},
                    "content": [{".b": "This is a header"}]
                },
                "footer": {
                    "x": "left", "y": 740, "height": "bottom", "style": {"text_align": "c"},
                    "content": [{".": ["Page ", {"var": "$page"}]}]
                }
            },
            "sections": []
        }

    @property    
    def report_error(self):
        return self.error_log
    
    @property
    def projectPhases(self):
        return {      
            'preliminary':'Preliminary',
            'substructure': 'Substructrue',
            'superstructure': 'Superstructure',
            'floors': 'Floors',
            'roofing': 'Roofing',
            'installations': 'Installations',
            'electrical': 'Electrical',
            'plumbung': 'Plumbing',
            'finishes': 'Finishes',
            'landscaping': 'Landscaping',      
        
        }
    

    @property
    def withdrawal_model(self):
        return   {
          "id": None,
          "date": None,
          "type": "Withdraw",
          "amount": 0,
          "recipient": {
            "name": None,
          },
          "ref": None
        }
    

    @property
    def salary_statement_model(self):
        return  {
          "ref": None,
          "jobid": None,
          "employeeid": None,
          "name": None,
          "date": None,
          "items": [],
          "deductions": [],
          "total": 0
        }
    

    @property
    def salary_statement_item_model(self):
        return  {
              "id": None,
              "description": None,
              "unit": None,
              "amount": 0,
              "price": 0,
              "total": 0
            }


    @property
    def data_validation_error(self):
        self.meta_data["created"] = timestamp()
        self.meta_data['flagged'] = {
            "message": "There was an error in your data, please rectify and try Mounting it again.",
            "flag": self.report_error
        }

    def validate_data(self, data, schema):
        try:
            validate(instance=data, schema=schema)
            return True
        except Exception as e:
            self.error_log['data_validation'] = str(e)
            self.data_validation_error   
            return False

    def setup(self):
        """is called after data has been mounted """
        check_list = self.meta_data.get("properties")
        self.process_address()
        if "owner" in check_list: pass
        else: self.data['owner'] = {
            "name": None,
            "contact": None,
            "address": {"lot": None, "street": None, "town": None,"city_parish": None,"country": None, }
        }
        if "account" in check_list: pass
        else: self.data['account'] = {
                "bank": {
                    "name": None,
                    "branch": None,
                    "account": None,
                    "account_type": None
                    },
                "budget": None,
                "ballance": 0,
                "started": timestamp(),
                "transactions": {
                    "deposit": [], 
                    "withdraw": []
                },
                "expences": [],
                "records": {
                    "invoices": [],
                    "purchase_orders": [],
                    "salary_statements": [],
                    "paybills": []
                }
            }
        if "tasks" in check_list: pass
        else:self.data['tasks'] = [] 
        if "workers" in check_list: pass
        else:self.data['workers'] = [] 
        if "inventory" in check_list: pass
        else:self.data['inventory'] = [] 
        if "activity_log" in check_list: pass
        else:self.data['activity_log'] = [] 
        self.process_event()
        self.process_state()
        self.meta_data['properties'] = list(self.data.keys())
        self.meta_data['properties'].remove('meta_data')

    def runsetup(self):
        """is called after data has been mounted """
        
        PROJECT_TEMPLATE = dict( 
            name = None,
            category = "residential",
            standard = "metric",
            address = {"lot": None, "street": None, "town": None,"city_parish": None,"country": "Jamaica", },
            owner = {
            "name": None,
            "contact": None,
            "address": {"lot": None, "street": None, "town": None,"city_parish": None,"country": None, }
        },
            account = {
                "bank": {
                    "name": None,
                    "branch": None,
                    "account": None,
                    "account_type": None
                    },
                "budget": None,
                "ballance": 0,
                "started": timestamp(),
                "transactions": {
                    "deposits": [], 
                    "withdraw": []
                },
                "expences": [],
                "records": {
                    "invoices": [],
                    "purchase_orders": [],
                    "salary_statements": [],
                    "paybills": []
                }
            },
            admin = {
            "leader": None,
            "staff": {
            "accountant": None,
            "architect": None,
            "engineer":None,
            "quantitysurveyor": None,
            "landsurveyor": None,
            "supervisors": []
            }
  },
            workers = [],
            tasks = [],
            rates = [],
            daywork = [],
            inventory = [],            
            event = {
                "started": 0,
                "completed": 0,
                "paused": [],
                "restart": [],
                "terminated": 0
            },
            state =  {
                "active": False,
                "completed": False,
                "paused": False,
                "terminated": False
            },      
            progress =  {
            "overall": None,
            "planning": None,
            "design": None,
            "estimates": None,
            "contract": None,
            "development": None,
            "build": None,
            "unit": None
            },
            activity_log = [],
            reports = [],
            estimates = [],
            meta_data = None
            
              )
        #self.data.update(PROJECT_TEMPLATE | self.data)
        self.data = PROJECT_TEMPLATE | self.data 
        self.meta_data['properties'] = list(self.data.keys())
        self.meta_data['properties'].remove('meta_data')


    def mount(self, data:dict=None): 
        #remove fragments from previous validation
        if self.meta_data.get('flagged'): del self.meta_data['flagged']       
        if data and self.validate_data(data, schema):
            self.meta_data["created"] = timestamp()
            self.meta_data['properties'] = list(data.keys())
            self.data = data            
            self.data['meta_data'] = self.meta_data
            if self.data.get("_id"):
                pass
            else:
                self.generate_id(local=True)

    # Utilities
    def as_currency(self, amount):
            if amount >= 0:
                return '${:,.2f}'.format(amount)
            else:
                return '-${:,.2f}'.format(-amount)

    ## CRUD OPERATIONS
    async def all(self):
        try:
            r = await self.conn.get(_directive="_design/project-index/_view/name-view") 
            return r           
        except Exception as e:
            return str(e)
        finally: del(r)

    async def all_raw(self):
        try:
            r = await self.conn.get(_directive="_design/project-index/_view/all-raw") 
            return r           
        except Exception as e:
            return str(e)
        finally: del(r)

    async def nameIndex(self):
        def processIndex(p):
            return  p.get('value')
        try:
            r = await self.conn.get(_directive="_design/project-index/_view/name-view") 
            return list(map( processIndex,  r.json().get('rows')))            
        except Exception as e:
            return str(e)
        finally: del(r)


    async def get(self, id:str=None):
        r = None
        try:
            r = await self.conn.get(_directive=id)

            logger().info(f'Request for Project {r.get("_id")} Completed sucessfully.')
            return r
        except Exception as e:
            logger().error(str(e))
            return str(e)
        finally: del(r)  


    async def save(self):        
        #self.mount(data=data)
        #self.setup()        
        await self.conn.post( json=self.data )  
        logger().info('New project created ')        
        return  self.data    
        

    async def update(self, data:dict=None):
        try:
            logger().info(f'Project {data.get("_id")} updated.')
            return await self.conn.put( json=data)            
        except Exception as e:
            logger().error(str(e))
            return str(e)
        

    async def delete(self, id:str=None):
        status = None
        try:
            status = await self.conn.delete(_id=id)
            return {"status": status}
        except Exception as e:
            return str(e)
        finally:
            del(status)


    async def get_elist(self):
        await self.all_projects()
        return self.projects 

    def generate_id(self, line_1:str=None, line_2:str=None, local:bool=None ):
        ''' Generates unique id's also may update the project data
            may also return a generator function 
            ---
            requires: 
                line_1: a char or string of chars.
                line_2: ditto above,
                local: True or False
            returns a generator function if no argument is provided
        ''' 
        from modules.utils import GenerateId       
        gen = GenerateId() 
        # Case_1: generate id for other
        if line_1 and line_2: 
            try:            
                return  gen.name_id(ln=line_1, fn=line_2) 
            except Exception as ex:
                return str(ex)
            finally:
                del(gen)
                del(GenerateId) 
        # Case_2: generate id locally               
        elif local: 
            try:            
                self._id = gen.name_id(
                    ln=self.data.get('name').split(' ')[1], 
                    fn=self.data.get('name')
                    ) 
                self.data['_id'] = self._id
            except Exception as ex:
                return str(ex)
            finally:                
                del(gen)
                del(GenerateId) 
        # Case_3: return the generator               
        else:
            try:
                return gen
            finally: 
                del(gen)
                del(GenerateId)


    def update_index(self, data:str) -> None:
        '''  Expects a unique id string ex. JD33766'''        
        self.index.add(data) 


    @property 
    def list_index(self) -> list:
        ''' Converts set index to readable list'''
        return [item for item in self.index]
   
    
    ## PROJECT ACCOUNTING
    async def handleTransaction(self, id:str=None, data:dict=None):
        if data:
            gen = self.generate_id()
            project = await self.get(id=id)
            data['id']= gen.gen_id(doc_tag='item')
            # process deposits
            if data.get('type') == 'deposit' or data.get('type') == 'Deposit':                
                project['account']['transactions']['deposit'].append(data)
                project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": f"Add Account {data.get('type')}",
                        "description": f"""Account {data.get('type') } with Refference {data.get('ref')} was added to Project  {project.get('_id')}
                        Account Transactions by { data.get('user') } at { timestamp() }"""
                    }

                )  
                
                #processProjectAccountBallance()
                project['account']['updated'] = timestamp()
            # process withdrawals
            if data.get('type') == 'withdraw' or data.get('type') == 'Withdraw':               
                project['account']['transactions']['withdraw'].append(data)
                project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": f"Add Account {data.get('type')}",
                        "description": f"""Account {data.get('type') } with Refference {data.get('ref')} was added to Project  {project.get('_id')}
                        Account Transactions by { data.get('user') }"""
                    }

                )  
                #processProjectAccountBallance()
                project['account']['updated'] = timestamp()
            try:
               
                await self.update(data=project)
                return data
            except Exception as e:
                return {'error': str(e)}
            finally:
                del(gen)
                del(project) # clean up
        else:
            return {"error": 501, "message": "You did not provide any data for processing."}

    async def addInvoice(self, id:str=None, data:dict=None):        
        project = await self.get(id=id)
        project['account']['records']['invoices'].append(data)
        try:
            await self.update(data=project)    
            return data         
        except Exception as e:
            return {'error': str(e)}
        finally:
            del(project)

    
    async def deleteInvoice(self, id:str=None, data:dict=None):        
        project = await self.get(id=id)
        project['account']['records']['invoices'].remove(data)
        try:
            return await self.update(data=project)            
        except Exception as e:
            return {'error': str(e)}
        finally:
            del(project)

    async def getInvoices(self, id:str=None):        
        project = await self.get(id=id)
        try:
            return project.get('account').get('records').get('invoices')
        except Exception as e:
            return str(e) 
        finally:
            del(project)


    # Project Expences
    async def addExpence(self, id:str=None, data:dict=None):        
        project = await self.get(id=id)
        project['account']['expences'].append(data)
        try:
            await self.update(data=project) 
            return project.get('account').get('expences')         
        except Exception as e:
            return {'error': str(e)}
        finally:
            del(project)

    async def getExpences(self, id:str=None):        
        project = await self.get(id=id)
        try:
            return project.get('account').get('expences')
        except Exception as e:
            return str(e) 
        finally:
            del(project)

    
    async def deleteExpence(self, id:str=None, data:dict=None):        
        project = await self.get(id=id)
        project['account']['expences'].remove(data)
        try:
            await self.update(data=project) 
            return project.get('account').get('expences')         
        except Exception as e:
            return {'error': str(e)}
        finally:
            del(project)


    # Worker Salary Record
    async def addWorkerSalary(self, id:str=None, data:dict=None):        
        project = await self.get(id=id) 
        withdraw =  {
                "id": data.get("ref"),
                "date": data.get("date"), 
                "type":"withdraw",            
                "amount": data.get("total"), 
                "ref": data.get("ref"),
                "recipient": {
                    "name": data.get("name")
                }
            } 
        project['account']['transactions']['withdraw'].append(withdraw)      
        project['account']['records']['salary_statements'].append(data)
        
        try:
            e = Employee()
            pb = await e.addPay(id=data.get('employeeid'), data=data )       
            #print(project['account']['records']['salary_statements'])
            #print(pb)
            await self.update(data=project) 
            return project.get('account').get('records').get('salary_statements')         
        except Exception as e:
            return {'error': str(e)}
        finally:
            del(project)

    async def deleteWorkerSalary(self, id:str=None, data:dict=None):
        ## get the project

        # get the account transactions and records 
        # find and remove the salary_statement in question
        # find and remove the withdrawal record from account transactions withdral
        # update the project 
        pass

    # Project Paybill Management
    async def create_new_paybill(self, id:str=None, data:dict=None):
        p = await self.get(id=id)
        data['ref'] = f"{id}-Bill-{len( p['account']['records']['paybills']) + 1 }"
        p['account']['records']['paybills'].append(data)
        await self.update(data=p) 
        return data
    

    async def add_bill_item(self, id:str=None, data:dict=None):
        idd = id.split('-')
        project = await self.get(id=idd[0])
        
        try:
            bill =[item for item in  project['account']['records']['paybills'] if item.get("ref") == id ][0]
            item_ids = []
            
            if len(bill['items']) > 0:
                for bill_item in bill.get('items'):  
                    item_ids.append(bill_item.get('id'))               

                if data.get('id') in item_ids:
                    print('BILL-item is already included in Pay Bill')
                        
                    return None
                else:
                    print(f"BILL-item will be added to the pay bill ....{data.get('id')}")
                    bill['items'].append(data)
                    await self.update(data=project)
                    return data 
        
            else:
                print('New BILL-item will be added to the Pay bill')
                bill['items'].append(data)
                await self.update(data=project)
                return data
               
        except Exception as e:
            return str(e)
        finally:
            print(data)
            print('ID', id)
           
    
    ## PROJECT WORKERS
    async def addWorkers(self, id:str=None, data:list=None):
        '''Requires a list of workers. Enshure the following JSON data format
            {
            "id": "LT0000",
            "key": "LT0000",
            "value": {
                "name": "Love True",
                "oc": "truelove",
                "occupation": "labourer",
                "added": 1664197078000
            }
            },
        '''
        if data:
            def enlist(item): # utility sort function
                return item['id']               
            project = await self.get(id=id)
            workers = list(map(enlist, project['workers'])) 
            updated = None
            for item in data:
                if item.get('id') in workers:
                    pass
                else:
                    project['workers'].append(item )
            try:
                updated = await self.update(data=project)
                return updated
            except Exception as e:
                return {'error': str(e)}
            finally:
                del(updated)
                del(item)
                del(workers)
                del(project)
        else:
            return {"error": 501, "message": "You did not provide any data for processing."}

    async def process_workers(self, index:list=None) -> dict:
        try:
            employees = []
            e = Employee()
            if len(index) > 0:
                for eid in index: 
                    worker = await e.get_worker(id=eid)
                    employees.append(worker)             
                return {"employees": employees} 
            else: return {"employees": []}                     
        except Exception as er:
            return str(er)
        finally: 
            del(employees)
            del(e)

    ## PROJECT INVENTORY 
    def sortInventory(self, keywords, datalist):
        def sort(item):
            keyword = item.get('item')
            for word in keywords:
                if word in keyword:
                    return None
                else: return item


    async def addInventory(self, id:str=None, data:list=None):
        if data:                          
            project = await self.get(id=id)  
            # check if this material inventory exists 
            # if not add it 
            project['inventory'].append(data)
        else:
            pass
        return project.get('inventory')
    
    async def addInventoryItem(self, id:str=None, data:list=None):
        if data:                          
            project = await self.get(id=id)  
            # check if this material inventory exists 
            # if not add it 
            project['inventory'].append(data)
        else:
            pass
        return project.get('inventory')

    ## PROJECT RATES
    async def addRate(self, id:str=None, data:list=None):
        if data:                          
            project = await self.get(id=id)         
            for item in data:
                item['_id'] = f"{id}-{item['_id']}"                
                project['rates'].append( item )
            try:
                await self.update(data=project)
                return project
            except Exception as e:
                return {'error': str(e)}
            finally:
                del(item)
                del(project)
        else:
            return {"error": 501, "message": "You did not provide any data for processing."}


    async def updateRate(self, id:str=None, data:list=None):
        if data:                          
            project = await self.get(id=id)         
            for item in data:
                item['_id'] = f"{id}-{item['_id']}"                
                project['rates'].append( item )
            try:
                await self.update(data=project)
                return project
            except Exception as e:
                return {'error': str(e)}
            finally:
                del(item)
                del(project)
        else:
            return {"error": 501, "message": "You did not provide any data for processing."}


    async def getRateById(self, id:str=None):
        idds = id.split('-') 
        def findData(rate): # utility search function
            return rate['_id'] == id
        project = await self.get(id=idds[0])
        try:
            return { "subject": project.get('name'), "id": idds[0], "rate": list(filter(findData, project.get('rates')))[0]}
        except Exception as e:
                return {'error': str(e)}
        finally:
                del(idds)
                del(project)

    async def getRate(self, rate_id:str=None):
        ''''Retreives a rate from the project. 
        Requires the assigned rate id '''
        try:            
            ends = rate_id.split('-')
            def findRate(rate): # utility search function 
                return rate['_id'] == rate_id        
            project = await self.get(id=ends[0])                 
            rate = list(filter( findRate, project.get('rates') ))
            return rate[0]
        except Exception as e:
            return {'error': str(e)}


    async def getEmployeeRates(self, pe_id:str=None):
        ''''Retreives a batch of rates assigned to the employee  from the project. 
        Requires the project id and the employee id'''
        try:            
            ends = pe_id.split('-')                
            def findRates(rate): # utility search function
                return rate['assignedto'] == ends[1]
            project =  await self.get(id=ends[0]) 
            rates = list(filter( findRates, project.get('rates') ))
            return rates
        except Exception as e:            
            return {'error': str(e)}
        finally:
            del(ends)
            del(rates)
            del(project) 


    ## PROJECT JOBS
    async def submitDayWork(self, id:str=None, data:dict=None)-> list:
        '''Returns the list of days worked'''
        p = await self.get(id=id)
        #print(e)
        p['daywork'].append(data)
        await self.update(data=p)
        return p.get('daywork')

    async def getJob(self, id:str=None, jobs:list=None):        
        def find_item(item):
                return item['_id'] == id
        try:
            return list(filter(find_item, jobs))[0]
        except Exception as e: return str(e) 
        

    async def addJobToQueue(self, id:str=None, data:dict=None):
        ''' Add a new job to the project jobs queue. returns the updated jobs queue'''
        if data:                          
            project = await self.get(id=id) 
            flg = data.get('title', 'p j')
            flg = flg.split(' ')
            jid = self.generate_id( line_1=flg[0], line_2=flg[1]) 
            data['_id'] = f"{id}-{jid}"                
            project['tasks'].append( data )
            try:
                await self.update(data=project)
                return project.get('tasks')
            except Exception as e:
                return {'error': str(e)}
            finally:
                del(flg)
                del(project)
        else:
            return {"error": 501, "message": "You did not provide any data for processing."}


    async def addTaskToJob(self, id:str=None, data:dict=None):
        '''adds a task to a job '''
        idd = id.split('-')        
        project = await self.get(id=idd[0])
        def find_item(item):
                return item['_id'] == id
        job = list(filter(find_item, project.get('tasks')))[0]         
        try:
            job['tasks'].append(data)
            logger().info(f"Task { data.get('_id')} Addedd to Job {idd[1]} on Queue {idd[0]}")        
            await self.update(project)
            return data
        except Exception as e:
            return str(e)
        finally:
            del(project)
            del(job)
            del(idd)

    async def processJobCost(self, id:str=None):
        idid = id.split('-')
        IS_METRIC = False
        project = await self.get(id=idid[0])
        if project.get('standard') == 'metric':
            IS_METRIC = True         
        def find_item(item):
            if item.get('_id') == id:
                return item
        job = list(filter(find_item, project.get('tasks')))[0]
        job['progress'] = 0        
        def process_task(task):
            ''''''
            # Process metric rates
            if IS_METRIC:
                metric = task.get('metric')
                cost = metric.get('cost')
                price = metric.get('price')
                quantity = metric.get('quantity')
                # Check and Validate type
                if cost: ## type is string convert to float 
                    if type(cost) == str: task['metric']['cost'] = float(cost)
                else: task['metric']['cost'] = 0.001  ## value is None give a small value   
                if price:  
                    if type(price) == str: task['metric']['price'] = float(price)
                else: task['metric']['price'] = 0.001 
                if quantity:  
                    if type(quantity) == str: task['metric']['quantity'] = float(quantity)
                else: task['metric']['quantity'] = 0.001  
                   
                task['metric']['cost'] = task.get('metric').get('price') * task.get('metric').get('quantity')
                job['cost']['task'] += float(task.get('metric').get('cost')) 
                job['progress'] += float(task.get('progress'))
                output = task.get('output').get('metric', 1)
                # Chech and Validate type
                if type(output) == None: output = 0.00001
                elif type(output) == str: output = float(output)
                # check for zero value
                if output < 1: output = 0.00001               
                task['duration'] = round(task.get('metric').get('quantity', 1) / float(output),2)
                if 'total' in list(task.get('metric').keys()): del(task['metric']['total'])
                else: pass
            # Handle task reassignment
            if task.get('assignedto') == job.get('crew').get('name'):
                task['assignedto'] = None
                task['assigned'] = False 
            elif not task.get('assignedto'):
                pass
            else: task['duration'] = task['duration'] / len( task['assignedto'])    
        # Generator       
        tasks = list(map( process_task,  job.get('tasks') ))
        # Process job costs
        job['cost']['contractor'] =  (float(job.get('fees').get('contractor', 0.0001)) / 100) * job.get('cost').get('task', 0)  
        job['cost']['misc'] =  (float(job.get('fees').get('misc', 0.0001)) / 100) * job.get('cost').get('task', 0)  
        job['cost']['insurance'] =  (float(job.get('fees').get('insurance', 0.0001)) / 100) * job.get('cost').get('task', 0) 
        job['cost']['overhead'] =  (float(job.get('fees').get('overhead', 0.0001)) / 100) * job.get('cost').get('task', 0) 
        total_costs = [
            job.get('cost').get('contractor'),
            job.get('cost').get('misc'),
            job.get('cost').get('insurance'),
            job.get('cost').get('overhead'),
            job.get('cost').get('task', 0)
        ]
        job['cost']['total'] = sum(total_costs)
       
        fee_percents = [
            float(job.get('fees').get('contractor', 0)),
            float(job.get('fees').get('misc', 0)),
            float(job.get('fees').get('insurance', 0)),
            float(job.get('fees').get('overhead', 0))

        ]
        job['fees']['job'] = 100 - sum(fee_percents)
        fee_percents.append(
            job.get('fees').get('job')
        )
        # Analytical Data 
        job['analytics'] = {
            "feePercents": fee_percents,
            "costTotals": total_costs,
            'jobCosts': {
                "title": f"Job Costs Disbursement",
                "legend": [
                    "Contractor",
                    "Miscellaneous",
                    "Insurance",
                    "Overheads",
                    "Job"
                    ],
                "series": [
                    {
                        "name": f"{job.get('_id')} Renumeration",
                        "type": "pie",
                        "radius": "55%",
                        "center": ["50%", "60%"],
                        "data": [
                            {"value": job.get('cost').get('contractor'), "name": "Contractor"},
                            {"value": job.get('cost').get('misc'), "name": "Miscellaneous"},
                            {"value": job.get('cost').get('insurance'), "name": "Insurance"},
                            {"value": job.get('cost').get('overhead'), "name": "Overheads"},
                            {"value": job.get('cost').get('task'), "name": "Job"}
                        ]
                    }
                ],
                "emphasis": {
                    "itemStyle": {
                    "shadowBlur": 10,
                    "shadowOffsetX": 0,
                    "shadowColor": "rgba(0, 0, 0, 0.5)"
                    }
                }

            }
        }
        tasks = len(job.get('tasks'))
        if tasks > 0:
            job['progress'] = job['progress'] / tasks
        else: pass
        return job
    

    async def updateJobTasks(self, id:str=None, tasks:list=None)-> list:
        '''Rplaces the projects job tasks list '''
        idd = id.split('-')
        p = await self.get(id=idd[0]) # locate the project
        job = await self.getJob(id=id, jobs=p.get('tasks'))  # locate the job
        job['tasks'] = tasks
        await self.update(data=p)
        return job.get('tasks')

    async def updateJobTask(self, id:str=None, data:dict=None)-> dict:
        '''Updates a single job task of the project'''
        print(id)
        idd = id.split('-')
        p = await self.get(id=idd[0]) # locate the project
        job = await self.getJob(id=id, jobs=p.get('tasks'))  # locate the job
        #job['tasks'] = tasks
        #await self.update(data=p)
        for item in job.get('tasks'):
            if item.get('_id') == data.get('_id'):
                print('F O U N D')
                job['tasks'][job['tasks'].index(item)] = data
                await self.update(data=p)
                
        return data

    
    ## PROJECT JOB CREW    
    async def getProjectCrews(self, id:str=None):
        ''' return a list of job crews employed to a project'''          
        project = await self.get(id=id)
        crews, names = [], [] 
        def find_item(item):
            if item.get('crew').get('name') not in names:
                names.append(item.get('crew').get('name'))
                crews.append(item.get('crew'))
            return item['crew']
        crews_ = list(map(find_item, project.get('tasks')))
        # remove duplicates
        return crews
    
    async def addCrewMember(self, id:str=None, data:dict=None):
        '''Assigns a single  member to the job's crew members list'''
        idd = id.split('-')
        p = await self.get(id=idd[0]) # locate the project

        job = await self.getJob(id=id, jobs=p.get('tasks'))  # locate the job
        
        try:
            job['crew']['members'].append(data)            
            await self.update(p)
            return data
        except Exception as e: return str(e)

    async def addCrewMembers(self, id:str=None, data:list=None):
        '''Assigns members from a list to the job's crew members list'''
        idd = id.split('-')
        p = await self.get(id=idd[0]) # locate the project

        job = await self.getJob(id=id, jobs=p.get('tasks'))  # locate the job
        
        try:
            for member in data:
                job['crew']['members'].append(member)
            
            await self.update(p)
            return job
        except Exception as e: return str(e)


    async def assignTaskToCrewMember(self, id:str=None, wid:str=None):
        '''Assigns a tasks of a number tasks to a crew member'''
        idd = id.split('-')
        p = await self.get(id=idd[0]) # locate the project
        job = await self.getJob(id=f"{idd[0]}-{idd[1]}", jobs=p.get('tasks'))  # locate the job
        
        # process Job task 
        def find_task(task):
            if task.get('_id') == id:
                return task
        task = list(filter(find_task, job.get('tasks')))[0]
        task['assigned'] = True
        if type(task['assignedto']) == str:
            task['assignedto'] = [wid]
        elif not task.get('assignedto'): 
            task['assignedto'] = [wid]
        else:
            task['assignedto'].append(wid)

        # process employee tasks
        def find_worker(worker):
            if worker.get('id') == wid:
                return worker
        worker = list(filter(find_worker, job.get('crew').get('members')))[0]
        
        e = Employee()
        employee_assigned_jobtasks = await e.addJobTask(id=f"{worker.get('occupation')}s:{wid}", data=id)

        worker['tasks'] = employee_assigned_jobtasks.get('tasks')
        try:
            
            await self.update(data=p)
            return job.get('tasks')
        except Exception as e: return str(e)

    async def administerTaskProgress(self, id:str=None, data:int=None):
        ''' Advances the task progress'''
        idd = id.split('-')
        p = await self.get(id=idd[0]) # locate the project
        job = await self.getJob(id=f"{idd[0]}-{idd[1]}", jobs=p.get('tasks'))  # locate the job
        def find_task(task):
            if task.get('_id') == id:
                return task
        task = list(filter(find_task, job.get('tasks')))[0]
        task['progress'] = data
        try:            
            await self.update(data=p)
            return {
                "tasks":job.get('tasks'),
                "analytics": await self.JobProgressAnalytics(job=job)
            }
        except Exception as e: return str(e)

    async def JobProgressAnalytics(self, job:dict=None):
        def get_ids(item):
            idd = item.get('_id').split('-')
            return f"{idd[1]}-{idd[2]}"
        task_ids = list(map(get_ids, job.get('tasks')))
        task_progress = [task.get('progress') for task in job.get('tasks')]

        return {
            "tasks_ids": task_ids,
            "progress": task_progress
        }
    
    async def getProjectWorkerData(self, id:str=None):  
        worker_data = {
                "project": None,
                "employee_id": None,
                "worker": None,               
                "tasks": None,
                "paybills": None,
                "payments ": None 

            }
        if id:
            access_points = id.split('-')
            ap2 = access_points[1].split(':')            
            project = await self.get(id=access_points[0])
            paybills = project.get('account').get('records').get('salary_statements')
            payments = project.get('account').get('transactions').get('withdraw')
            worker = await Employee().get_worker(id=access_points[1])
            def sort_pay_bill(item):
                if item.get('employeeid') == ap2[1]:
                    return item
                
            def sort_payments(item):
                if item.get('recipient').get('name') == worker.get('name'):
                    return item

            worker_data["project"] = access_points[0]
            worker_data["employee_id"] = ap2[1]
            worker_data["worker"] = worker.get('name')               
            worker_data["tasks"] = [t for t in worker.get('tasks') if access_points[0] in t ]
            worker_data["paybills"] = list(filter(sort_pay_bill, paybills))
            worker_data["payments"] = list(filter(sort_payments, payments))
            worker_data["earnings"] = [pay.get('amount') for pay in worker_data.get("payments")]
            worker_data["pay_dates"] = [payitem.get('date') for payitem in worker_data.get("payments")]
            worker_data["total_earnings"] = sum( worker_data["earnings"] )

            
        else:
            worker_data["project"] = None,
            worker_data["employee_id"] = None,
            worker_data["worker"] = None,               
            worker_data["tasks"] = None,
            worker_data["paybills"] = None,
            worker_data["payments"] = None 

            
        try:
            return worker_data
        except Exception as e:
            return str(e) 
        finally:
            del(worker_data)
            del(worker)
            del(payments)
            del(paybills)
            del(project)
            del(ap2)
            del(access_points)
            

    ## PROJECT LOCATION AND ADDRESS MANAGEMENT
    def process_address(self):
        template = {"lot": None, "street": None, "town": None,"city_parish": None,"country": "Jamaica", }
        if 'address' in self.meta_data.get('properties'):
            check_list = list(self.data.get('address').keys())            
            for item in check_list:
                template[item] =  self.data['address'][item]
            self.data['address'] = template
        else: self.data['address'] = template

    ## PROJECT EVENTS 
    def process_event(self):
        template = {
            "started": 0,
            "completed": 0,
            "paused": [],
            "restart": [],
            "terminated": 0
        }
        if 'event' in self.meta_data.get('properties'):
            check_list = list(self.data.get('event').keys())            
            for item in check_list:
                template[item] =  self.data['event'][item]
            self.data['event'] = template
        else: self.data['event'] = template

    ## PROJECT STATE MANAGEMENT       
    def process_state(self):
        template =  {
            "active": False,
            "completed": False,
            "paused": False,
            "terminated": False
        }
        if 'state' in self.meta_data.get('properties'):
            check_list = list(self.data.get('state').keys())            
            for item in check_list:
                template[item] = self.data['state'][item]
            self.data['state'] = template
        else: self.data['state'] = template
    
    ## PROJECT PHASE MANAGEMENT
    async def update_project_job_phase(self, id:str=None, phase:str=None):
        """Updates A Job Phase """        
        idd = id.split('-')
        p = await self.get(id=idd[0])
        jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
        if len(jb) > 0:
            job = jb[0] 
            job['projectPhase'] = phase
            await self.update(data=p)
            return phase
        else:
            return None
        
        
    ## PROJECT REPORTING
    async def addJobReport(self, id:str=None, data:dict=None):
        project = await self.get(id=id)
        project['reports'].append(data)
        try:
            await self.update(data=project) 
            return data          
        except Exception as e:
            return {'error': str(e)}
        finally:
            del(project)

    async def getJobReports(self, id:str=None):
        idds = id.split('-')
        project = await self.get(id=idds[0])
        reports = project.get('reports')
        if len(reports) > 0:
            def process_report(item):
                if item.get('meta_data').get('job_id') == id:
                    return item

            try:
                return list(filter(process_report, reports))                          
            except Exception as e:
                return {'error': str(e)}
            finally:
                del(project)
        else: return []
    
    # DATA OPERATIONS 
    async def getRemoteProject(self, id:str=None):
        ''' Retrieves data from a remote server 
            returns None on network error
        '''
        import httpx
        endpoint = f"http://192.168.0.19:6757/project/{id}"
        r = None
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(endpoint)
            return r.json()
        except Exception: return None
        finally: #close connection and clean up
            if r:
                await r.aclose()
                del(r)


    async def sync_remote_data(self, id:str=None):
        ''' Sync local and remote data 
            return local data if remote is absent 

        '''
                
        remote = await self.getRemoteProject(id=id) # remote data source
        local = await self.get(id=id) # local data source
        local_rev = json.loads(json.dumps(local['_rev']))
        if remote:
            del local['_rev'] # prepare data
            del remote['_rev']
        
            if remote == local:
                return {'payload': remote}
            else:
                from deepdiff import DeepDiff
                diff = DeepDiff(local, remote, cache_size=512)

                update = local | remote
                update['_rev'] = local_rev # update data with local _rev for local storage
                await self.update(data=update)
                
                payload = {
                    'payload': update,
                    'update': {
                    'diff': list(diff.affected_root_keys),
                    'affected_path': list(diff.affected_paths),
                    'json_result': json.loads(diff.to_json())
                    }

                    }
                logger().add(SYSTEM_LOG)
                logger().info(f"{update.get('_id')} was updated. {payload.get('update')} ")
                return payload
        else:
            local['_rev'] = local_rev
            return {
            'payload': local
            }


    async def process_project_inventory(self, id:str=None):
        inventory_items = set()
        inventory = []
        inventory_set = set()
        p = await self.get(id=id) # local data source
        invoices = p.get('account').get('records').get('invoices')
        # build items set
        for invoice in invoices:
            for item in invoice.get('items'):
                inventory_items.add(item['description'])
                inventory.append(item)
                #process item set
        for inv_item in inventory:
            if inv_item.get('description') in inventory_items:
                inventory_item = {
                        "id": self.generate_id(line_1=inv_item.get('description'), line_2=inv_item.get('description')[0]),
                        "item": inv_item.get('description'),
                        "unit": inv_item.get('unit'),
                        "instock": float(inv_item.get('quantity')), 
                        "usage": [ { "date": "", "amt": 0 } ], 
                        "restock": [ { "date": "", "amt": 0 } ], 
                        "updated": timestamp()
                        
                        }
                    
                inventory_set.add(json.dumps(inventory_item))
        
        for json_obj in inventory_set:            
            p['inventory'].append(json.loads(json_obj))
        
        await self.update(data=p)    
        return {
            'inventory_log': list(inventory_items),
            'inventory': p.get('inventory')
        }

    # PRINTERS
    async def printJobQueue(self, id:str=None)-> dict:
        '''Print Job Queue 
        Creates a Pdf document of the requested Project Job Queue 
        bassed on the job's state.
        url Endpoint should be constructed with flag  as follows;
        "print_project_jobs/PROJECT_ID-active" for active Jobs
        "print_project_jobs/PROJECT_ID-completed" for completed jobs
        "print_project_jobs/PROJECT_ID-paused" for paused jobs
        "print_project_jobs/PROJECT_ID-terminated" for terminated jobs
        "print_project_jobs/PROJECT_ID-all" for all jobs
        '''
        idd = id.split('-')
        state = idd[1].strip()

        p = await self.get(id=idd[0]) # locate the project
        if state == 'all':
            job_queue = [{
                "id": i.get('_id'), 
                "title": i.get('title'), 
                "state": i.get('state'),
                "event": i.get('event'),
                "projectPhase": i.get( "projectPhase"),
            } for i in p.get('tasks') ]
        else:
            job_queue = [{
                "id": i.get('_id'), 
                "title": i.get('title'), 
                "state": i.get('state'),
                "event": i.get('event'),
                "projectPhase": i.get( "projectPhase"),
            } for i in p.get('tasks') if i.get('state')[state] == True]
        from pdfme import build_pdf
        import os
        document = json.loads(json.dumps(self.document))
        section_1 = {}
        document['sections'].append(section_1)
        section_1['content'] = content_1 = []
        content_1.append({
            '.': f"{p.get('name')} Quarterly JobsReport", 'style': 'title', 'label': 'title_1',
            'outline': {'level': 1, 'text': 'A different title 1'}
        })
        content_1.append({
            '.': f"{state.capitalize()} Jobs", 'style': 'sub_title', 'label': 'title_2'})
        
        content_1.append({
            '.': f"Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
        

        table_def1 = {
            'widths': [1.5, 2, 1.25,1.25,1.25],
            'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': 'teal', 's': 9},
            
            'fills': [{'pos': '1::2;:', 'color': 0.8}],
            'borders': [{'pos': 'h0,1,-1;:', 'width': 0.5}],
            'table': [
                ['Id', 'Title', 'Project Phase', 'Start', 'Completion'],
               
            ]
        }
        for item in job_queue:
            data = [ 
                item.get('id'), 
                item.get('title'),
                item.get('projectPhase'),
                datetime.date.fromtimestamp((item.get('event').get('started'))/1000),
                item.get('event').get('completed')
                ]
           
            table_def1['table'].append(data)
        content_1.append(table_def1)
        file_name = os.path.join(DOCUMENT_PATH, f"{p.get('name')}-{state}-JobsReport.pdf")
        with open(file_name, 'wb') as f:
            build_pdf(document, f)
        return {"file": file_name }

    async def printJob(self, id:str=None)-> dict:
        idd = id.split('-')
        
        p = await self.get(id=idd[0])
        return [item for item in p.get('tasks') if item.get("_id") == id ][0]

    async def printSalaryStatement(self, id:str=None)-> dict:
        pass

    async def printSalaryStatements(self, id:str=None, employee:str=None)-> list:
        pass

   
    async def printJobTask(self, data:dict=None)-> dict:
        def as_currency(amount):
            if amount >= 0:
                return '${:,.2f}'.format(amount)
            else:
                return '-${:,.2f}'.format(-amount)

        iid = data.get('_id').split('-')
        project = await self.get(id=iid[0])
        try:
            from pdfme import build_pdf
            import os
           
           
            document = json.loads(json.dumps(self.document))
            section_1 = {}
            document['sections'].append(section_1)
            section_1['content'] = content_1 = []
            table_def = {
                'widths': [1.75, 6.25],
                'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': '#3065ba', 's': 9},               
                
                'table':  [
                    ['', ''],
                
                ]
            }
            header = [ 
                    {
                        'image': os.path.join(IMAGES_PATH, "modlogo.jpg"),
                        'style': {'margin_left': 5, 'margin_right': 430},
                        'min_height': 100
                    }, 
                    {
                    '.':  [ {".b": "CENTRYPLAN C O N S T R U C T I O N SERVICES", 'style': 'title_header'},
                
                    " Marlinway, Old Harbour, Jamaica. W.I ______________________________________________________________________________",
               
                
                ] 
                    }
                   
                    
                    ]
            table_def['table'].append(header)
            content_1.append(table_def)
            content_1.append({
                '.': f"Project: {project.get('name')}", 'style': 'sub_text'})
            content_1.append({
                '.': f"Job Id: {data.get('_id')}", 'style': 'sub_text'})            
            content_1.append({
                '.': f"Job Title: {data.get('title').capitalize()} Cost Report", 'style': 'title', 'label': 'title_1',
                'outline': {'level': 1, 'text': 'Job Report'}
            })
            content_1.append({
                '.': f"Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
            content_1.append({
                '.': f"Description: {data.get('description')}", 'style': 'sub_text', 'label': 'title_2'})
            
           

            table_def1 = {
                'widths': [2.5, 2, 1.25, 1.25, 1.25, 1.25, 1.5],
                'style': {'border_width': 0, 'margin_left': 15, 'margin_right': 15, 'c': 'teal', 's': 9},
                
                'fills': [{'pos': '1::2;:', 'color': 0.8}],
                'borders': [{'pos': 'h0,1,-1;:', 'width': 0.5}],
                'table': [
                    ['Id', 'Title', 'Category', 'Unit', 'Rate', 'Amount', 'Cost'],
                
                ]
            }
            transactions_totals = []

            for item in data.get('tasks'):
                tasks = [ 
                    f"{item.get('_id')}", 
                    item.get('title'),
                    item.get('category'),
                    item.get('metric').get('unit'),
                    as_currency(item.get('metric').get('price')),
                    item.get('metric').get('quantity'),
                    as_currency(float(item.get('metric').get('price')) * float(item.get('metric').get('quantity')))
                    
                    
                    
                    ]
                
                transactions_totals.append(float(item.get('metric').get('price')) * float(item.get('metric').get('quantity')))
                         
                table_def1['table'].append(tasks)
            data['cost']['task'] = sum(transactions_totals)
            data['cost']['contractor'] = float(data.get('fees').get('contractor')) / 100 * data.get('cost').get('task')
            table_def1['table'].append(
                [ 
                    "Job Cost", 
                    "", 
                    "", 
                    "", 
                    "", 
                    "", 
                   as_currency(data['cost']['task'] )           
                    
                    
                    ]
            )
            table_def1['table'].append(
                [ 
                    "Contractor Fees", 
                    "", 
                    f"{data.get('fees').get('contractor')} %", 
                    "", 
                    "", 
                    "", 
                   as_currency(data['cost']['contractor'] )           
                    
                    
                    ]
            )
            table_def1['table'].append(
                [ 
                    "Total Cost", 
                    "", 
                    "", 
                    "", 
                    "", 
                    "", 
                   as_currency(data['cost']['task'] + data['cost']['contractor'])           
                    
                    
                    ]
            )
            content_1.append(table_def1)
            
            
            file_name = os.path.join(DOCUMENT_PATH, f"{data.get('_id')}-costreport.pdf")
            with open(file_name, 'wb') as f:
                build_pdf(document, f)
            data["file"] = file_name 
            return data
        except Exception as e:
            return str(e)
        finally: 
            import webbrowser 
            chrome_path = '/usr/bin/google-chrome %s'
            webbrowser.get(chrome_path).open(file_name)
            del(build_pdf) 
            del(os)
    
    #printAccountTransactions(data=data)
    async def printAccountTransactions(self, data:dict=None)-> dict:
        def as_currency(amount):
            if amount >= 0:
                return '${:,.2f}'.format(amount)
            else:
                return '-${:,.2f}'.format(-amount)

        id = data.get('id')
        project = await self.get(id=id)
        try:
            from pdfme import build_pdf
            import os, arrow
           
            document = json.loads(json.dumps(self.document))
            section_1 = {}
            document['sections'].append(section_1)
            section_1['content'] = content_1 = []
            table_def = {
                'widths': [1.75, 6.25],
                'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': '#3065ba', 's': 9},               
                
                'table':  [
                    ['', ''],
                
                ]
            }
            header = [ 
                    {
                        'image': os.path.join(IMAGES_PATH, "modlogo.jpg"),
                        'style': {'margin_left': 5, 'margin_right': 430},
                        'min_height': 100
                    }, 
                    {
                    '.':  [ {".b": "CENTRYPLAN C O N S T R U C T I O N SERVICES", 'style': 'title_header'},
                
                    " Marlinway, Old Harbour, Jamaica. W.I ______________________________________________________________________________",
               
                
                ] 
                    }
                   
                    
                    ]
            table_def['table'].append(header)
            content_1.append(table_def)
            
            
            if data.get('data').get('filter').get('start') == None:
                content_1.append({
                '.': f"Project Account Receivables: {data.get('id')}", 'style': 'sub_text'}) 
                     
            else:
                content_1.append({
                '.': [{".b": "Project Account Receivables"}, {".": f" for period : {data.get('data').get('filter').get('start')} To {data.get('data').get('filter').get('end')}", 'style': 'sub_text'}]})       

            content_1.append({
                '.': [{".b": "Project"}, {".": f" {project.get('name')}", 'style': 'sub_text'}]
                })              
            #content_1.append({
            #    '.': f"Job Title: {data.get('title').capitalize()} Cost Report", 'style': 'title', 'label': 'title_1',
            #    'outline': {'level': 1, 'text': 'Job Report'}
            #})
            content_1.append({
                '.': f"Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
            #content_1.append({
            #    '.': f"Description: {data.get('description')}", 'style': 'sub_text', 'label': 'title_2'})
            #-+-9*/
           

            table_def1 = {
                'widths': [2.5, 2, 1.25,1.25,1.25, 1.5],
                'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': 'teal', 's': 9},
                
                'fills': [{'pos': '1::2;:', 'color': 0.8}],
                'borders': [{'pos': 'h0,1,-1;:', 'width': 0.5}],
                'table': [
                    ['Id', 'Date', 'Type', 'Ref', 'Amount', 'Payee'],
                
                ]
            }
            transactions_totals = []

            for item in data.get('data').get('data'):
                transation = [ 
                    f"{item.get('id')}", 
                    f"{arrow.get(item.get('date') -(60*60*60*24)).format(arrow.FORMAT_RFC1036)}",
                    item.get('type'),
                    item.get('ref'),
                    as_currency(item.get('amount')),
                    
                    item.get('payee'),
                    
                    ]
                
                transactions_totals.append(float(item.get('amount')))
                         
                table_def1['table'].append(transation)
            
            table_def1['table'].append(
                [ 
                    "Total for Period", 
                    "", 
                    "", 
                    "", 
                    "", 
                   as_currency(sum(transactions_totals) )           
                    
                    
                    ]
            )
            
            
            content_1.append(table_def1)
            
            
            file_name = os.path.join(DOCUMENT_PATH, f"{data.get('id')}-Account-transactions.pdf")
            with open(file_name, 'wb') as f:
                build_pdf(document, f)
            data["file"] = file_name 
            return data
        except Exception as e:
            return str(e)
        finally: 
            import webbrowser 
            chrome_path = '/usr/bin/google-chrome %s'
            webbrowser.get(chrome_path).open(file_name)
            del(build_pdf) 
            del(os)

    

    async def print_project_rates(self, data:dict=None):
        project = await self.get(id=data.get('id'))   
        try:
            from pdfme import build_pdf
            import os, arrow

            file_name = os.path.join(DOCUMENT_PATH, f"{data.get('id')}-{data.get('category')}-JobRates.pdf")
           
            document = json.loads(json.dumps(self.document))
            section_1 = {}
            document['sections'].append(section_1)
            section_1['content'] = content_1 = []
            table_def = {
                'widths': [1.75, 6.75],
                'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': '#3065ba', 's': 9},               
                
                'table':  [
                    ['', ''],
                
                ]
            }
            header = [ 
                    {
                        'image': os.path.join(IMAGES_PATH, "modlogo.jpg"),
                        'style': {'margin_left': 5, 'margin_right': 430},
                        'min_height': 100
                    }, 
                    {
                    '.':  [ {".b": "CENTRYPLAN C O N S T R U C T I O N SERVICES", 'style': 'title_header'},
                
                    " Marlinway, Old Harbour, Jamaica. W.I ______________________________________________________________________________",
               
                
                ] 
                    }
                   
                    
                    ]
            table_def['table'].append(header)
            content_1.append(table_def)
            
            
            
            content_1.append({ '.': f"{project.get('name')}  Job Rates", 'style': 'title'}) 
            content_1.append({ '.': f"Job Category: {data.get('category')}", 'style': 'title'}) 
                     
              

            content_1.append({
                '.': f"Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
            
           

            table_def1 = {
                'widths': [1.5,1.5, 2.75,1.75, 1.75],
                'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': 'teal', 's': 9},
                
                'fills': [{'pos': '1::2;:', 'color': 0.8}],
                'borders': [{'pos': 'h0,1,-1;:', 'width': 0.5}],
                'table': [
                    ['Id', 'Category', 'Title', 'Metric', 'Imperial'],
                
                ]
            }           

            for item in data.get('data'):                
                    
                rate = [ 
                    item.get('_id'), 
                    item.get('category'),
                    item.get('title'),
                    f"{self.as_currency(item.get('metric').get('price'))} / {item.get('metric').get('unit')}",
                    f"{self.as_currency(item.get('imperial').get('price'))} / {item.get('imperial').get('unit')}"
                    ]
                
                
                         
                table_def1['table'].append(rate)           
            
            
            
            content_1.append(table_def1) 
                 

            
            
            with open(file_name, 'wb') as f:
                build_pdf(document, f)
             
            return {"file_name": file_name} 
        except Exception as e:
            return str(e)
        finally: 
            import webbrowser 
            chrome_path = '/usr/bin/google-chrome %s'
            webbrowser.get(chrome_path).open(file_name)
            del(build_pdf) 
            del(os)
            del(arrow)
            del(project)


        
        # Html Project index Generator
    
    # HTML Responces
   
    async def html_page(self, id:str=None):
        p = await self.get(id=id)
        return f"""
        <div class="flex flex-col space-y-1.5">
            <div class="border-b-2 border-gray-200 dark:border-gray-700 ml-5">
            <nav class="-mb-0.5 flex space-x-6">
                <a 
                class="py-4 px-1 inline-flex items-center gap-2 border-b-2 border-transparent text-sm whitespace-nowrap text-gray-500 hover:text-blue-600 focus:outline-none focus:text-blue-600" 
                href="#"
                hx-get="/project_account/{id}"
                hx-target="#project_properties"
                hx-trigger="click"                
                >
                <svg class="flex-shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" ><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>
                Account
                </a>
                <a 
                class="py-4 px-1 inline-flex items-center gap-2 border-b-2 border-blue-500 text-sm font-medium whitespace-nowrap text-blue-600 focus:outline-none focus:text-blue-800" 
                href="#" aria-current="page"
                hx-get="/project_workers/{id}/{'all'}"
                hx-target="#project_properties"
                hx-trigger="click"
                >
                <svg class="flex-shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="10" r="3"/><path d="M7 20.662V19a2 2 0 0 1 2-2h6a2 2 0 0 1 2 2v1.662"/></svg>
                Workers
                </a>
                <a 
                class="py-4 px-1 inline-flex items-center gap-2 border-b-2 border-transparent text-sm whitespace-nowrap text-gray-500 hover:text-blue-600 focus:outline-none focus:text-blue-600"
                href="#"
                hx-get="/project_jobs/{id}"
                hx-target="#project_properties"
                hx-trigger="click"
                >
                <svg class="flex-shrink-0 size-4" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12.22 2h-.44a2 2 0 0 0-2 2v.18a2 2 0 0 1-1 1.73l-.43.25a2 2 0 0 1-2 0l-.15-.08a2 2 0 0 0-2.73.73l-.22.38a2 2 0 0 0 .73 2.73l.15.1a2 2 0 0 1 1 1.72v.51a2 2 0 0 1-1 1.74l-.15.09a2 2 0 0 0-.73 2.73l.22.38a2 2 0 0 0 2.73.73l.15-.08a2 2 0 0 1 2 0l.43.25a2 2 0 0 1 1 1.73V20a2 2 0 0 0 2 2h.44a2 2 0 0 0 2-2v-.18a2 2 0 0 1 1-1.73l.43-.25a2 2 0 0 1 2 0l.15.08a2 2 0 0 0 2.73-.73l.22-.39a2 2 0 0 0-.73-2.73l-.15-.08a2 2 0 0 1-1-1.74v-.5a2 2 0 0 1 1-1.74l.15-.09a2 2 0 0 0 .73-2.73l-.22-.38a2 2 0 0 0-2.73-.73l-.15.08a2 2 0 0 1-2 0l-.43-.25a2 2 0 0 1-1-1.73V4a2 2 0 0 0-2-2z"/><circle cx="12" cy="12" r="3"/></svg>
                Jobs
                </a>
                 <a 
                class="py-4 px-1 inline-flex items-center gap-2 border-b-2 border-transparent text-sm whitespace-nowrap text-gray-500 hover:text-blue-600 focus:outline-none focus:text-blue-600"
                href="#"
                hx-get="/project_days/{id}"
                hx-target="#project_properties"
                hx-trigger="click"
                >Daywork</a>
                 <a 
                class="py-4 px-1 inline-flex items-center gap-2 border-b-2 border-transparent text-sm whitespace-nowrap text-gray-500 hover:text-blue-600 focus:outline-none focus:text-blue-600"
                href="#"
                hx-get="/project_rates/{id}"
                hx-target="#project_properties"
                hx-trigger="click"
                >Rates</a>
            </nav>
            </div>
                            <div id="project_properties">
                            <div class="bg-gray-300 p-5 border rounded">
                            {p.get('name')} {p.get('category')} standard {p.get('standard')}
                            </div>
                            
                             <div class="bg-gray-300 p-5 border rounded">{p.get('owner')}</div>
                             <div class="bg-gray-300 p-5 border rounded">{p.get('address')}</div>
                             </div>
                             
                    </div> 
                """
    
    async def html_account_page(self, id:str=None):
        p = await self.get(id=id)
        return f"""<div class="flex flex-col space-y-1.5">
            <header class="flex flex-wrap sm:justify-start sm:flex-nowrap z-50 w-full bg-white text-sm py-4 dark:bg-gray-800">
                <nav class="max-w-[85rem] w-full mx-auto px-4 sm:flex sm:items-center sm:justify-between" aria-label="Global">
                    <a class="flex-none text-xl font-semibold dark:text-white" href="#">{p.get('name')} Accounting</a>
                    <div class="flex flex-row items-center gap-5 mt-5 sm:justify-end sm:mt-0 sm:ps-5">
                    <a 
                    class="font-medium text-blue-500 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600" 
                    href="#" 
                    aria-current="page"
                    hx-get="/project_account_deposits/{id}"
                    hx-target="#account"
                    hx-trigger="click delay:10ms"
                                        
                    >Deposits</a>
                    <a 
                    class="font-medium text-gray-600 hover:text-gray-400 dark:text-gray-400 dark:hover:text-gray-500 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600" 
                    href="#"
                    hx-get="/project_account_withdrawals/{id}"
                    hx-target="#account"
                    hx-trigger="click"
                    >Withdrawals</a>
                    <a 
                    class="font-medium text-gray-600 hover:text-gray-400 dark:text-gray-400 dark:hover:text-gray-500 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600" 
                    href="#"
                    hx-get="/project_account_paybills/{id}"
                    hx-target="#account"
                    hx-trigger="click"
                    >Paybills</a>
                    <a 
                    class="font-medium text-gray-600 hover:text-gray-400 dark:text-gray-400 dark:hover:text-gray-500 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600" 
                    href="#"
                    hx-get="/project_account_salaries/{id}"
                    hx-target="#account"
                    hx-trigger="click"                    
                    >Salaries</a>
                    <a 
                    class="font-medium text-gray-600 hover:text-gray-400 dark:text-gray-400 dark:hover:text-gray-500 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600" 
                    href="#"
                    hx-get="/project_account_expences/{id}"
                    hx-target="#account"
                    hx-trigger="click"
                    >Expences</a>
                    <a 
                    class="font-medium text-gray-600 hover:text-gray-400 dark:text-gray-400 dark:hover:text-gray-500 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600" 
                    href="#"
                    hx-get="/project_account_purchases/{id}"
                    hx-target="#account"
                    hx-trigger="click"
                    >Purchases</a>
                    </div>

                </nav>
                </header>
                    <div id="account-coms"></div>
                            <div class="acc">
                            <div class="p-5 border rounded">
                                <div id="account">
                               
                                <div class="card">
                                    <div class="card-body"> {p.get('account')}</div>
                                </div>
                                
                                </div>
                            </div>
                            </div>
                    </div> 
                """
    
    async def html_account_deposits_generator(self, id:str=None, filter:str=None):
        from datetime import datetime
        p = await self.get(id=id)
        total_deposits = 0
        try:
            yield f""" <div class="flex flex-col">
                    <div class="m-1.5 overflow-x-auto">
                    <a href="#deposit-modal" uk-toggle>Deposit Funds</a>
                    <p                                     
                      hx-get="/project_deposits_total/{id}"
                       hx-trigger="every 2s"
                    >
                                    
                                </p>
                    <div id="deposit-result"></div>

                        <div class="p-1.5 min-w-full h-screen inline-block align-middle overflow-y-auto">
                        <div class="overflow-hidden">
                            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                            <thead>
                                <tr>
                                <th scope="col" class="px-2 py-2 text-start text-xs font-medium text-gray-500 uppercase">Id.</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Date</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Ref</th>
                                <th scope="col" class="px-4 py-2 text-end text-xs font-medium text-gray-500 uppercase">Payee</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Amount</th>
                                
                                <th></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">

                    """
            for d in p.get('account').get('transactions').get('deposit', []):
                total_deposits += float(d.get('amount'))
                yield f"""<tr class="hover:bg-gray-100 dark:hover:bg-gray-700">              
                <td class="px-2 py-2 whitespace-wrap text-sm font-medium text-gray-800 dark:text-gray-200 w-32">{d.get('id')}</td>
                <td class="px-4 py-2 whitespace-wrap text-sm text-gray-800 dark:text-gray-200">{datetime.date(datetime.fromtimestamp(d.get('date') / 1000, tz=None)).strftime("%A %d. %B %Y")}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{d.get('ref')} </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{d.get('payee')} </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{self.as_currency(float(d.get('amount')))}</td>
                <td class="px-4 py-2 whitespace-nowrap text-end text-sm font-medium">

                <div class="uk-inline">
                    <button class="uk-button uk-button-default" type="button">Manage</button>
                    <div uk-dropdown>
                        <ul class="uk-nav uk-dropdown-nav">
                            <li class="uk-active">
                                <a 
                                    href="#" 
                                    hx-get="/edit_account_deposit/{id}_{d.get('id')}-{d.get('ref')}"
                                    hx-target="#message"
                                    
                                    >Edit</a></li>
                            <li><a href="#">Tag</a></li>
                            <li><a href="#"><button type="button" class="inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent text-blue-600 hover:text-blue-800 disabled:opacity-50 disabled:pointer-events-none dark:text-blue-500 dark:hover:text-blue-400 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">Delete</button>
                                </a>
                            </li>
                        </ul>
                        
                    </div>
                </div>
                    
                     </td>
                </tr>"""
            yield f"""<tr class="hover:bg-gray-100 dark:hover:bg-gray-700"> 
                <td class="px-2 py-2 whitespace-wrap text-sm font-medium text-gray-800 dark:text-gray-200 w-32">Total Deposits to Date</td>
                <td></td>
                <td></td>
                 <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{self.as_currency(total_deposits)}</td>
                
                <td></td>
                </tr>
            
            """
            yield f"""</tbody></table></div></div></div></div>
                <!-- This is the Deposit modal -->
                <div id="deposit-modal" uk-modal>
                    <div class="uk-modal-dialog uk-modal-body">
                        <h2 class="uk-modal-title">Project Account Deposit</h2>
                        <form 
                            hx-post="/account_deposit/{id}"
                            hx-target="#deposit-result"
                            hx-trigger="submit"                        
                            class="uk-grid-small" 
                            uk-grid
                            >
                            <div class="uk-width-1-1">
                                <input class="uk-input" type="date" placeholder="Date" name="date" aria-label="Date">
                            </div>
                            <div class="uk-width-1-2@s">
                                <input class="uk-input" type="text" placeholder="Transaction Type" value="deposit" name="type" aria-label="Deposit">
                            </div>
                            <div class="uk-width-1-4@s">
                                <input class="uk-input" type="text" placeholder="Refference" name="ref" aria-label="Ref">
                            </div>
                            <div class="uk-width-1-4@s">
                                <input class="uk-input" type="number" step="0.01" placeholder="Amount" name="amount" aria-label="$">
                            </div>
                            <div class="uk-width-1-2@s">
                                <input class="uk-input" type="text" placeholder="Payee" name="payee" aria-label="Payee">
                            </div>
                            
                    
                            <p class="uk-text-right">
                                <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                                <button class="uk-button uk-button-primary" type="submit" uk-modal-close>Save</button>
                            </p>
                        </form>
                       
                    </div>
                </div>
            
            """
            
        except Exception as e:
            yield f"""<div class="bg-red-500 text-sm text-red-50 font-bold mx-10 my-5 py-2 px-4">{ str(e)}</div>         
            """            
        finally:
            del(p)
            del(datetime)
            
    
    async def html_account_withdrawal_generator(self, id:str=None, filter:str=None):
        from datetime import datetime
        p = await self.get(id=id)
        total_ = 0
        try:
            yield f""" <div class="flex flex-col">
                    <div class="m-1.5 overflow-x-auto">
                    <a href="#withdraw-modal" uk-toggle>Withdraw Funds</a>
                    <p                                     
                      hx-get="/project_withdrawals_total/{id}"
                       hx-trigger="every 2s"
                    >
                    <div id="result"></div>

                        <div class="p-1.5 min-w-full h-screen inline-block align-middle overflow-y-auto">
                        <div class="overflow-hidden">
                            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                            <thead>
                                <tr>
                                <th scope="col" class="px-2 py-2 text-start text-xs font-medium text-gray-500 uppercase">Id.</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Date</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Ref</th>
                                <th scope="col" class="px-4 py-2 text-end text-xs font-medium text-gray-500 uppercase">Recipient</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Amount</th>
                                
                                <th></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">

                    """
            for d in p.get('account').get('transactions').get('withdraw', []):
                total_ += float(d.get('amount'))
                yield f"""<tr class="hover:bg-gray-100 dark:hover:bg-gray-700">              
                <td class="px-2 py-2 whitespace-wrap text-sm font-medium text-gray-800 dark:text-gray-200 w-32">{d.get('id')}</td>"""
                if type(d.get('date')) == int:
                    yield f"""<td class="px-4 py-2 whitespace-wrap text-sm text-gray-800 dark:text-gray-200">{datetime.date(datetime.fromtimestamp(d.get('date') / 1000, tz=None)).strftime("%A %d. %B %Y")}</td>"""
                else:
                    yield f"""<td class="px-4 py-2 whitespace-wrap text-sm text-gray-800 dark:text-gray-200">{d.get('date')}</td>"""
                yield f"""<td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{d.get('ref')} </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{d.get('recipient')} </td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{self.as_currency(float(d.get('amount')))}</td>
                <td class="px-4 py-2 whitespace-nowrap text-end text-sm font-medium">
                    <button type="button" class="inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent text-blue-600 hover:text-blue-800 disabled:opacity-50 disabled:pointer-events-none dark:text-blue-500 dark:hover:text-blue-400 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">Delete</button>
                </td>
                </tr>"""
            yield f"""<tr class="hover:bg-gray-100 dark:hover:bg-gray-700"> 
                <td class="px-2 py-2 whitespace-wrap text-sm font-medium text-gray-800 dark:text-gray-200 w-32">Total Withdrawals to Date</td>
                <td></td>
                <td></td>
                <td></td>
                 <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{self.as_currency(total_)}</td>
                
                <td></td>
                </tr>
            
            """
            yield f"""</tbody></table></div></div></div></div>
                <!-- This is the Withdrawal modal -->
                <div id="withdraw-modal" uk-modal>
                    <div class="uk-modal-dialog uk-modal-body">
                        <h2 class="uk-modal-title">Project Account Withdrawal</h2>
                        <form 
                            hx-post="/account_withdrawal/{id}"
                            hx-target="#result"
                            hx-trigger="submit"                        
                            class="uk-grid-small" 
                            uk-grid
                            >
                            <div class="uk-width-1-1">
                                <input class="uk-input" type="date" placeholder="Date" name="date" aria-label="Date">
                            </div>
                            <div class="uk-width-1-2@s">
                                <input class="uk-input" type="text" placeholder="Transaction Type" value="withdraw" name="type" aria-label="Deposit">
                            </div>
                            <div class="uk-width-1-4@s">
                                <input class="uk-input" type="text" placeholder="Refference" name="ref" aria-label="Ref">
                            </div>
                            <div class="uk-width-1-4@s">
                                <input class="uk-input" type="number" step="0.01" placeholder="Amount" name="amount" aria-label="$">
                            </div>
                            <div class="uk-width-1-2@s">
                                <input class="uk-input" type="text" placeholder="Recipient" name="recipient" aria-label="Payee">
                            </div>
                            
                    
                            <p class="uk-text-right">
                                <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                                <button class="uk-button uk-button-primary" type="submit" uk-modal-close>Save</button>
                            </p>
                        </form>
                       
                    </div>
                </div>
            
            """
            
        except Exception as e:
            yield f"""<div class="bg-red-500 text-sm text-red-50 font-bold mx-10 my-5 py-2 px-4">{ str(e)}</div>         
            """            
        finally:
            del(p)
            del(datetime)
            


    async def html_account_paybills_generator(self, id:str=None, filter:str=None):
        from datetime import datetime
        p = await self.get(id=id)
        total_ = 0
        return p.get('account').get('records').get('paybills', [])
    
    async def html_account_salaries_generator(self, id:str=None, filter:str=None):
        from datetime import datetime
        p = await self.get(id=id)
        total_ = 0
        return p.get('account').get('records').get('salary_statements', [])
    
    
    async def html_account_expences_generator(self, id:str=None, filter:str=None):
        from datetime import datetime
        p = await self.get(id=id)
        total_ = 0
        return p.get('account').get('expences', [])
    

    async def html_account_purchases_generator(self, id:str=None, filter:str=None):
        from datetime import datetime
        p = await self.get(id=id)
        total_ = 0
        return p.get('account').get('records', {}).get('invoices', [])
    
    async def html_account_purchase_orders_generator(self, id:str=None, filter:str=None):
        from datetime import datetime
        p = await self.get(id=id)
        total_ = 0
        return p.get('account').get('records', {}).get('purchase_orders', [])


               
    async def html_job_page_generator(self, id:str=None): 
        idd = id.split('-')
        p = await self.get(id=idd[0])
        jb = [j for j in p.get('tasks') if j.get('_id') == id ] 
        if len(jb) > 0:
            job = jb[0] 
        else:
            job={}
       
        yield f"""
            <div class="flex flex-col space-y-1.5">
                <div class="navbar">
                    <div class="navbar-start">
                        <a class="navbar-item text-sm"><span>{p.get('name')} / {job.get('title')} </span></a>
                    </div>
                    <div class="navbar-center">
                        <ul class="uk-subnav uk-subnav-pill" uk-switcher="connect: #job-properties">
                            <li><a href="#" class="navbar-item">Home</a></li>
                            <li><a href="#" class="navbar-item">Tasks</a></li>
                            <li><a href="#" class="navbar-item">Crew</a></li>
                            
                        
                        </ul>
                        
                    </div>
                    <div class="navbar-end">
                    <a href="#add-job-task-modal" uk-toggle class="navbar-item">Add Task</a>
                    <a href="#add-crew-member-modal" uk-toggle class="navbar-item">Add Crew</a>
                        
                        
                        <div id="state" class="dropdown">
                        <label class="btn btn-solid-primary my-2" tabindex="0">Set State</label>
                        <div class="dropdown-menu">
                            <a 
                            class="dropdown-item text-sm"
                            hx-get="/update_project_job_state/{job.get('_id')}/{'active'}"
                            hx-target="#state"
                            >Active</a>
                            <a 
                            tabindex="-1" 
                            class="dropdown-item text-sm"
                            hx-get="/update_project_job_state/{job.get('_id')}/{'completed'}"
                            hx-target="#state"
                            >Completed</a>
                            <a 
                            tabindex="-1" 
                            class="dropdown-item text-sm"
                            hx-get="/update_project_job_state/{job.get('_id')}/{'paused'}"
                            hx-target="#state"                            
                            >Paused</a>
                            <a 
                            tabindex="-1" 
                            class="dropdown-item text-sm"
                            hx-get="/update_project_job_state/{job.get('_id')}/{'terminated'}"
                            hx-target="#state"                           
                            >Terminated</a>
                        </div>
                    </div> 
                    </div>
                </div>
               
                <div id="result"></div>
                <ul id="job-properties" class="uk-switcher uk-margin">
                    <li>                    
                        <div class="flex flex-row bg-gray-300 p-5 border rounded">
                        
                        <div class="card">
                            <div class="card-body">
                                <h2 class="card-header"><span class="uk-badge">{job.get('_id')}</span> {job.get('title')}
                                </h2>
                                <p class="text-content2">
                                {job.get('description')}
                                projectPhase  {job.get('projectPhase')}
                                Crew {job.get('crew').get('name')} | Members {len(job.get('crew').get('members'))}
                                </p>
                                <div class="card-footer">
                                    <button class="btn-secondary btn">Learn More</button>
                                </div>
                            </div>
                        </div>

                        <div class="card">
                            <div class="card-body">
                                <h2 class="card-header">{job.get('title')}</h2>
                                <p class="text-content2">{job}</p>
                                <div class="card-footer">
                                    <button class="btn-secondary btn">Learn More</button>
                                </div>
                            </div>
                        </div>
                        
                        
                        </div>                    
                    </li>
                    <li>
                        <div class="bg-gray-300 p-5 border rounded">{job.get("tasks")}</div>                     
                    </li>
                    <li><div class="bg-gray-300 p-5 border rounded">{job.get("crew")}</div></li>
                    
                </ul>

               

                <!-- This is the add task to job modal -->
                <div id="add-job-task-modal" uk-modal>
                    <div class="uk-modal-dialog uk-modal-body">
                        <h2 class="uk-modal-title">Add Job Task</h2>
                        

                        <div class="uk-child-width-1-3@s" uk-grid>
                            <div>
                                <h4>Project Rates Index</h4>
                                <div uk-sortable="group: sortable-group">
                                """
        for task_rate in p.get("rates"):
            yield f"""<div class="uk-margin">
                            <div class="uk-card uk-card-default uk-card-body uk-card-small" >{task_rate.get("_id")} {task_rate.get("title")}</div>
                        </div>"""
        yield f""" </div>
                            </div>
                            
                            <div>
                                <h4>Job Tasks List</h4>
                                <div 
                                    uk-sortable="group: sortable-group"
                                    hx-post="/add_job_task" 
                                   hx-vals='{ {"myVal": task_rate} }' 
                                    hx-target="#result" 
                                    hx-trigger="added"
                                    
                                    ></div>
                            </div>
                        </div>


                        <p class="uk-text-right">
                            <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                            <button class="uk-button uk-button-primary" type="button">Save</button>
                        </p>
                    </div>
                </div>

               

                <!-- This is the add crew member modal -->
                <div id="add-crew-member-modal" uk-modal>
                    <div class="uk-modal-dialog uk-modal-body">
                        <h2 class="uk-modal-title">Add Crew Member</h2>
                        <p>{p.get("workers")}</p>
                        <p class="uk-text-right">
                            <button class="uk-button uk-button-default uk-modal-close" type="button">Cancel</button>
                            <button class="uk-button uk-button-primary" type="button">Save</button>
                        </p>
                    </div>
                </div>
                           
                            
                    </div>  """   
        
        
    async def html_workers_page(self, id:str=None, filter:str=None):
        p = await self.get(id=id)
        workers = p.get('workers')
        categories = { worker.get('value').get('occupation') for worker in workers }
        if filter:
            if filter == 'all' or filter == 'None':            
                filtered = workers 
            else:
                filtered = [worker for worker in workers if worker.get("value").get("occupation") == filter]

            yield f"""
            <div class="flex flex-row bg-gray-300 py-3 px-4 items-inline text-center rounded">
                <span class="cursor-pointer" uk-toggle="target: #new-employee-modal"uk-icon="plus"></span>
                    <p class="mx-5">{p.get('name')} Workers Index</>                
                    <span class="bg-gray-50 py-1 px-2 border rounded-full mx-10">{len(filtered)}<span>   
                      <a href><span uk-drop-parent-icon></span></a>
                    <div uk-dropdown="pos: bottom-center">
                    <ul class="uk-nav uk-dropdown-nav">
                     <li class="uk-nav-header">Filter Workers</li>
                     <li><a 
                                href="#"
                                hx-get="/project_workers/{id}/{'all'}"
                                hx-target="#project_properties"
                                hx-trigger="click"                                 
                                >All Workers</a>
                        </li>
                        """

            for item in categories:
                yield f""" <li>
                                <a 
                                href="#"                               
                                hx-get="/project_workers/{id}/{item}"
                                hx-target="#project_properties"
                                hx-trigger="click"                                 
                                >{item}</a></li>"""
                       
                        
            yield f""" </ul></div>
                    </div>
                <table class="uk-table uk-table-small uk-table-hover uk-table-divider text-teal-800">
                <thead>
                    <tr class="uk-text-primary">
                        <th></th>
                        <th>Id</th>
                        <th>Name</th>
                        <th>OC</th>
                        <th>Occupation</th>
                        <th>Rating</th>
                         <th>Contact</th>
                    </tr>
                </thead>
                <tbody> """
            for e in filtered:

                yield f"""<tr
                            hx-get="/team/{e.get('id').split('-')[1]}"
                            hx-target="#project_properties"
                            hx-trigger="click"
                            >
                        <td><img class="h-12 w-12 rounded-full" src="{e.get('value').get('imgurl')}" alt="P"></td>
                        <td>{e.get('id')}</td>
                        <td>{e.get("value").get('name')}</td>
                        <td>{e.get("value").get('oc')}</td>
                        <td>{e.get("value").get('occupation')}</td>    
                        <td>{e.get("value").get('rating')}</td>  
                        <td>
                        <div class="flex flex-col text-xs">
                       <span>Email. {e.get("value").get('email')}</span>
                        <span>Mobile {e.get("value").get('mobile')}<span>
                        
                         </div>

                        </td>                   
                        
                    </tr>             
                    """
            yield """</tbody></table>"""
        else:
            yield f"""
            <div class="flex flex-row bg-gray-300 py-3 px-4 items-inline text-center rounded">
                <span class="cursor-pointer" uk-toggle="target: #new-employee-modal"uk-icon="plus"></span>
                    <p class="mx-5">{p.get('name')} Workers Index</>                
                    <span class="bg-gray-50 py-1 px-2 border rounded-full">{len(workers)}<span>   
                      <a href><span uk-drop-parent-icon></span></a>
                    <div uk-dropdown="pos: bottom-center">
                    <ul class="uk-nav uk-dropdown-nav">
                     <li class="uk-nav-header">Filter Workers</li>
                     <li><a 
                                href="#"
                                hx-get="/project_workers/{id}/{'all'}"
                                hx-target="#project_properties"
                                hx-trigger="click"                                 
                                >All Workers</a>
                        </li>
                        """

            for item in categories:
                yield f""" <li>
                                <a 
                                href="#"
                                hx-get="/project_workers/{id}/{item}"
                                hx-target="#project_properties"
                                hx-trigger="click"                                 
                                >{item}</a></li>"""
                       
                        
            yield f""" </ul></div>
                    </div>
                <table class="uk-table uk-table-small uk-table-hover uk-table-divider text-teal-800">
                <thead>
                    <tr class="uk-text-primary">
                        <th>Id</th>
                        <th>Name</th>
                        <th>Occupation</th>
                    </tr>
                </thead>
                <tbody> """
            for e in workers:
                yield f"""<tr
                            hx-get="/team/{e.get('_id').split('-')[1]}"
                            hx-target="#project_properties"
                            hx-trigger="click"
                            >
                        <td>{e.get('_id')}</td>
                        <td>{e.get('name')}</td>
                        <td>{e.get('occupation')}</td>                   
                        
                    </tr>             
                    """
            yield """</tbody></table>"""
    
    
    async def html_admin_page(self, id:str=None):
        
        p = await self.get(id=id)
        
        return p.get('admin', {})
    
    async def html_rates_page_generator(self, id:str=None):
        try:
            from modules.rate import Rate
        
            industry_rates = await Rate().all_rates()
            p = await self.get(id=id)
            yield f"""
                <div class="navbar">
                    <div class="navbar-start">
                        <a class="navbar-item">{p.get('name')} Rates Index</a>
                    </div>
                    <div class="navbar-end">
                        <a class="navbar-item">Filter</a>
                         <a class="navbar-item">About</a>
                        <label class="btn btn-primary" for="modal-2">Add Industry Rate</label>
                      
                    </div>
                </div>
            """
            yield f""" <div class="flex flex-col">
                    <div class="m-1.5 overflow-x-auto">
                        <div class="p-1.5 min-w-full h-screen inline-block align-middle overflow-y-auto">
                        <div class="overflow-hidden">
                            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                            <thead>
                                <tr>
                                 <th scope="col" class="px-2 py-2 text-start text-xs font-medium text-gray-500 uppercase">Id</th>
                                <th scope="col" class="px-2 py-2 text-start text-xs font-medium text-gray-500 uppercase">Title</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Description</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Category</th>
                                <th scope="col" class="px-4 py-2 text-start text-xs font-medium text-gray-500 uppercase">Metric</th>
                                <th scope="col" class="px-4 py-2 text-end text-xs font-medium text-gray-500 uppercase">Imperial</th>
                                <th></th>
                                </tr>
                            </thead>
                            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                    """
            for rate in p.get('rates', []):
                yield f"""<tr class="hover:bg-gray-100 dark:hover:bg-gray-700">      
                <td class="px-2 py-2 whitespace-wrap text-xs font-medium text-gray-800 dark:text-gray-200 w-32">{rate.get('_id')}</td>
                       
                <td class="px-2 py-2 whitespace-wrap text-sm font-medium text-gray-800 dark:text-gray-200 w-32">{rate.get('title')}</td>
                <td class="px-4 py-2 whitespace-wrap text-sm text-gray-800 dark:text-gray-200">{rate.get('description')}</td>
                <td class="px-4 py-2 whitespace-wrap text-sm text-gray-800 dark:text-gray-200">{rate.get('category')}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{self.as_currency(float(rate.get('metric').get('price')))} /{rate.get('metric').get('unit')}</td>
                <td class="px-4 py-2 whitespace-nowrap text-sm text-gray-800 dark:text-gray-200">{self.as_currency(float(rate.get('imperial').get('price')))} /{rate.get('imperial').get('unit')}</td>
                <td class="px-4 py-2 whitespace-nowrap text-end text-sm font-medium">
                    <button type="button" class="inline-flex items-center gap-x-2 text-sm font-semibold rounded-lg border border-transparent text-blue-600 hover:text-blue-800 disabled:opacity-50 disabled:pointer-events-none dark:text-blue-500 dark:hover:text-blue-400 dark:focus:outline-none dark:focus:ring-1 dark:focus:ring-gray-600">Delete</button>
                </td>
                </tr>"""

            yield f"""</tbody></table></div></div></div></div>

                

                <input class="modal-state" id="modal-2" type="checkbox" />
                <div class="modal w-screen">
                    <label class="modal-overlay" for="modal-2"></label>
                    <div class="modal-content flex flex-col gap-5 max-w-3xl">
                        <label for="modal-2" class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</label>
                        <h2 class="text-xl">Industry Rates Index</h2>
                        <section>
                        <div>Filter</div>
                        <div class="bg-gray-300 text-gray-900 p-1 rounded-md">
                            <p class="text-xs">Add Industry Rate to Project</p>
                            <form prevent-default>
                             <table class="uk-table uk-table-divider">
                            <thead>
                        <tr>
                            <th></th>
                            <th>Id</th>
                            <th>Title</th>
                            <th>Description</th>
                            <th>Category</th>
                        </tr>
                        </thead>
                        <tbody>"""
                            
                       
            for rate in industry_rates:         
                yield f""" <tr>
                            <td>
                             
                            <input 
                                type="radio" 
                                class="radio radio-bordered-primary"
                                value="{rate.get('_id')}" 
                                name="rate" 
                                hx-post="/add_industry_rate/{p.get('_id')}" 
                                hx-target="#message" 
                              
                                >
                            </td>
                            <td>{ rate.get("_id") }</td>
                            <td> { rate.get("title") }</td>
                            <td> { rate.get("description") }</td>
                            <td> { rate.get("category") }</td>

                        </tr>"""
            yield f"""                  
                        </tbody>
                    </table>
                                
            </form></div>
                        </section>
                        <!--div class="flex gap-3">
                            <button class="btn btn-error btn-block">Delete</button>
                            <button class="btn btn-block">Cancel</button>
                        </div-->
                    </div>
                </div>
            
            """
        except Exception as e:
            yield f"<div> {str(e)}</div>"

    async def html_inventory_generator(self, id:str=None):
        
        p = await self.get(id=id)        
        return p.get('inventory', [])
    
    
    async def html_state(self, id:str=None):
        
        p = await self.get(id=id)
        
        return p.get('state', {})
    

    async def html_events(self, id:str=None):
        
        p = await self.get(id=id)
        
        return p.get('event', {})
    

    async def html_progress_report(self, id:str=None):
        
        p = await self.get(id=id)
        
        return p.get('progress', {})
    

    async def html_activity_log_generator(self, id:str=None):
        
        p = await self.get(id=id)        
        return p.get('activity_log', [])
    
    async def html_reports_generator(self, id:str=None):
        
        p = await self.get(id=id)        
        return p.get('reports', [])
    

    async def html_estimates_generator(self, id:str=None):
        
        p = await self.get(id=id)        
        return p.get('estimates', [])
 
    
        





""" TEST
data = {
    "name":"The Donotia Experience",   
    "address":{},

}      

p = Project(data=data)


print()
print(p.data)

import asyncio
#asyncio.run(p.delete(p.data))

asyncio.run(p.all_workers())

print(p.workers)
"""