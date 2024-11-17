
from dataclasses import dataclass
try:
    from modules.project import get_project
except ImportError:   
    from project import get_project


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


