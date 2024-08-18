
#from aiohttp import web
from starlette.responses import JSONResponse, PlainTextResponse
from starlette_login.decorator import login_required
from decoRouter import Router


from modules.project import logger, Project
from modules.rate import Rate
from modules.zen import zen_now
from modules.utils import GenerateId

main = Router()


@main.get('/genid/{flag}')
async def generateId(request):
  flag = request.path_params.get('flag').split(' ')
  g = GenerateId()
  return PlainTextResponse(await g.nameid(fn=flag[0], ln=flag[1] ))


    
#------------ RATE SHEET ROUTES ------------------

# Create
@main.post('/rate')
@login_required
async def saveRate( request ):
    try:
        payload = await request.json()              
        return JSONResponse(await Rate(data=payload).save())
    except Exception: return JSONResponse({"error": str(Exception)})
    finally: del payload 

# Update
@main.put('/rate')
@login_required
async def updateRate( request ):
    try:
        payload = await request.json()             
        return JSONResponse( await Rate().update(data=payload) )
    except Exception: return JSONResponse({"error": str(Exception)})
    finally: del(payload) 

# Get One
@main.get('/rate/{id}')
async def getRate( request ):
    """description: These end-points retreives a single Industry Job Rates \
    produced by The Master Builders Association of Jamaica by default requires \
    directive id. \
    ---
    summary: Info for a  specific rate
    tags:
      - rate
    parameters:
      - name: id
        in: path
        required: true
        description: The id of the rate item to retrieve
        schema:
          type: string
          format: utf-8
    responses:
      '200':
        description: Expected response to a valid request
    """
    try: return JSONResponse( await Rate().get(id=request.path_params.get('id')) )
    except Exception as e: return JSONResponse({"error": str(e)})
    

# Get Index
@main.get('/rate')
async def get_rate_index( request ):
    """description: These end-points retreives an index of Industry Job Rates \
    produced by The Master Builders Association of Jamaica by default and \
    followed by a directive produces a list of rates, an individual rate, \
    or can be mapped to produce a list of specific nodes of data. \
    ---
                     summary: Info for a list of rates or a specific rate
    tags:
      - rate
    parameters:
      - name: id
        in: path
        required: true
        description: The id of the rate item to retrieve
        schema:
          type: string
          format: utf-8
    responses:
      '200':
        description: Expected response to a valid request
    """
    try: return JSONResponse( await Rate().all())
    except Exception as e: return JSONResponse({"error": str(e)})

# Get Rates
@main.get('/rates')
async def getRates( request ):
    """description: These end-points retreives an index of Industry Job Rates \
    produced by The Master Builders Association of Jamaica by default and \
    followed by a directive produces a list of rates, an individual rate, \
    or can be mapped to produce a list of specific nodes of data. \
    ---
    summary: Info for a list of rates or a specific rate
    tags:
      - rate
    parameters:
      - name: id
        in: path
        required: true
        description: The id of the rate item to retrieve
        schema:
          type: string
          format: utf-8
    responses:
      '200':
        description: Expected response to a valid request
    """
    try: return JSONResponse( await Rate().all_rates())
    except Exception as e: return JSONResponse({"error": str(e)})


# Delete
@main.delete('/rate/{id}')
@login_required
async def deleteRate( request ):
    """description: These end-points retreives a single Industry Job Rates \
    produced by The Master Builders Association of Jamaica by default requires \
    directive id. \
    ---
    summary: Info for a  specific rate
    tags:
      - rate
    parameters:
      - name: id
        in: path
        required: true
        description: The id of the rate item to retrieve
        schema:
          type: string
          format: utf-8
    responses:
      '200':
        description: Expected response to a valid request
    """
    try: return JSONResponse( await Rate().delete(id=request.path_params.get('id')) )
    except Exception as e: return JSONResponse({"error": str(e)})

# Backup
@main.post('/backup')
async def backup(request): return JSONResponse({"status": "Pending", "request": await request.json()})

# _______________ Project  API ________________________
  
# CREATE
@main.post('/project')
@login_required
async def new_project( request ):
  '''Create new projects '''
  data = await request.json()
  
  p = Project(data=data)    
  p.meta_data["created_by"] = request.user.username
  return JSONResponse(await p.save())

# READ
@main.get('/projects')
async def projects( request ):
  '''Create new projects '''
  p = Project() 
  return JSONResponse(await p.all())

@main.get('/raw_projects')
async def raw_projects( request ):
  '''Create new projects '''
  p = Project() 
  return JSONResponse(await p.all_raw())


