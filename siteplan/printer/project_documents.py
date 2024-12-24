import datetime
import json
from pdfme import build_pdf
from box import Box
from pathlib import Path
from modules.purchase_order import PurchaseOrder

# Config
BASEPATH = Path(__file__).parent.parent
STATIC_PATH = Path.joinpath(BASEPATH.parent, 'static')
DOC_PATH = Path.joinpath(STATIC_PATH, 'docs')


# Currency dollars
def to_dollars(amount:float=None):
    if amount:
        amount = float(amount)
        if amount >= 0:
            return '${:,.2f}'.format(amount)
        else:
            return '-${:,.2f}'.format(-amount)
    else:
        return 0
    

def doc_template(key:str=None):
    doc = {
            "style": {
                'margin_bottom': 15,
                'text_align': 'j',
                 "page_size": "legal", 
                 "margin": [30, 20]
            },
            "formats": {
                'url': {'c': 'blue', 'u': 1},
                'title': {'b': 1, 's': 13},
                'title_header': {'b': 1, 's': 16},
                'sub_title': {'b': .5, 's': 11},
                'sub_text': {'s': 9},
                'line_title': {'b': .5, 's': 8},
                'line_header': {'b': .5, 's': 10},
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
    if key: return json.loads(json.dumps(doc.get(key))) 
    else: return json.loads(json.dumps(doc))
         



# PRINTERS
def printJobQueue(project_jobs:dict=None)-> dict:
        '''Print Job Queue       
        '''
        pj = Box(project_jobs)               
        total_tracker = 0
        con_tracker = 0
        document = doc_template()
        section_1 = {}
        document['sections'].append(section_1)
        section_1['content'] = content_1 = []
        content_1.append({
            '.': f"{pj.name} Jobs Statement", 'style': 'title', 'label': 'title_1',
            'outline': {'level': 1, 'text': 'A different title 1'}
        })
        
        
        content_1.append({
            '.': f"Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
        

        table_def1 = {
            'widths': [ 2, 3, 1.25, 1.25, 1.25, 1.25, 1.5],
            'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': '#133E87', 's': 9},
            
            'fills': [{'pos': '1::2;:', 'color': 0.8}],
            'borders': [{'pos': 'h0,1,-1;:', 'width': 0.5}],
            'table': [
                ['Title', 'Description', 'Metric Amt', 'Metric Price','Imperial Amt', 'Imperial Price', 'Total'],
               
            ]
        }
        
        for item in  pj.jobs:
            title = [ 
                {'.': f"Job {item.get('_id')}", 'style': 'line_title', 'label': 'title_1'},                 
                
                {'.': f"{item.get('title')}", 'style': 'line_header', 'label': 'title_1'},   
                "",
                "",
                "",
                "",
                ""
                ]
            table_def1['table'].append(title)
            for task in item.get('tasks'):
                #task = Box(task)
                if task.get('metric').get('total') == None:
                    task['metric']['total'] = 0
                else:
                    total_tracker += float(task.get('metric').get('total'))
                                 
                data = [ 
                    
                    task.get('title'),
                    task.get('description'),
                    f"{task.get('metric').get('quantity')} {task.get('metric').get('unit')} ",
                    to_dollars(amount=task.get('metric').get('price')),
                    f"{round(float(task.get('imperial').get('quantity')),2)} {task.get('imperial').get('unit')}",
                    to_dollars(amount=round(float(task.get('imperial').get('price')),2)),
                    to_dollars(amount=task.get('metric').get('total'))
                    ]
            
                table_def1['table'].append(data)
        tasks_total = [
            'Jobs Total',
            "",
            "",
            "",
            "",
            "",
            to_dollars(amount=total_tracker)
        ]
        table_def1['table'].append(tasks_total)
        con_tracker = (float(item.get('fees').get('contractor'))/100) * total_tracker
        table_def1['table'].append(
             [
            'Contractor Charges',
            f"{item.get('fees').get('contractor')}%",
            "",           
            "",
            "",
            "",
            to_dollars(amount=con_tracker)
        ]
        )
        table_def1['table'].append(
             [
            'Total Labour Costs',
            "",
            "",           
            "",
            "",
            "",
            to_dollars(amount=con_tracker + total_tracker )
        ]
        )

        
        content_1.append(table_def1)
        file_name = f"{pj.name}-JobsReport.pdf"
        file_path = Path.joinpath(DOC_PATH, file_name)
        with open(file_path, 'wb') as f:
            build_pdf(document, f)
        return {
            "file": file_name,
            'handle': file_path,
            'url': f"/static/docs/{file_name}"
            }


def printMetricJobQueue(project_jobs:dict=None)-> dict:
        '''Print Metric only data Job Queue       
        '''
        pj = Box(project_jobs)               
        total_tracker = 0
        con_tracker = 0
        document = doc_template()
        section_1 = {}
        document['sections'].append(section_1)
        section_1['content'] = content_1 = []
        content_1.append({
            '.': f"{pj.name} Jobs Statement", 'style': 'title', 'label': 'title_1',
            'outline': {'level': 1, 'text': 'A different title 1'}
        })
        
        
        content_1.append({
            '.': f"Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
        

        table_def1 = {
            'widths': [ 2, 2, 3, 1.25, 1.25, 1.5],
            'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': '#133E87', 's': 9},
            
            'fills': [{'pos': '1::2;:', 'color': 0.8}],
            'borders': [{'pos': 'h0,1,-1;:', 'width': 0.5}],
            'table': [
                ['Id', 'Title', 'Description', 'Metric Amt', 'Metric Price', 'Total'],
               
            ]
        }
        
        for item in  pj.jobs:
            title = [ 
                "",
                {'.': f"Job {item.get('_id')}", 'style': 'line_title', 'label': 'title_1'},                 
                
                {'.': f"{item.get('title')}", 'style': 'line_header', 'label': 'title_1'},   
                "",
                "",
                ""
                ]
            table_def1['table'].append(title)
            for task in item.get('tasks'):
                #task = Box(task)
                if task.get('metric').get('total') == None:
                    task['metric']['total'] = 0
                else:
                    total_tracker += float(task.get('metric').get('total'))
                                 
                data = [ 
                    task.get('_id'),
                    task.get('title'),
                    task.get('description'),
                    f"{task.get('metric').get('quantity')} {task.get('metric').get('unit')} ",
                    to_dollars(amount=task.get('metric').get('price')),                   
                    to_dollars(amount=task.get('metric').get('total'))
                    ]
            
                table_def1['table'].append(data)
        tasks_total = [
            'Jobs Total',
            "",
            "",
            "",           
            "",
            to_dollars(amount=total_tracker)
        ]
        table_def1['table'].append(tasks_total)
        con_tracker = (float(item.get('fees').get('contractor'))/100) * total_tracker
        table_def1['table'].append(
             [
            'Contractor Charges',
            f"{item.get('fees').get('contractor')}%",
            "",           
            "",
            "",            
            to_dollars(amount=con_tracker)
        ]
        )
        table_def1['table'].append(
             [
            'Total Labour Costs',
            "",
            "",           
            "",
            "",           
            to_dollars(amount=con_tracker + total_tracker )
        ]
        )
        content_1.append(table_def1)
        file_name = f"{pj.name}-MetricJobsReport.pdf"
        file_path = Path.joinpath(DOC_PATH, file_name)
        with open(file_path, 'wb') as f:
            build_pdf(document, f)
        return {
            "file": file_name,
            'handle': file_path,
            'url': f"/static/docs/{file_name}"
            }


def printImperialJobQueue(project_jobs:dict=None)-> dict:
        '''Print Imperial only data Job Queue       
        '''
        pj = Box(project_jobs)               
        total_tracker = 0
        con_tracker = 0
        document = doc_template()
        section_1 = {}
        document['sections'].append(section_1)
        section_1['content'] = content_1 = []
        content_1.append({
            '.': f"{pj.name} Jobs Statement", 'style': 'title', 'label': 'title_1',
            'outline': {'level': 1, 'text': 'A different title 1'}
        })
        
        
        content_1.append({
            '.': f"Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
        

        table_def1 = {
            'widths': [ 2, 2, 3, 1.25, 1.25, 1.5],
            'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': '#133E87', 's': 9},
            
            'fills': [{'pos': '1::2;:', 'color': 0.8}],
            'borders': [{'pos': 'h0,1,-1;:', 'width': 0.5}],
            'table': [
                ['Id', 'Title', 'Description', 'Amount', 'Price', 'Total'],
               
            ]
        }
        
        for item in  pj.jobs:
            title = [ 
                "",
                {'.': f"Job {item.get('_id')}", 'style': 'line_title', 'label': 'title_1'},                 
                
                {'.': f"{item.get('title')}", 'style': 'line_header', 'label': 'title_1'},   
                "",
                "",
                ""
                ]
            table_def1['table'].append(title)
            for task in item.get('tasks'):
                #task = Box(task)
                if task.get('imperial').get('total') == None:
                    task['imperial']['total'] = 0
                else:
                    total_tracker += float(task.get('imperial').get('total'))
                                 
                data = [ 
                    task.get('_id'),
                    task.get('title'),
                    task.get('description'),
                    f"{round(task.get('imperial').get('quantity'),2)} {task.get('imperial').get('unit')} ",
                    to_dollars(amount=task.get('imperial').get('price')),                   
                    to_dollars(amount=task.get('imperial').get('total'))
                    ]
            
                table_def1['table'].append(data)
        tasks_total = [
            'Jobs Total',
            "",
            "",
            "",           
            "",
            to_dollars(amount=total_tracker)
        ]
        table_def1['table'].append(tasks_total)
        con_tracker = (float(item.get('fees').get('contractor'))/100) * total_tracker
        table_def1['table'].append(
             [
            'Contractor Charges',
            f"{item.get('fees').get('contractor')}%",
            "",           
            "",
            "",            
            to_dollars(amount=con_tracker)
        ]
        )
        table_def1['table'].append(
             [
            'Total Labour Costs',
            "",
            "",           
            "",
            "",           
            to_dollars(amount=con_tracker + total_tracker )
        ]
        )
        content_1.append(table_def1)
        file_name = f"{pj.name}-ImperialJobsReport.pdf"
        file_path = Path.joinpath(DOC_PATH, file_name)
        with open(file_path, 'wb') as f:
            build_pdf(document, f)
        return {
            "file": file_name,
            'handle': file_path,
            'url': f"/static/docs/{file_name}"
            }


def print_project_rates(data:dict=None):
    project_rates:list=data.get('rates')
    project_name:str=data.get('name')
    filter:str = data.get('filter')
    if filter == 'all':
        filter = ""
    else: filter = f"-{filter}"

    document = doc_template()
    section_1 = {}
    document['sections'].append(section_1)
    section_1['content'] = content_1 = []
    content_1.append({
            '.': f"{project_name} {filter} Rate Sheet", 'style': 'title', 'label': 'title_1',
            'outline': {'level': 1, 'text': 'A different title 1'}
    })        
    content_1.append({
            '.': f"Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
    table_def1 = {
            'widths': [ 2, 2.5, 3.5, 1.25, 1.5, 1.5],
            'style': {'border_width': 0, 'margin_left': 20, 'margin_right': 20, 'c': '#133E87', 's': 9},
            
            'fills': [{'pos': '1::2;:', 'color': 0.8}],
            'borders': [{'pos': 'h0,1,-1;:', 'width': 0.5}],
            'table': [
                ['Id', 'Title', 'Description', 'Category', 'Metric', 'Imperial'],
               
            ]
        }
    for rate in project_rates:
        #task = Box(task)                      
        data = [ 
                rate.get('_id'),
                rate.get('title'),
                rate.get('description'),
                rate.get('category'),
                f"{to_dollars(amount=rate.get('metric').get('price'))}/{rate.get('metric').get('unit')} ",
                f"{to_dollars(amount=rate.get('imperial').get('price'))}/{rate.get('imperial').get('unit')} ",
                                
                
                ]
            
        table_def1['table'].append(data)
    content_1.append(table_def1)    
    file_name = f"{project_name}{filter}-RateSheet.pdf"
    file_path = Path.joinpath(DOC_PATH, file_name)
    with open(file_path, 'wb') as f:
        build_pdf(document, f)
    return {
            "file": file_name,
            'handle': file_path,
            'url': f"/static/docs/{file_name}"
        }
        

def printPurchaseOrder(purchase_order:PurchaseOrder=None)-> dict:
    if purchase_order:
        po = purchase_order
        document = doc_template()
        section_1 = {}
        document['sections'].append(section_1)
        section_1['content'] = content_1 = []
        content_1.append({
                '.': f"{po.title}", 'style': 'title', 'label': 'title_1',
                'outline': {'level': 1, 'text': f"{po.title}"}
        })


        content_1.append({'.': f"Order Id: {po.id}", 'style': 'sub_text'})
        content_1.append({'.': f"Site: {po.site}", 'style': 'sub_text'})
        content_1.append({'.': f"Location: {po.location}", 'style': 'sub_text'})        
        content_1.append({
            '.': f"Order Date: {datetime.datetime.now().strftime('%A %d. %B %Y')}", 'style': 'sub_text'})
        
        file_name = f"{po.title}.pdf"
        file_path = Path.joinpath(DOC_PATH, file_name)
        with open(file_path, 'wb') as f:
            build_pdf(document, f)
        return {
            "file": file_name,
            'handle': file_path,
            'url': f"/static/docs/{file_name}"
            }
