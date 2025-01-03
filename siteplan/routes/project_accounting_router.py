## Project Accounting Router
## Handles project accounting related requests 

import json
from asyncio import sleep
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, StreamingResponse
from starlette_login.decorator import login_required
from starlette.background import BackgroundTask
from decoRouter import Router
from modules.project import ( get_project, handle_transaction, update_project, 
    process_paybill_dayworker, add_expence, default_fees, salary_statement_item_model, salary_statement_model,
    withdrawal_model, project_account_withdrawal_generator, get_project_inventory)
from modules.employee import  get_worker, update_employee, process_days_work
from modules.supplier import supplier_name_index, get_supplier, update as update_supplier
from modules.utils import timestamp, to_dollars, filter_dates, today, exception_message
from modules.accumulator import ProjectDataAccumulator   
from modules.inventory import Inventory, InventoryItem, material_index, stock_material, Supplier
from config import TEMPLATES
from modules.invoice_processor import InvoiceItem, save_invoice_item, get_invoice_items, reset_invoice_repo
router = Router()

## Project Acconting
@router.get('/project_account/{id}')
@login_required
async def get_project_account(request):
    id = request.path_params.get('id')
    p = await get_project(id=id)
    return TEMPLATES.TemplateResponse('/project/account/accountPage.html', {
        "request": request,
        "id": id,
        "name": p.get('name'),
        "account": p.get('account')
        })



# PROCESS DEPOSITS
@router.get('/project_account_deposits/{id}')
@login_required
async def get_project_account_deposits(request):
    id = request.path_params.get('id')
    p = await get_project(id=id)
    return TEMPLATES.TemplateResponse(
        '/project/account/depositsIndex.html', 
        {
            "request": request,
            "id": id,
            "index": p.get('account').get('transactions').get('deposit', []),
            "total_deposits": sum([float(item.get('amount')) for item in p.get('account').get('transactions').get('deposit', [])])
        })


@router.post('/account_deposit/{id}')
@login_required
async def project_account_deposit(request):
    id = request.path_params.get('id')  
    username = request.user.username    
    payload = {}
    try:
        async with request.form() as form:
            payload['date'] = timestamp(form.get('date'))
            payload['type'] = form.get('type')
            payload['ref'] = form.get('ref')
            payload['amount'] = float(form.get('amount'))
            payload['payee'] = form.get('payee')
        payload['user'] = username
        #print(username, password)
        result = await handle_transaction(id=id, data=payload)
        #return RedirectResponse(url='/dash', status_code=303)
        return HTMLResponse(f""" <div class="uk-alert-success" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>Ref: {payload.get('ref')} {to_dollars(payload.get('amount'))} was deposited on {form.get('date')}</p>
                                </div>""")
    except Exception as e:
        return HTMLResponse(f"""
                            <div class="uk-alert-warning" uk-alert>
                                <a href class="uk-alert-close" uk-close></a>
                                <p>{str(e)}</p>
                            </div>
                            """)



