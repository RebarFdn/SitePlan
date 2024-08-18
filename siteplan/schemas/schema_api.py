##coding='utf-8'
# Data Validation against prescribed schemas |  schema_api.py | Ian Moncrieffe | dec 8 2022

import json
from starlette.responses import JSONResponse
from decoRouter import Router
from pathlib import Path
from os import listdir
from jsonschema import validate 


BASE_PATH = Path(__file__).parent
schemas:list = [item for item in listdir(BASE_PATH) if 'json' in item]


schema = {
    "type" : "object",
    "properties" : {
        "price" : {"type" : "number"},
        "name" : {"type" : "string"},
        },
}
deposit_schema = {
    "#schema": "https://json-schema.org/draft/2020-12/schema",
    "type":"object",
    "properties":{
        "id":{
            "description":"The Unique identifier for a deposit",
            "type":"string"
        },
        "date":{
            "description":"Integer timesamp",
            "type":"integer"
        },
        "type":{"description":"Transaction type flag","type":"string"},
        "amount":{"description":"Figure value of the deposit","type":"number"},
        "ref":{"description":"Refference number","type":"string"},
        "payee":{"description":"Person or Corporation name","type":"string"}
    },
    "required":["date","amount","payee"]
}
location_schema = {
  "$id": "http://localhost:6757/schemas/geographical-location.schema.json",
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "Longitude and Latitude",
  "description": "A geographical coordinate on a planet (most commonly Earth).",
  "required": [ "latitude", "longitude" ],
  "type": "object",
  "properties": {
    "latitude": {
      "type": "number",
      "minimum": -90,
      "maximum": 90
    },
    "longitude": {
      "type": "number",
      "minimum": -180,
      "maximum": 180
    }
  }
}
address_schema = {
    "#schema": "https://json-schema.org/draft/2020-12/schema",    
    "title": "Address",
    "description": "A phycal place in a town or village",
    "type": "object",
    "properties": {
                "lot": {
                    "type": "string"
                },
                "street": {
                    "type": "string"
                },
                "town": {
                    "type": "string"
                },
                "city_parish": {
                    "type": "string"
                },
                "country": {
                    "type": "string"
                },            
                "zip_code": {
                    "type": "string"
                }
        
    }
}
contact_schema = {
    "#schema": "https://json-schema.org/draft/2020-12/schema",    
    "title": "Contact",
    "description": "Methods of commucation",
    "type": "object",
    "properties": {
                "tel": {
                    "type": "string"
                },
                "mobile": {
                    "type": "string"
                },
                "email": {
                    "type": "string"
                },
                "city_parish": {
                    "type": "string"
                }
        
    }
}

project_schema = {
    "$id": "http://localhost:6757/schemas/project_schema.json",
    "$schema": "https://json-schema.org/draft/2020-12/schema",    
    "title": "Project",
    "description": "A Construction Project Built in accrdance with the Jamaican Institute of Builders",
    "type": "object",
    "properties": {
        "_id": {
            "description": "The Unique identifier for a project",
            "type": "string"
        },
        "name": {
            "description": "The Given Name of the Project",
            "type": "string"
        },
        "category": {
            "description": "The Project Construction Classification",
            "type": "string"
        },
        "standard": {
            "description": "The Project system of measurement",
            "type": "string"
        },
        "address": address_schema,
        "owner": {
            "description": "The Client , a person or corporation  that the project belongs to",
            "type": "object",
            "properties": {
                "name": {
                    "type": "string"
                },
                "address": address_schema,
                "contact": contact_schema
            }
        },
        "account": {
            "description": "The Project Financial records",
            "type": "object"
        },
        "tasks":{
            "description": "Lists of job tasks of the Project",
            "type":"array",
                "items": {
                    "type": "object"
                }
        },
        "workers":{
            "description": "Lists of employees on the Project",
            "type":"array",
                "items": {
                    "type": "object"
                },
                "uniqueItems": True
        },
        "inventory":{
            "description": "Lists of Materials for use on the project",
            "type":"array",
                "items": {
                    "type": "object"
                },
                "uniqueItems": True
        },
        "activity_log":{
            "description": "Lists of important events and activities on the project ",
            "type":"array",
                "items": {
                    "type": "object"
                },
                "uniqueItems": True
        },
        "state":{
            "description": "The motive condition of the project",
            "type":"object"
        },
        "event":{
            "description": "Timestamp records of project related events",
            "type":"object"
        },
        "meta_data": {
            "description": "Server records about the project",
            "type": "object"
        }
    },
    "required": [
      "name", "category", "standard"
    ]
}

################################# TESTS ############################

project = dict( 
    name="BeefBone Ranch",
    category = 'commercial',
    standard = 'metric',
    address = {'lot': '5', 'street': 'simms rd'},
    owner = {},
    account = {},
    tasks = [],
    workers = [],
    inventory = [],
    activity_log=[],
    event = {},
    state = {},
    
)

deposit = {
    "id": "CC7725",
    "date": 1660694400000,
    "type": "deposit",
    "amount": 1700000.9,
    "ref": "CONFND7XX",
    "payee": "Clayton"
}

def validate_data(data, schema):
    try:
        validate(instance=data, schema=schema)
        return True
    except Exception as e:
        print(str(e))
        return False

print(validate_data(project, project_schema))
#validate(instance={"name" : "Eggs", "price" : '34.99'}, schema=schemas[1])


 
# returns JSON object as
# a dictionary

 