@main.get('/project/{id}')
async def project( request ):
  '''Create new projects '''
  id = request.path_params.get('id')
  p = Project() 
  project = await p.get(id=id)
  '''#print(project['tasks'])
  for item in project['tasks']:
    item['event']['completion'] = 0
    item['event']['duration'] = 0
    
  try:
     await p.update(data=project) 
  except Exception as e:
     print(str(e)) '''
  return JSONResponse(project)

# UPDATE
@main.put('/project')
@login_required
async def update_project( request ):
  '''Updates existing project '''
  data = await request.json()
  p = Project() 
  await p.update(data=data)
  return JSONResponse(await p.get(id=data.get('_id')))

# DELETE
@main.delete('/project/{id}')
@login_required
async def deleteProject( request ):
  id = request.path_params.get('id')
  p = Project() 
  return JSONResponse(await p.delete(id=id))

## PROJECT ACCOUNTING
#Account Transaction
@main.post('/transaction/{id}')
@login_required
async def account_transaction( request ):
  '''Handles Project account transactions.'''
  id = request.path_params.get('id')
  data = await request.json()
  p = Project() 
  result = await p.handleTransaction(id=id, data=data)
  return JSONResponse(result)


# Project PayBill
@main.post('/paybill/{id}')
@login_required
async def projectPaybill(request):
  id = request.path_params.get('id')
  data = await request.json()
  
  p = Project()
  try: return JSONResponse(await p.addWorkerSalary(id=id, data=data))
  except Exception as e: return JSONResponse(str(e))
  finally: 
    del(id)
    del(p)


# Project Purchases
@main.get('/purchases/{id}')
@login_required
async def projectPurchases(request):
  id = request.path_params.get('id')
  p = Project()
  try: return JSONResponse(await p.getInvoices(id=id))
  except Exception as e: return JSONResponse(str(e))
  finally: 
    del(id)
    del(p)

# Project Expence
@main.post('/expence/{id}')
@login_required
async def addProjectExpence(request):
  id = request.path_params.get('id')
  data = await request.json()
  p = Project()
  try: return JSONResponse(await p.addExpence(id=id, data=data))
  except Exception as e: return JSONResponse(str(e))
  finally: 
    del(id)
    del(p)

@main.get('/expences/{id}')
async def getProjectExpence(request):
  id = request.path_params.get('id')  
  p = Project()
  try: return JSONResponse(await p.getExpences(id=id))
  except Exception as e: return JSONResponse(str(e))
  finally: 
    del(id)
    del(p)



# PROJECT WORKERS
@main.post('/addworkers/{id}')
@login_required
async def addProjectWorkers( request ):
  ''' Adds a list of workers to the projects workers index'''
  id = request.path_params.get('id')
  data = await request.json()
  p = Project() 
  result = await p.addWorkers(id=id, data=data)
  return JSONResponse(result)

## PROJECT JOBS
@main.post('/addjobtask/{id}')
@login_required
async def addTaskToJob(request):
  ''' Adds a task to an existing project job'''
  id = request.path_params.get('id')  
  data = await request.json()
  p = Project() 
  result = await p.addTaskToJob(id=id, data=data)
  return JSONResponse(result)


@main.post('/addJob/{id}')
@login_required
async def addJobToQueue(request ):
  '''Creates a new job on the project tasks '''
  id = request.path_params.get('id')
  data = await request.json()
  p = Project()  
  return JSONResponse(await p.addJobToQueue(id=id, data=data))

@main.post('/jobreport/{id}')
@login_required
async def addJobReport(request ):
  '''Creates a new job report on the project reports '''
  id = request.path_params.get('id')
  data = await request.json()
  p = Project()  
  return JSONResponse(await p.addJobReport(id=id, data=data))

@main.get('/jobreport/{id}')
async def getJobReports(request ):
  '''Returs a list of job reports as per request id'''
  id = request.path_params.get('id')
  p = Project()  
  return JSONResponse(await p.getJobReports(id=id))

@main.post('/addinvoice/{id}')
@login_required
async def addProjectInvoice(request):
    id = request.path_params.get('id')
    invoice_data = await request.json()
    p = Project()
    try:
        result = await p.addInvoice(id=id, data=invoice_data)
    except Exception as e:
            result = {'error': str(e)}
    finally:
        del(p)
        return JSONResponse( result )

@main.get('/processJobCost/{id}')
@login_required
async def processJobCost(request ):
  '''Returs processed job costs'''
  id = request.path_params.get('id')
  p = Project()  
  return JSONResponse(await p.processJobCost(id=id))


@main.post('/dayworkRecord/{id}')
@login_required
async def addDayworkReport(request ):
  '''Creates a new daywor report on the project reports '''
  id = request.path_params.get('id')
  data = await request.json()
  p = await Project().submitDayWork(id=id, data=data)  
  return JSONResponse(p)