@router.get("/edit_account_deposit/{id}")
@login_required
async def edit_account_deposit(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    did = idd[1].split('-')
    p = await get_project(id=idd[0])
    account = p.get('account')
    deposit = [dep for dep in account.get('transactions').get('deposit') if dep.get('id') == did[0]][0]
    return TEMPLATES.TemplateResponse("/project/account/editDeposit.html", {
        "request": request, 
        "d": deposit,
        "id": idd[0]

        })



@router.put('/update_account_deposit/{id}')
@login_required
async def update_account_deposit(request):
    id = request.path_params.get('id')
    username = request.user.username  
    p = await get_project(id=id)
    account = p.get('account')    
    dep = {}
    async with request.form() as form:       
        deposit = [item for item in account.get('transactions').get('deposit') if item.get('id') == form.get('id')][0]
    deposit['ref'] = form.get('ref')
    deposit['amount'] = form.get('amount')
    deposit['payee'] = form.get('payee')
    p['activity_log'].append(
                {
                    "id": timestamp(),
                    "title": "update Account deposit",
                    "description": f"""Account Deposit with Refference {deposit.get('ref')} was updated.  Project  {p.get('_id')}
                     Account Transactions by {username} on {today()}"""
                }

            ) 
    if len(form.get('date')) > 1:
         deposit['date'] = timestamp(form.get('date'))
    else: pass
      
    await update_project(data=p)
    return HTMLResponse( f"""
        <div class="uk-alert-success" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p>Account Deposit { deposit.get('ref')} Updated!</p>
            <table  class="uk-table uk-table-small">
                <thead>
                    <tr>
                        <th>Id</th>
                        <th>Date</th>
                        <th>Ref</th>
                        <th>Amount</th>
                        <th>Payee</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>{deposit.get('id')}</td>
                        <td>{deposit.get('date')}</td>
                        <td>{deposit.get('ref')}</td>
                        <td>{to_dollars(deposit.get('amount'))}</td>
                        <td>{deposit.get('payee')}</td>

                    </tr>
                </tbody>
            </table>
        </div>
    """)


# PROCESS WITHDRAWALS

@router.post('/account_withdrawal/{id}')
@login_required
async def project_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


@router.get("/edit_account_withdrawal/{id}")
@login_required
async def edit_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


@router.put('/update_account_withdrawal/{id}')
@login_required
async def update_account_withdrawal(request):
    return HTMLResponse("""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p class="text-sm">Process Not Implemented Yet!.</p>
                    </div>""")


# PROCESS PAYBILLS
@router.get('/project_account_paybills/{id}')
@login_required
async def get_project_account_paybills(request):
    id = request.path_params.get('id')
    p = await get_project(id=id)    
    return TEMPLATES.TemplateResponse('/project/account/projectPaybills.html',                                      
        {
            "request": request,
            "id": id,
            "p": {
                "_id": p.get('_id'),
                "name": p.get("name"),
                "account": {
                    "records": {
                        "paybills": p.get("account").get('records').get('paybills')
                    }                 
                },
                "new_billref": f"""Bill-{ len(p.get("account").get('records').get('paybills')) + 1} """
            },            
        })


@router.get('/paybill_total/{id}')
async def paybill_total(request):   
    id = request.path_params.get('id')
    project = await get_project(id=id.split('-')[0])
    items_total = 0    
    for bill in project.get('account').get('records').get('paybills') :
        if bill.get('ref') == id:
            for item in bill.get('items'):
                items_total += float(item.get('metric').get('cost'))
            bill["itemsTotal"] = items_total
            bill["expence"] = {
                "contractor": items_total * ((item.get('fees', {}).get('contractor', 20 )) / 100),
                "insurance": items_total * ((item.get('fees', {}).get('insurance', 5 )) / 100),
                "misc": items_total * ((item.get('fees', {}).get('misc', 5 )) / 100),
                "overhead": items_total *  ((item.get('fees', {}).get('overhead', 5 )) / 100)
            }
            bill["expence"]["total"] = sum([
                bill["expence"]["contractor"],
                bill["expence"]["insurance"],
                bill["expence"]["misc"],
                bill["expence"]["overhead"],
            ])

 
@router.post('/new_paybill/{id}')
@login_required
async def new_paybill(request):
    bill_refs = set()
    id = request.path_params.get('id')
    username = request.user.username  
    project = await get_project(id=id)
    paybill = {
        'project_id': id, 
        'items': [], 
        'fees': {
            "contractor": 10,
            "insurance": 3,
            "misc": 3,
            "overhead": 3,
            "unit": "%"
        }, 
        'itemsTotal': 0, 
        'total': 0
    }
    for bill in project.get('account').get('records').get('paybills') :
        bill_refs.add(bill.get('ref'))
    try:
        async with request.form() as form: 
            for key in form:
                paybill[key] = form.get(key) 
        paybill['ref'] = f"{id}-{paybill['ref']}"
        if paybill.get('ref') in bill_refs:
            return TEMPLATES.TemplateResponse('/project/account/paybills.html', {
                "request": request,
                "paybills":  project.get('account').get('records').get('paybills')
            }) 
        else:
            project['account']['records']['paybills'].append(paybill)    
            project['activity_log'].append(
                {
                    "id": timestamp(),
                    "title": "Create New Paybill",
                    "description": f"""New Paybill with Refference {paybill.get('ref')} was added to Project  {project.get('_id')} by 
                                                        {username} at {today()}"""
                }
            )   
            await update_project(data=project)
            return TEMPLATES.TemplateResponse('/project/account/paybills.html', {
                "request": request,
                "paybills":  project.get('account').get('records').get('paybills')
            }) 
    except Exception as e:
        return TEMPLATES.TemplateResponse('/project/account/paybills.html', {
                "request": request,
                "paybills":  project.get('account').get('records').get('paybills')
            }) 
    finally:
        del(paybill)



@router.get('/paybill/{id}')
@login_required
async def get_paybill(request):
    id = request.path_params.get('id')
    idd = id.split('-')
    project = await get_project(id=idd[0])
    bill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref').strip() == id][0]
    bill_payees = set()
    for item in bill.get('items'):
        if item.get('paid'):
            if len(item.get('paid')) > 0:
                for statement in item.get('paid'):
                    bill_payees.add(f"{statement.get('employee')}-{statement.get('employee_id')}")

    items_total = 0
    if bill.get('date_starting') and bill.get('date_ending'):
        days = [day_work for day_work in project.get('daywork', []) if filter_dates(date=day_work.get('date'), start=bill.get('date_starting'), end=bill.get('date_ending') ) ]
    else:
        days = []
    if len(days) > 0:
        day_workers = set()#days = sorted(days)
    
        worker_occurence = [ item.get('worker_name') for item in days ]
        for day_worker in worker_occurence:
            day_workers.add(day_worker)
        workers = []
        for worker in list(day_workers):
            name = json.loads(json.dumps(worker.split('_')))
            workers.append({"id": name[1], "name": name[0], "days": worker_occurence.count(worker)})  
        bill["days_work"] = days
        bill["day_workers"] = workers
    else:
        bill["days_work"] = []
        bill["day_workers"] = []
    try:
        if bill.get('expence'):
            pass
        else:
            bill["expence"] = {
                    "contractor": 0,
                    "insurance": 0,
                    "misc": 0,
                    "overhead": 0,
                    "total": 0

                }       
        
        if len(bill.get('items')) == 0: 
            
            bill['fees'] = default_fees()
            project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Auto Update to Project Paybill Properties",
                        "description": f"""Paybill {bill.get('ref')} expence and fee properties has been updated by System Auto Updates. """
                    }
                )      
            await update_project(data=project)            
            return TEMPLATES.TemplateResponse('/project/account/projectPaybill.html',
            {
                "request": request, 
                "bill": bill, 
                "bill_payees": bill_payees,               
                "items_count": len(bill.get('items')) 
                })
        else:
            for item in bill.get('items'):                    
                items_total += float(item.get('metric', {}).get('cost', item.get('metric', {}).get('total', 0))) # check for item cost or total            
            if bill.get('fees', {}).get('contractor' ):
                bill["expence"]["contractor"] = items_total * ((bill.get('fees').get('contractor' )) / 100)
            else:
                bill['fees']['contractor'] = default_fees('contractor') # fallback to default fees
                bill['fees']['unit'] = default_fees('unit') # fallback to default fees
                bill["expence"]["contractor"] = items_total * ((bill.get('fees').get('contractor' )) / 100)            
            if bill.get('fees', {}).get('insurance' ):
                bill["expence"]["insurance"] = items_total * ((bill.get('fees').get('insurance' )) / 100)
            else:
                bill['fees']['insurance'] = default_fees('insurance') # fallback to default fees  
                bill["expence"]["insurance"] = items_total * ((bill.get('fees').get('insurance' )) / 100)            
            if bill.get('fees', {}).get('misc' ):
                bill["expence"]["misc"] = items_total * ((bill.get('fees').get('misc' )) / 100)
            else:
                bill['fees']['misc'] = default_fees('misc') # fallback to default fees
                bill["expence"]["misc"] = items_total * ((bill.get('fees').get('misc' )) / 100)            
            if bill.get('fees', {}).get('overhead' ):
                bill["expence"]["overhead"] = items_total * ((bill.get('fees').get('overhead' )) / 100)
            else:
                bill['fees']['overhead'] = default_fees('overhead') # fallback to default fees 
                bill["expence"]["overhead"] = items_total * ((bill.get('fees').get('overhead' )) / 100)             
            bill["itemsTotal"] = items_total            
            bill["expence"]["total"] = sum([
                    bill["expence"]["contractor"],
                    bill["expence"]["insurance"],
                    bill["expence"]["misc"],
                    bill["expence"]["overhead"],
                ])
            bill['total'] = items_total + bill.get("expence").get("total")
            project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Auto Update to Project Paybill Properties",
                        "description": f"""Paybill {bill.get('ref')} expence and fee properties has been updated by System Auto Updates. """
                    }
                )    
            await update_project(data=project)
            return TEMPLATES.TemplateResponse(
                '/project/account/projectPaybill.html',
                {
                    "request": request, 
                    "bill": bill, 
                    "bill_payees": bill_payees,
                    "items_count": len(bill.get('items')) 
                    })
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)
    finally:
        del(project)
        del(bill)


