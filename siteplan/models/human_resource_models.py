from datetime import date
from enum import Enum
from uuid import UUID, uuid4
from typing import List
from pydantic import BaseModel, EmailStr


class Department(Enum):
    HR = 'HR'
    SALES = 'SALES'
    IT = 'IT'
    ENGINEERING = 'ENGINEERING'
    CONSTRUCTION= 'CONSTRUCTION'


class Roles(Enum):
    ADMIN = 'ADMIN'
    GUEST = 'GUEST'
    USER = 'USER'
    STAFF = 'STAFF'
    WORKER = 'WORKER'


class Address(BaseModel):
    lot: str | None = None
    street: str | None = None
    town: str | None = None
    city_parish: str | None = None
    zip: str | None = None


class Contact(BaseModel):
    tel: str | None = None
    mobile: str | None = None
    email: EmailStr | None = None
    watsapp: str | None = None


class Bank(BaseModel):
    name: str | None = None
    branch: str | None = None
    account: str | None = None
    account_type: str = "savings"


class Loan(BaseModel):
    id: str


class Payment(BaseModel):
    id: str


class Account(BaseModel):
    bank: Bank | None = None
    payments: List[Payment]
    loans: List[Loan]

class CommercialAccount(BaseModel):
    bank: Bank | None = None
    transactions: list = []


class Supplier(BaseModel):
    _id: str  | None = None
    name:str      
    taxid: str | None = None
    account: CommercialAccount | None = None
    address: Address | None = None
    contact: Contact | None = None
        

class NextOfKin(BaseModel):
    name: str | None = None
    relation: str | None = None
    address: Address | None = None
    contact: Contact | None = None


class EmployeeState(BaseModel):
    employed: bool = False    
    on_leave: bool = False
    terminated: bool | None = False
    active: bool | None = False
    

class EmployeeEvent(BaseModel):
    employed: date | None = None
    started: date | None = None
    on_leave: List[ date ] | None = None
    resumption: List[ date ] | None = None
    terminated: date | None = None


class EmployeeStats(BaseModel):
    sex: str | None = None
    dob: date | None = None
    height: str | None = None


class Identity(BaseModel):
    identity: str | None = None
    id_type: str | None = None
    trn: str | None = None

class Occupation(BaseModel):
    occupation: str | None = None
    rating: float | None = None  

class JobTasks(BaseModel):
    jobs: List[ str ]
    tasks: List[ str ]
    


class BaseEmployee(BaseModel):
    employee_id: UUID = uuid4() 
    _id:str | None = None
    name: str
    oc: str | None = None
    identity: Identity | None = None
    stats: EmployeeStats | None = None
    occupation: Occupation | None = None
    added: date | None = None      
    imgurl: str | None = None    
    address: Address | None = None
    contact: Contact | None = None
    account: Account | None = None
    nok: NextOfKin | None = None
    jobtask: JobTasks 
    state: EmployeeState | None = None
    event: EmployeeEvent | None = None
    department: Department | None = None
    role: Roles | None = None
    
'''
url = ["http://localhost/employee_by_name/Ausar Moncrieffe", "http://localhost/employee_name_index"]
data = get(url[1]).json()
#employee = Employee( ** dict(name='Jack Price', oc='Big Jack', sex='male', occupation='plumber') )
 #for item in data:
worker = get(f"http://localhost/employee_by_name/Ausar Moncrieffe").json()
c = worker.get('contact')
c.get('email')

def convert_empty_string(_string:str=None):
    if type(_string == str ):        
        if len(_string) == 0:
            return None
        else:
            pass

for item in c:
    c[item] = convert_empty_string(_string= c.get(item))      
        
#e = Employee( ** worker )
sleep(0.1)
    
print(worker.get('contact')) 

'''


