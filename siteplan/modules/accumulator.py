
from dataclasses import dataclass
from collections import ChainMap
from modules.project import get_project
from modules.project import all_projects
from modules.employee import all_workers
from modules.rate import all_rates
from flagman import Flagman

def ListToDict(lst:list)->dict:
    res_dct = {lst[i].get("id") : lst[i] for i in range(0, len(lst))}
    return res_dct

def RateListToDict(lst:list)->dict:
    res_dct = {lst[i].get("_id") : lst[i] for i in range(0, len(lst))}
    return res_dct


async def accumulate():
    projects = await all_projects()
    workers = await all_workers()
    rates = await all_rates()
    accumulated:ChainMap = ChainMap(ListToDict(workers), ListToDict(projects), RateListToDict(rates))
    try:
        return accumulated
        
    except Exception as ex:   
        Flagman(title='Data Acculator', message=str(ex))
        

@dataclass
class ProjectDataAccumulator:
    project_id:str

    async def unpaid_tasks(self):
        if self.project_id:
            unpaid = []
            project = await get_project(id=self.project_id)
            jobs = project.get('tasks')
            for job in jobs:
                if job.get('state').get('complete'):
                    pass
                else:
                    for item in job.get('tasks'):
                        
                        if type(item.get('paid')) == dict:
                            if item.get('paid').get('value') < 100 and item.get('progress') > 0:
                                item['job_id']=job.get('_id')
                                unpaid.append(item)
                            else:
                                pass
                        else:
                            if item.get('progress') > 0:
                                item['job_id']=job.get('_id')
                                unpaid.append(item)
            return unpaid
        else:
            return []