@router.get('/project_account_withdrawals/{id}')
@login_required
async def get_project_account_withdrawals(request):
    id = request.path_params.get('id')
    generator =  project_account_withdrawal_generator(id=id)
    return StreamingResponse(generator, media_type="text/html")


@router.post('/current_paybill/{id}')
@login_required
async def current_paybill(request):
    id = request.path_params.get('id')    
    try: 
        return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>Current Paybill is {id}.</p>
                        </div>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)
    finally:
        del(id)


@router.get('/unpaid_tasks/{id}')
async def unpaid_tasks(request):     
    id = request.path_params.get('id')
    idd = id.split('-')
    accumulator = ProjectDataAccumulator(project_id=idd[0])
    unpaid_tasks = await accumulator.unpaid_tasks()
    await sleep(1)
    return TEMPLATES.TemplateResponse("/project/account/unpaidTasks.html", {
        "request": request,
        "unpaid_tasks": unpaid_tasks,
        "bill_ref": id
    })


@router.post('/add_task_to_bill/{id}')
@login_required
async def add_task_to_bill(request):
    id = request.path_params.get('id')  
    username = request.user.username    
    project = await get_project(id=id.split('-')[0])
    try:
        async with request.form() as form:
            task_id = form.get('task')
        idds = task_id.split('_')
        for job in project.get('tasks'):
            if job.get('_id') == idds[0]:
                for task in job.get('tasks'):
                    if task.get('_id') == idds[1]:                                   
                        bill_item = {
                                    "id": task.get('_id'),
                                        "job_id": task.get('job_id'),
                                        "title": task.get('title'),
                                        "description": task.get('description'),
                                        "metric": task.get('metric'),
                                        "imperial":task.get('imperial'),
                                        "assignedto": task.get('assignedto'),
                                        "paid": task.get('paid'),
                                        "phase": task.get('phase'),
                                        "progress": task.get('progress'),
                                        "category": task.get('category'),

                                    } 
                        for bill in project.get('account').get('records').get('paybills'):
                            if bill.get('ref').strip() == id.strip():
                                bill['items'].append(bill_item)
                                project['activity_log'].append(
                                    {
                                        "id": timestamp(),
                                        "title": "Add Task Item to Paybill",
                                        "description": f"""Job {job.get('_id')} Task  {task.get('_id')} wae added to Paybill {bill.get('ref')} by 
                                                        {username} at {today()}"""
                                    }
                                )     
            
        await update_project(data=project)
        """return TEMPLATES.TemplateResponse("/project/account/paybillItem.html", {
            "request": request,
            "bill_items": bill.get('items') })"""
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)       
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)
    finally:
        del(id)


@router.get('/process_paybill_dayworker/{id}')
async def process_paybill_dayworker(request):
    id = request.path_params.get('id')
    idds = id.split('_')
    nid = idds[1].split('@')
    dts = nid[1]
    dts = dts.split('&')
    bref = idds[0]
    wname = nid[0]
    start = dts[0]
    end = dts[1]
    project = await get_project(id=id.split('-')[0])     
    days = await process_paybill_dayworker( bill_ref=bref, worker=wname, start_date=start, end_date=end)    
    return TEMPLATES.TemplateResponse(
        "/project/account/paybillDayworkerStatement.html", 
        {
            "request": request,
            "id": id,
            "project": project.get('name'),
            "days_worked": days,
            "worker": wname,
            "start": start,
            "end": end

        }
        )


@router.post('/set_days_rate/{id}')
@login_required
async def set_days_rate(request):
    id = request.path_params.get('id')
    idds = id.split('_')
    nid = idds[1].split('@')
    dts = nid[1]
    dts = dts.split('&')
    bref = idds[0]
    wname = nid[0]
    start = dts[0]
    end = dts[1]
    project = await get_project(id=id.split('-')[0])
    
    
    data = {}
    async with request.form() as form:
        for key in form.keys():
            data[key] = form.get(key)
    if start and end:
        days = [day_work for day_work in project.get('daywork', []) if filter_dates(date=day_work.get('date'), start=start, end=end ) ]
        days = [item for item in days if item.get('worker_name').split('_')[0] == wname]
        for daywork in days:
            daywork['payment']['rate'] = data.get('day_rate')
            #daywork['payment']['amount'] = float(data.get('day_rate'))
        await update_project(data=project)
            
    else:
        days = []

    
    return TEMPLATES.TemplateResponse(
        "/project/account/paybillDaysWorkTable.html",
        {
            "request": request,
            "id": id,
            "days_worked": days,
            "data": data
        }
    ) 
  