## PROJECT JOB CREW MANAGEMENT
@main.get('/projectcrews/{id}')
async def getProjectCrews(request):  
  id = request.path_params.get('id')  
  p = Project() 
  return JSONResponse(await p.getProjectCrews(id=id))

# Add crew member
@main.post('/addCrewMember/{id}')
@login_required
async def addCrewMembers(request):
  id = request.path_params.get('id')
  data = await request.json()
  p = Project() 
  try:
    return JSONResponse(await p.addCrewMember(id=id, data=data))
  except Exception as e:
    logger.error(str(e))


# Add crew members from a list
@main.post('/addCrewMembers/{id}')
@login_required
async def addCrewMembers(request):
  id = request.path_params.get('id')
  data = await request.json()
  p = Project() 
  try:
    return JSONResponse(await p.addCrewMembers(id=id, data=data))
  except Exception as e:
    logger.error(str(e))

# Assign Task to worker
@main.post('/assigntask/{id}')
@login_required
async def assignTaskToCrewMember(request):
  id = request.path_params.get('id')
  data = await request.json()
  p = Project()
  result = await p.assignTaskToCrewMember(id=id, wid=data.get('wid'))

  return JSONResponse(result)

@main.post('/taskprogress/{id}')
@login_required
async def administerTaskProgress(request):
  id = request.path_params.get('id')
  data = await request.json()
  p = Project()
  result = await p.administerTaskProgress(id=id, data=int(data.get('progress')))
  return JSONResponse(result)


@main.post('/updateJobTasks/{id}')
@login_required
async def updateJobTasks(request):
  id = request.path_params.get('id')
  data = await request.json()
  p = Project()
  result = await p.updateJobTasks(id=id, tasks=data)
  return JSONResponse(result)


@main.post('/updateJobTask/{id}')
@login_required
async def updateJobTask(request):
  id = request.path_params.get('id')
  data = await request.json()
  p = Project()
  result = await p.updateJobTask(id=id, data=data)
  return JSONResponse(result)


@main.get('/project_worker_tasks/{id}')
async def getProjectWorkerData(request):
  id = request.path_params.get('id')
  p = Project()
  result = await p.getProjectWorkerData(id=id)
  return JSONResponse(result)

@main.get('/print_project_jobs/{id}')
async def printProjectJobs(request):
  id = request.path_params.get('id')
  result = await Project().printJobQueue(id=id)
  return JSONResponse(result)

@main.get('/print_job/{id}')
async def printJob(request):
  id = request.path_params.get('id')
  result = await Project().printJob(id=id)
  return JSONResponse(result)

@main.post('/printjob')
async def printJobTask(request):
  data = await request.json()
  result = await Project().printJobTask(data=data)
  return JSONResponse(result)



@main.post('/print_account_transactions')
async def print_account_transactions(request):
  data = await request.json()
  result = await Project().printAccountTransactions(data=data)
  return JSONResponse(result)


@main.post('/print_project_rates')
async def print_project_rates(request):
  data = await request.json()
  return JSONResponse(await Project().print_project_rates(data=data) )


async def getRemoteProject(id:str=None):
  ''' Retrieves data from a remote server 
    returns null on network error
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

@main.get('/sync_remote/{id}')
@login_required
async def sync_remote(request):
  ''' Sync local and remote data 
    return local data if remote is absent 
  '''
  import json
  import datetime
  import subprocess
  def Copy_Logs():
    Sourcedir = datetime.datetime.now().strftime("/data1/logs/%B/%b_%d_%y/")
    Destdir = "/data2/logs/"
    subprocess.call(['rsync', '-avz', '--min-size=1', '--include=*.txt', '--exclude=*', Sourcedir, Destdir ])
    
  id = request.path_params.get('id')  
  data = await Project().sync_remote_data(id=id)
  return JSONResponse(data)

@main.get('/netscan')
@login_required
async def network_scanner(request):
  query_port = '6757'
  target = '192.168.0.0/24' #input("Enter target: ")import nmap3
  return JSONResponse({
    'query_port': query_port,
    'hosts': target
    }

  )

@main.get('/inventory/{id}')
async def process_project_inventory(request):

  return JSONResponse(await Project().process_project_inventory(id=request.path_params.get('id')))


@main.post('/create_new_paybill/{id}')
@login_required
async def create_new_paybill(request):
  id = request.path_params.get('id') 
  data = await request.json()
  return JSONResponse(await Project().create_new_paybill(id=id, data=data))



@main.post('/add_bill_item/{id}')
@login_required
async def add_bill_item(request):
  id = request.path_params.get('id') 
  data = await request.json()
  result = await Project().add_bill_item(id=id, data=data) 
  if result is None:
    return JSONResponse({"error": "Item Already Exist in Bill."}, status_code=406)
  else:
    return JSONResponse(result)