@router.post('/apply_paybill_daysrate/{id}')
@login_required
async def apply_paybill_daysrate(request):
    id = request.path_params.get('id')
    idds = id.split('_')
    nid = idds[1].split('@')
    dts = nid[1]
    dts = dts.split('&')
    bref = idds[0]
    wname = nid[0]
    start = dts[0]
    end = dts[1]

    project = await get_project(id=id.split('-')[0])
    
    data = {}
    async with request.form() as form:
        for key in form.keys():
            data[key] = form.get(key)
    if start and end:
        total_days_pay = 0
        days = [day_work for day_work in project.get('daywork', []) if filter_dates(date=day_work.get('date'), start=start, end=end ) ]
        days = [item for item in days if item.get('worker_name').split('_')[0] == wname]
        for daywork in days:
            #form_date = [day_item for day_item in data if day_item.get("id") == daywork.get('id')][0]
            await process_days_work(name=wname, date_id=daywork.get('id'), paid=True, amount= float(daywork.get('payment').get('rate')))
            if data.get(daywork.get('id')):
                
                daywork['payment']['amount'] = float(data.get(daywork.get('id')))
            else:                
                daywork['payment']['amount'] = float(daywork.get('payment').get('rate'))
            daywork['payment']['paid'] = True

            total_days_pay += daywork['payment']['amount'] 
        average_day_pay = total_days_pay / len(days)
        bill_item = {
                "id": f"{ id.split('-')[0] }-{ timestamp() }",
                "job_id": None,
                "title": f"Dayworks for { wname }",
                "description": f"Dayworks for { wname } for Period Starting { start } and ending { end }",
                "metric": {
                    "unit": "day",
                    "quantity": len(days),
                    "price": float(average_day_pay),
                    "total": float(total_days_pay)
                },
                "imperial":{
                    "unit": "day",
                    "quantity": len(days),
                    "price": float(average_day_pay),
                    "total": float(total_days_pay)
                },
                "assignedto": wname,
                "paidout": {
                "unit": "%",
                "value": 100,
                "amount": float(total_days_pay),
                "totalPaidOut": float(total_days_pay)
              },
                "paid": [
                {
                  "job_ref": "",
                  "bill_ref": bref,
                  "bill_item_id": f"{ id.split('-')[0] }-{ timestamp() }",
                  "employee_id": "",
                  "employee": wname,
                  "date": timestamp(),
                  "metric": {
                    "unit": "day",
                    "price": float(average_day_pay),
                    "quantity": len(days),
                    "total": float(total_days_pay)
                  },
                  "imperial": {
                    "unit": "day",
                    "price": float(average_day_pay),
                    "quantity": len(days),
                    "total": float(total_days_pay)
                  },
                  "total": float(total_days_pay)
                }],
                "phase": "n/a",
                "progress": "100",
                "category": "labour"
                } 
        for bill in project.get('account').get('records').get('paybills'):
            if bill.get('ref').strip() == idds[0].strip():
                bill['items'].append(bill_item)
        project['activity_log'].append(
            {
                "id": timestamp(),
                "title": "Add Days Work Item to Paybill",
                "description": f"""Daywork Summary {bill_item.get('id')} for {wname} was added to Paybill {bill.get('ref')} by 
                            {request.user.username}."""
            })  
        
        await update_project(data=project)
            
    else:
        days = []

    
    return TEMPLATES.TemplateResponse(
        "/project/account/paybillDaysWorkTable.html",
        {
            "request": request,
            "id": id,
            "days_worked": days,
            "data": data
        }
    ) 
 


@router.get('/edit_paybill_item/{id}')
@router.post('/edit_paybill_item/{id}')
@login_required
async def edit_paybill_item(request):
    id = request.path_params.get('id') 
    username = request.user.username  
    idd = id.split('_')
    project = await get_project(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == idd[0]][0]
    bill_item = [item for item in paybill.get('items') if item.get('id') == idd[1]][0]
    #print(bill_item)
    if request.method == 'GET':
        
        return TEMPLATES.TemplateResponse('/project/account/editPaybillItem.html', {
            "request": request, 
            "bill_item": bill_item,
            "bill_ref": idd[0]
            
            }  )
    if request.method == 'POST':
        async with request.form() as form:
        
            updates = {
                "id": form.get('id'),
                
            }
            bill_item['id'] = form.get('id')
            if form.get('description'):
                bill_item['description'] = form.get('description')
            if form.get('title'):
                bill_item['title'] = form.get('title')
            bill_item['metric']['unit'] = form.get('metric_unit')
            bill_item['metric']['quantity'] = form.get('metric_quantity')
            bill_item['metric']['price'] = form.get('metric_price')
            bill_item['metric']['cost'] = round(float(bill_item['metric']['quantity']) * float(bill_item['metric']['price']),2)
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Updating Paybill Item",
                        "description": f"""Project Paybill {paybill.get('ref')} Item id {bill_item.get('id')}  was updated by 
                                        {username} on {today()}"""
                    }

                )     
        await update_project(data=project)        
        return RedirectResponse(url=f"/paybill/{idd[0].strip()}", status_code=302)
    

@router.get('/update_contractor_fee/{id}')
@router.post('/update_contractor_fee/{id}')
@login_required
async def update_contractor_fee(request):
    id = request.path_params.get('id')   
    username = request.user.username
    project = await get_project(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ][0]
    
    if request.method == 'GET':
        
        response =f"""
        
            <form><input 
                            type="range" 
                            class="range range-secondary" 
                            name="contractor_fee"
                            min="0"
                            max="40"
                            step="1"
                            value="{paybill.get('fees').get('contractor')}"
                            hx-post="/update_contractor_fee/{paybill.get('ref')}"
                            hx-target="#account"
                            hx-trigger="change delay:500ms"
                            />
                        </form>{paybill.get('fees').get('contractor')}
            </p>
        
        """ 
        
            
    if request.method == 'POST':
        async with request.form() as form:
            fee = int(form.get('contractor_fee'))
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Updating Job Contractor Fees",
                        "description": f"""Project Paybill {paybill.get('ref')} Contractor fee  was updated from {paybill.get('fees', {}).get('contractor')}  to {fee} by 
                                        {username} on {today()}"""
                    }

                )           
        paybill['fees']['contractor'] = fee
        await update_project(data=project)
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
    return HTMLResponse(response)
    


@router.get('/update_insurance_fee/{id}')
@router.post('/update_insurance_fee/{id}')
@login_required
async def update_insurance_fee(request):
    id = request.path_params.get('id')  
    username = request.user.username
    project = await get_project(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ][0]    
    if request.method == 'GET':        
        response =f"""        
            <form><input 
                            type="range" 
                            class="range range-secondary" 
                            name="insurance_fee"
                            min="0"
                            max="40"
                            step="1"
                            value="{paybill.get('fees').get('insurance')}"
                            hx-post="/update_insurance_fee/{paybill.get('ref')}"
                            hx-target="#account"
                            hx-trigger="change delay:500ms"
                            />
            </form>
            <p>{paybill.get('fees').get('insurance')}</p>
        
        """  
    if request.method == 'POST':
        async with request.form() as form:
            fee = int(form.get('insurance_fee')) 
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Updating Job Insurance Fees",
                        "description": f"""Project Paybill {paybill.get('ref')} Insurance fee  was updated from {paybill.get('fees', {}).get('insurance')}  to {fee} by 
                                        {username} on {today()}"""
                    }

                )           
        paybill['fees']['insurance'] = fee
        await update_project(data=project)
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
    return HTMLResponse(response)
    


@router.get('/update_misc_fee/{id}')
@router.post('/update_misc_fee/{id}')
@login_required
async def update_misc_fee(request):
    id = request.path_params.get('id')  
    username = request.user.username
    project = await get_project(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ][0]    
    if request.method == 'GET':        
        response =f"""        
            <form><input 
                            type="number"                            
                            name="misc_fee"                            
                            step="1"
                            value="{paybill.get('fees').get('misc')}"
                            hx-post="/update_misc_fee/{paybill.get('ref')}"
                            hx-target="#account"
                            hx-trigger="change delay:500ms"
                            />
            </form>
            <p>{paybill.get('fees').get('misc')}</p>
        
        """  
    if request.method == 'POST':
        async with request.form() as form:
            fee = int(form.get('misc_fee')) 
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Updating Job Miscellaneous Fees",
                        "description": f"""Project Paybill {paybill.get('ref')} Miscellaneous  was updated from {paybill.get('fees', {}).get('misc')}  to {fee} by 
                                        {username} on {today()}"""
                    }

                )
        paybill['fees']['misc'] = fee
        await update_project(data=project)
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
    return HTMLResponse(response)



@router.get('/update_overhead_fee/{id}')
@router.post('/update_overhead_fee/{id}')
@login_required
async def update_overhead_fee(request):
    username = request.user.username
    id = request.path_params.get('id')  
    project = await get_project(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == id ][0]    
    if request.method == 'GET':        
        response =f"""        
            <form><input 
                            type="range" 
                            class="range range-secondary" 
                            name="overhead_fee"
                            min="0"
                            max="40"
                            step="1"
                            value="{paybill.get('fees').get('overhead')}"
                            hx-post="/update_overhead_fee/{paybill.get('ref')}"
                            hx-target="#account"
                            hx-trigger="change delay:500ms"
                            />
            </form>
            <p>{paybill.get('fees').get('overhead')}</p>
        
        """  
    if request.method == 'POST':
        async with request.form() as form:
            fee = int(form.get('overhead_fee'))            
        paybill['fees']['overhead'] = fee
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Updating Job Fees (Overhead)",
                        "description": f"""Project Paybill {paybill.get('ref')} Overhead was updated from {paybill.get('fees', {}).get('overhead')}  to {fee} by 
                                        {username} on {today()}"""
                    }

                )
        await update_project(data=project)
        return RedirectResponse(url=f"/paybill/{id}", status_code=302)
    return HTMLResponse(response)


@router.get("/project_paybills_cost/{id}")
async def project_paybills_cost(request):
    id = request.path_params.get('id')  
    project = await get_project(id=id)
    paybills_cost = [bill.get('total', 0) for bill in project.get('account').get('records').get('paybills')  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/accountPropertyTally.html", 
        {"request": request, "property_total": sum(paybills_cost), "title": "Total"}
        )



@router.get('/process_employee_salary/{id}')
@login_required
async def process_employee_salary(request):
    id = request.path_params.get('id')
    
    idd = id.split('_')
    eid = idd[0].split('-')[1]
    bid = idd[1]
    pid = bid.split('-')[0]
    
    project = await get_project(id=pid)
    bill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref').strip() == bid][0]
    employee = await get_worker(id=eid)
    pay_item = salary_statement_item_model()
    pay_statement = salary_statement_model()
    pay_statement['ref'] = f"{eid}@{bill.get('ref')}"
    pay_statement['jobid'] = bill.get('ref')
    pay_statement['employeeid'] = eid
    pay_statement['name'] = employee.get('name')
    pay_statement['date'] = timestamp()
    for item in bill.get('items'):
        if item.get('paid'):
            if len(item.get('paid')) > 0:
                for payment in item.get('paid'):                    
                    if payment.get('employee_id') == eid:
                        pay_item['id'] = payment.get("job_ref")
                        pay_item['description'] = item.get('description')
                        pay_item['unit'] = payment.get('metric').get('unit')
                        pay_item['amount'] = payment.get('metric').get('quantity')
                        pay_item['price'] = payment.get('metric').get('price')
                        pay_item['total'] = payment.get('metric').get('total')
                        pay_statement['total'] += pay_item.get('total')
                        pay_statement['items'].append(json.loads(json.dumps(pay_item)))
                        pay_item = {
                                "id": None,
                                "description": None,
                                "unit": None,
                                "amount": 0,
                                "price": 0,
                                "total": 0
                            }                        
    try:
        existing_statement = [statement for statement in project['account']['records']['salary_statements'] if statement.get('ref') == pay_statement.get('ref')]
        if len(existing_statement) > 0:
            existing_statement = existing_statement[0]
            existing_statement.update(pay_statement)
        else:
            project['account']['records']['salary_statements'].append(pay_statement)  
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Process Employee Salary",
                        "description": f"""Salary Statement {pay_statement.get('ref')} for 
                            {employee.get('name')}  on Paybill 
                            {bill.get('ref')} was Processed by {request.user.username} """
                    }

                )      
        await update_project(data=project)
        del(pay_statement['employeeid'])
        del(pay_statement['name'])        
        existing_record =[ record for record in employee.get('account').get('payments') if record.get('ref') == pay_statement.get('ref')]
        if len(existing_record) > 0:
            existing_record = existing_record[0]
            existing_record.update(pay_statement)
        else:
            employee['account']['payments'].append(pay_statement) 
        await update_employee(data=employee)
        return RedirectResponse(url=f"/paybill/{bid}", status_code=302)
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(project)
        del(employee)
        del(pay_item)
        del(pay_statement)
        del(bill)
    



@router.post('/record_employee_loan/{id}')
async def record_employee_loan(request): 
    e = await get_worker(id=request.path_params.get('id')) 
    #return TEMPLATES.TemplateResponse('/employee/employeePage.html', {"request": request, "e": e})
    loan = {
        "id": timestamp(),
        "repayment": []
    }
    async with request.form() as form:
        for key, value in form.items():
            loan[key] = value 
        loan['amount'] = float(loan.get('amount'))    

    e['account']['loans'].append(loan)
    await update_employee(data=e)
    return HTMLResponse(f"""
        <div class="uk-alert-success" uk-alert>
            <a href class="uk-alert-close" uk-close></a>
            <p class="text-sm">{e['account']['loans']}</p>
        </div>
        
    """)



@router.get('/repay_employee_loan/{id}')
@router.post('/repay_employee_loan/{id}')
async def repay_employee_loan(request): 
    id=request.path_params.get('id')
    idd = id.split('_')
    employee = await get_worker(id=idd[0]) 
    
    loan = [item for item in employee.get('account').get('loans') if item.get('id') == int(idd[1])][0]
    if request.method == 'GET':
        form = f""" <form class="mx-auto flex w-full max-w-lg flex-col rounded-xl border border-border bg-backgroundSecondary p-4 sm:p-20">
           
          
            <div class="form-group">
                <div class="flex w-full flex-col gap-2">
                    <div class="form-field">
                        <label class="form-label">Date </label>
            
                        <input type="date"  name="date" class="input max-w-full" />
                        <label class="form-label">
                            <span class="form-label-alt">Please enter a valid date.</span>
                        </label>
                    </div>
                    <div class="form-field">
                        <label class="form-label">
                            <span>Amount</span>
                        </label>
                        <div class="form-control">
                            <input placeholder="Amount here" type="number" step="0.01" name="amount" class="input max-w-full" />
                        </div>
                    </div>
                    <div class="form-field pt-5">
                        <div class="form-control justify-between">
                            <button 
                                type="button" 
                                class="btn btn-primary w-full uk-modal-close"
                                hx-post="/repay_employee_loan/{id}"
                                hx-target="#message"
                            >Pay Amount</button>
                        </div>
                    </div>
                </div>
        </form>"""
    
    if request.method == 'POST':
        payment = { }
        async with request.form() as form:
            payment['date'] = form.get('date')
            payment['amount'] = float(form.get('amount')) 
            if payment.get('amount') == float(loan.get('amount')):
                payment['resolved'] = True
            else: 
                payment['resolved'] = False
                payment['ballance'] = float(loan.get('amount')) - payment.get('amount')
        loan["repayment"].append(payment)
        await update_employee(data=employee)
        return HTMLResponse(f"""<div>{loan}</div>""")
    return HTMLResponse(f"""{form}""")


@router.get("/project_deposits_total/{id}")
async def project_deposits_total(request):
    id = request.path_params.get('id')  
    project = await get_project(id=id)
    if len(project.get('account').get('transactions').get('deposit')) == 0:
        deposits_total = []
    else:
        deposits_total = [float(dep.get('amount', 0)) for dep in project.get('account').get('transactions').get('deposit')  ]
    return TEMPLATES.TemplateResponse(
         "/project/account/accountPropertyTally.html", 
        {"request": request, "property_total": sum(deposits_total), "title": "Total"}
        )



@router.get("/project_withdrawals_total/{id}")
async def project_withdrawals_total(request):
    id = request.path_params.get('id')  
    project = await get_project(id=id)
    withdrawals_total = [float(dep.get('amount', 0)) for dep in project.get('account').get('transactions').get('withdraw')  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/accountPropertyTally.html", 
        {"request": request, "property_total": sum(withdrawals_total), "title": "Total"}
        )

 
   

@router.get("/project_jobs_total/{id}")
async def project_jobs_total(request):
    id = request.path_params.get('id')  
    project = await get_project(id=id)
    jobs_tasks_total = []
    jobs_costs_total = []
    for job in project.get('tasks'):
        if job.get('cost').get('task') > 0:
            jobs_tasks_total.append(job.get('cost').get('task'))
            jobs_costs_total.append(job.get('cost').get('total').get('metric'))

    
    return TEMPLATES.TemplateResponse(
         "/project/account/projectJobsCosts.html", 
        {
            "request": request, 
            "jobs_tasks_total": sum(jobs_tasks_total), 
            "jobs_costs_total": sum(jobs_costs_total),
            "title": "Jobs Tasks Total Cost"
        }
        )



@router.get("/project_expences_total/{id}")
async def project_expences_total(request):
    id = request.path_params.get('id')  
    project = await get_project(id=id)
    expences_total = [float(exp.get('total', 0)) for exp in project.get('account').get('expences')  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/accountPropertyTally.html", 
        {"request": request, "property_total": sum(expences_total), "title": "Total"}
        )



@router.get("/project_purchases_total/{id}")
async def project_purchases_total(request):
    id = request.path_params.get('id')  
    project = await get_project(id=id)
    purchases_total = [float(exp.get('total', 0)) for exp in project.get('account').get('records', {}).get('invoices', [])  ]
    return TEMPLATES.TemplateResponse(
         "/project/account/accountPropertyTally.html", 
        {"request": request, "property_total": sum(purchases_total), "title": "Total"}
        )



@router.get("/project_salaries_total/{id}")
async def project_salaries_total(request):
    id = request.path_params.get('id')  
    project = await get_project(id=id)
    salaries_total = [float(exp.get('total', 0)) for exp in project.get('account').get('records', {}).get('salary_statements', [])  ]
    return TEMPLATES.TemplateResponse(
        "/project/account/accountPropertyTally.html", 
        {"request": request, "property_total": sum(salaries_total), "title": "Total"}
        )



@router.post('/delete_paybill/{id}')
@login_required
async def delete_paybill(request):
    username = request.user.username
    id = request.path_params.get('id')
    idd = id.split('-')
    project = await get_project(id=idd[0])
    try:           
        project['account']['records']['paybills'] = [bill for bill in project.get('account').get('records').get('paybills') if not bill.get('ref').strip() == id.strip()]
                        
        project['activity_log'].append(
                            {
                                "id": timestamp(),
                                "title": "Record Deletion",
                                "description": f"""Project Paybill with refference { id } was deleted by 
                                                {username} """
                            }

                        )
                

        await update_project(data=project)
        return HTMLResponse(f"""<div uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <h3>Notice</h3>
                            <p>Bill with Ref {id} deleted from Records.</p>
                        </div>""")
    except Exception as e:
        return HTMLResponse(f"""<p class="bg-red-400 text-red-800 text-2xl font-bold py-3 px-4"> An error occured! ---- {str(e)}</p> """)

    finally:
        del(id)



# PROCESS SALARIES

@router.post('/get_worker_pay_item/{id}')
async def get_worker_pay_item(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    project = await get_project(id=id.split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == idd[0]][0]
    bill_item = [item for item in paybill.get('items') if item.get('id') == idd[1]][0]

    async with request.form() as form:
        worker_id = form.get('worker').strip()

    employee = await get_worker(id=worker_id)
    data_form = f"""  
        <p class="text-sm font-semibold">{employee.get('name')} Payroll Item </p>
    <form class="mx-auto flex w-full max-w-lg flex-col rounded-xl border border-border bg-backgroundSecondary p-4 sm:p-20">
            <div class="form-group">
                <div class="flex w-full flex-col gap-2">
                    <div class="form-field">
                        <label class="form-label">Title </label>            
                        <input type="text"  name="title"  value="{bill_item.get('title')}" class="input max-w-full" />                        
                    </div>
                    <div class="form-field">
                        <label class="form-label">
                            <span>Description</span>
                        </label>
                        <div class="form-control">
                            <input placeholder="Description here" type="textarea" name="description" value="{bill_item.get('description')}" class="input max-w-full" />
                        </div>
                    </div>
                    <div class="form-field">
                        <label class="form-label">
                            <span>Category</span>
                        </label>
                        <div class="form-control">
                            <input placeholder="Category here" type="textarea" name="category" value="{bill_item.get('category')}" class="input max-w-full" />
                        </div>
                    </div>
                    <div class="flex flex-row">
                        <div class="flex flex-col mx-2 my-5">
                            <p class="text-xs">Metric Properties</p>
                            <div class="form-field">
                                <label class="form-label">
                                    <span>Unit</span>
                                </label>
                                <div class="form-control">
                                    <input placeholder="Metric Unit here" type="text" name="metric_unit" value="{bill_item.get('metric').get('unit')}" class="input max-w-full" />
                                </div>
                            </div>
                            <div class="form-field">
                                <label class="form-label">
                                    <span>Price Per Unit</span>
                                </label>
                                <div class="form-control">
                                    <input placeholder="Price here" type="number" step="0.01" name="metric_price" value="{bill_item.get('metric').get('price')}" class="input max-w-full" />
                                </div>
                            </div>
                            <div class="form-field">
                                <label class="form-label">
                                    <span>Quantity</span>
                                </label>
                                <div class="form-control">
                                    <input placeholder="Quantity" type="number" step="0.01" name="metric_quantity" value="{bill_item.get('metric').get('quantity')}" class="input max-w-full" />
                                </div>
                            </div>
                                                       

                        </div>
                        <div class="flex flex-col mx-2 my-5">
                            <p class="text-xs">Imperial Properties</p>
                            <div class="form-field">
                                <label class="form-label">
                                    <span>Unit</span>
                                </label>
                                <div class="form-control">
                                    <input placeholder="Imperial Unit here" type="text" name="imperial_unit" value="{bill_item.get('imperial').get('unit')}" class="input max-w-full" />
                                </div>
                            </div>
                            <div class="form-field">
                                <label class="form-label">
                                    <span>Price Per Unit</span>
                                </label>
                                <div class="form-control">
                                    <input placeholder="Price here" type="number" step="0.01" name="imperial_price"  value="{bill_item.get('imperial').get('price')}" class="input max-w-full" />
                                </div>
                            </div>
                            <div class="form-field">
                                <label class="form-label">
                                    <span>Quantity</span>
                                </label>
                                <div class="form-control">
                                    <input placeholder="Quantity" type="number" step="0.01" name="imperial_quantity" value="{bill_item.get('imperial').get('quantity')}" class="input max-w-full" />
                                </div>
                            </div>
                           
                        </div>
                    </div>
                    <div class="form-field pt-5">
                        <div class="form-control justify-between">
                            <button 
                                type="button" 
                                class="btn btn-primary w-full uk-modal-close"
                                hx-post="/pay_worker/{id}_{worker_id}"
                                hx-target="#message"
                            >Pay Worker</button>
                        </div>
                    </div>
                </div>
        </form>"""
    
    return HTMLResponse(data_form) #form)


@router.post('/pay_worker/{id}')
async def pay_worker(request):
    id = request.path_params.get('id')
    idd = id.split('_')
    project = await get_project(id=idd[0].split('-')[0])
    paybill = [bill for bill in project.get('account').get('records').get('paybills') if bill.get('ref') == idd[0]][0]
    bill_item = [item for item in paybill.get('items') if item.get('id') == idd[1]][0]
    employee = await get_worker(id=idd[2])

    async with request.form() as form:
        pay_detail = {
                "job_ref": f"{idd[1]}",
                "bill_ref": f"{idd[0]}",
                "bill_item_id": bill_item.get('id'), 
                "employee_id": employee.get('_id'),
                "employee": employee.get('name'),                
                "date": timestamp(),
                "metric": {
                    "unit": form.get('metric_unit'),
                    "price": form.get('metric_price'),
                    "quantity": form.get('metric_quantity'),
                    "total": float(form.get('metric_price')) * float(form.get('metric_quantity'))
                },
                "imperial": {
                    "unit": form.get('imperial_unit'),
                    "price": form.get('imperial_price'),
                    "quantity": form.get('imperial_quantity'),
                    "total": float(form.get('imperial_price')) * float(form.get('imperial_quantity'))
                }
            }
    if bill_item.get('paid'):
        bill_item['paid'].append(pay_detail) 
    else:
        bill_item['paid'] = [pay_detail]
    pay_detail['total'] = pay_detail.get('metric').get('total')
    employee['account']['payments'].append(pay_detail)
    withdrawal = withdrawal_model()
   
    withdrawal['date'] = timestamp()
    withdrawal['amount'] = pay_detail.get('total')
    withdrawal['recipient']['name'] = employee.get('name')
    withdrawal['ref'] = f"{idd[0]}_{idd[1]}"
    project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Pay Employee Salary",
                        "description": f"""Payment Transaction was initiated for 
                        {employee.get('name')} for {bill_item.get('id')} on Paybill {paybill.get('ref')} by {request.user.username} """
                    }

                )
    await update_project(data=project)
    await update_employee(data=employee)    
    return RedirectResponse(url=f"/paybill/{idd[0]}", status_code=302)



@router.get('/project_account_salaries/{id}')
@login_required
async def get_project_account_salaries(request):
    id = request.path_params.get('id')
    p = await get_project(id=id)
    
    return TEMPLATES.TemplateResponse(
        "/project/account/salaryIndex.html",
        {
            "request": request,
            "id": id,
            "salaries": p.get('account').get('records').get('salary_statements', []),
            "total_salary": sum([float(item.get('total', 0)) for item in p.get('account').get('records').get('salary_statements', [])])
         
         }
        )


# Manage Salaries
@router.get('/edit_salary/{id}')
@login_required
async def edit_salary(request):
    username = request.user.username
    id = request.path_params.get('id')
    idd = id.split('_')
    project = await get_project(id=idd[0])
    salary_statement = [statement for statement in project.get('account').get('records').get('salary_statements', []) if statement.get('ref') == idd[1]][0]
    return TEMPLATES.TemplateResponse(
        "/project/account/salaryStatement.html", 
        {
            "request": request, 
            "id": idd[0],
            "salary_statement": salary_statement
        } 
    )


# PROCESS EXPENCES & purchases
@router.get('/project_account_expences/{id}')
@login_required
async def get_project_account_expences(request):
    id = request.path_params.get('id')
    project = await get_project(id)
    return TEMPLATES.TemplateResponse(
        '/project/account/expenceIndex.html',
        {
            "request": request,
            "id": id,
            "expences": project.get('account').get('expences', [])
         }
    )


@router.post('/new_expence/{id}')
@login_required
async def new_expence_record(request):
    expence = {
        "ref": f"EXP-{timestamp()}",
        "date": "",
        "description": "",
        "claimant": "",
        "method": "",
        "total": 0
      }
    async with request.form() as form:
        for key, value in form.items():
            expence[key] = value    
    await add_expence(id=request.path_params.get('id'), data=expence)    
    return RedirectResponse(url=f"/project_account_expences/{ request.path_params.get('id') }", status_code=302)



@router.get('/project_account_purchases/{id}')
@login_required
async def get_project_account_purchases(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    suppliers = await supplier_name_index()    
    return TEMPLATES.TemplateResponse(
        "/project/account/purchasesIndex.html",
        {
            "request": request, 
            "suppliers": suppliers,
            "project": {
                "_id": project.get('_id'),
                "name": project.get('name'),
                "account": {
                    "records": {
                        "invoices": project.get('account').get('records', {}).get('invoices', [])
                    }
                }

            }
        }
    )


#@router.get('/add_invoice_item/{id}/{inv_no}')
@router.put('/get_invoice_item/{id}')
@login_required
async def get_invoice_item(request:Request):
    id = request.path_params.get('id')    
    project_inventories:dict = await get_project_inventory(id=id)
    mat_index = material_index(inventories=project_inventories)    
    async with request.form() as form: 
        inv_no:str = form.get('invoice_no') 
        date:str = form.get('date') 
        supplier:str = form.get('supplier')   
    inv_items:list = get_invoice_items(inv_no=inv_no) # get items from temporary database
    items_count:int = len(inv_items) + 1
    return TEMPLATES.TemplateResponse('/project/account/invoiceItem.html', 
            {'request': request, 'id': id, 'date':date, 'supplier':supplier, 'inv_no': inv_no, 'mat_index': mat_index, 'inv_items':items_count}
        )


@router.post('/add_invoice_item/{id}/{date}/{supplier}')
@login_required
async def add_invoice_item(request):
    """ request id shall be if format /project_id/invoiceno/suppliername""" 
    id = request.path_params.get('id')
    project = await get_project(id=id)
    supplier = Supplier(name= request.path_params.get('supplier') )    
    async with request.form() as form:
        invoice_item = InvoiceItem(
            itemno = form.get('item_no'),
            description = form.get("description"),
            quantity = form.get("quantity"),
            unit = form.get("unit"),
            price = form.get("price"))            
    inv_no = form.get('invoice_no')
    inventory_item = InventoryItem(
            ref=inv_no,
            name=invoice_item.description, 
            amt=invoice_item.quantity, 
            unit=invoice_item.unit,
            stocking_date= str(request.path_params.get('date')),
            supplier=supplier
            )
    #print(inventory_item)
    project['inventory'].update(stock_material(item=inventory_item.model_dump(), inventories=project['inventory']))
    #print(project.get('inventory'))
    await update_project(data=project)
    await sleep(.5)
    save_invoice_item(inv_no=inv_no, data=invoice_item.model_dump())       
    return HTMLResponse(f"""<div class="uk-alert-success" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p>Item {invoice_item.description} was successfully added to Invoice { inv_no}!</p>
                    </div>"""
                )



@router.post('/new_invoice/{id}')
@login_required
async def save_invoice(request):
    id = request.path_params.get('id')
    project = await get_project(id=id)
    suppliers = await supplier_name_index()
    
    async with request.form() as form:
        invoice = {
          "supplier": {
            "_id": None,
            "name": form.get('supplier'),
            "taxid": None
          },
          "invoiceno": form.get('invoice_no'),
          "datetime": form.get('date'),
          "items": [],
          "tax": form.get('tax'),
          "total": form.get('total')
        }
    
    supplier:list = [item for item in suppliers if item.get('name') == invoice.get('supplier').get('name') ]
    if len(supplier) > 0:
        supplier:dict= supplier[0]
        invoice['supplier']['_id'] = supplier.get('_id')
        invoice['supplier']['taxid'] = supplier.get('taxid')
    inv_no=invoice.get("invoiceno")
    items =  get_invoice_items(inv_no=inv_no)   
    invoice['items'] = items
    #print(invoice)
    supplier_record = {
        "id": f"{id}-{inv_no}",
        "ref": inv_no,
        "date": invoice.get("datetime"),
        "amt":  invoice.get("total")
      }
    _supplier = await get_supplier(id=supplier.get('_id'))
    
     
    if len(project.get('account').get('records', {}).get('invoices', [])) > 1:
        for item in project.get('account').get('records', {}).get('invoices', []): # Check for duplicate
            if item.get("invoiceno") == invoice.get("invoiceno") and item.get('supplier').get('name') == invoice.get('supplier').get('name'):     
                return HTMLResponse(f"""<div class="uk-alert-warning" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p>Invoice {invoice.get("invoiceno")} already exists!</p>
                    </div>"""
                )
            else:  
                                    
                project['account']['records']['invoices'].append(invoice) # Append to occupied list
                project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Record Invoice",
                        "description": f"""Invoice {invoice.get("invoiceno")} from  {invoice.get('supplier').get('name')} was Saved by {request.user.username} """
                    }

                )
                
                _supplier['account']['transactions'].append(supplier_record)
                task = BackgroundTask(update_supplier, data=_supplier)
                await update_project(data=project)
                
                return HTMLResponse(f"""<div class="uk-alert-success" uk-alert>
                        <a href class="uk-alert-close" uk-close></a>
                        <p>Invoice {invoice.get("invoiceno")} from  {invoice.get('supplier').get('name')} was saved successfully!</p>
                    </div>""", background=task
                )
    else:                
        project['account']['records']['invoices'].append(invoice) # Append to empty list        
        project['activity_log'].append(
                    {
                        "id": timestamp(),
                        "title": "Record Invoice",
                        "description": f"""Invoice {invoice.get("invoiceno")} from from  {invoice.get('supplier').get('name')} was Saved by {request.user.username} """
                    }

                )
        
        _supplier['account']['transactions'].append(supplier_record)
        task = BackgroundTask(update_supplier, data=_supplier)
        #print(_supplier)
        try:
            
            await update_project(data=project)
            return HTMLResponse(f"""<div class="uk-alert-success" uk-alert>
                            <a href class="uk-alert-close" uk-close></a>
                            <p>Invoice {invoice.get("invoiceno")} was saved successfully!</p>
                        </div>""", background=task
                    )
        finally:            
            reset_invoice_repo()
            


