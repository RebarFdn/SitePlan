import json
import asyncio
#from pycal import Water
from modules.estimator.schema import WallSchema, RebarSchema
from modules.estimator.slab import lib, logging

class Wall:
    def __init__(self, data:dict=None):
        if data:
            self.data=WallSchema(data)
            self.set_unit_system(self.data.unit)
           
        else:
            logging.info("Empty Wall Object Initializd")

        if self.data.get('type') == 'cmu':
            self.block = {
                "length": {"unit": 'mm', "value": 400},
                "depth": {"unit": 'mm', "value": 200}
            }
            self.block['area'] = self.block.get('length') * self.block.get('depth')
    
    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.usys = lib.set_unit_system(unit)
        logging.info(f"System units converted to {unit}.")
    
    def set_rebars(self, data:dict=None):
        ''' Inserts reinforcing rebars in wall system. '''
        if data:
            self.rebar = RebarSchema(data) 
        else:
            logging.info("Failed to insert reinforcements to wall system.")

    @property
    async def load_wall_system(self):
        self.wall_system = await lib.get_resource(f'{self.data.type}-{int(self.data.thickness)}')
    
    @property
    async def process_rebars(self):
        unit = self.usys.get('length')
        try:
            if unit == self.rebar.unit:
                pass
            elif unit == "m" and self.rebar.unit== 'mm':
                factor = 1000
                self.rebar.unit = "m"
                self.rebar.vb_spacing = round(self.rebar.vb_spacing / factor,2)
                self.rebar.hb_spacing = round(self.rebar.hb_spacing / factor,2)
                self.rebar.vb_height = round(self.rebar.vb_height / factor,2)
                self.rebar.hb_length = round(self.rebar.hb_length / factor,2)                
            elif unit == "m" and self.rebar.unit== 'ft':
                factor = 0.3048
                self.rebar.unit = "m"
                self.rebar.vb_spacing = round(self.rebar.vb_spacing * factor,2)
                self.rebar.hb_spacing = round(self.rebar.hb_spacing * factor,2)
                self.rebar.vb_height = round(self.rebar.vb_height * factor,2)
                self.rebar.hb_length = round(self.rebar.hb_length * factor,2)                
                self.rebar.vb = await lib.convert_bar(self.rebar.vb)
                self.rebar.hb = await lib.convert_bar(self.rebar.hb)
            elif unit == "ft" and self.rebar.unit== 'mm':
                factor = 304.8
                self.rebar.unit = "ft"
                self.rebar.vb_spacing = round(self.rebar.vb_spacing / factor,2)
                self.rebar.hb_spacing = round(self.rebar.hb_spacing / factor,2)
                self.rebar.vb_height = round(self.rebar.vb_height / factor,2)
                self.rebar.hb_length = round(self.rebar.hb_length / factor,2)
                self.rebar.vb = await lib.convert_bar(self.rebar.vb)
                self.rebar.hb = await lib.convert_bar(self.rebar.hb) 
            elif unit == "ft" and self.rebar.unit== 'm':
                factor = 3.048
                self.rebar.unit = "ft"
                self.rebar.vb_spacing = round(self.rebar.vb_spacing * factor,2)
                self.rebar.hb_spacing = round(self.rebar.hb_spacing * factor,2)
                self.rebar.vb_height = round(self.rebar.vb_height * factor,2)
                self.rebar.hb_length = round(self.rebar.hb_length * factor,2)                
                self.rebar.vb = await lib.convert_bar(self.rebar.vb)
                self.rebar.hb = await lib.convert_bar(self.rebar.hb)
        except Exception as e:
            logging.warning(e)        
  
    # -- Converters ----- 
    @property
    def to_meter(self):
        unit = self.data.unit
        if unit == 'mm':
            factor = 1000
            self.data.length = self.data.length / factor
            self.data.height = self.data.height / factor
            self.data.thickness = self.data.thickness / factor            
            self.set_unit_system('m') 
            logging.info("Measurement system Converted from millimeters to meters." )         
        elif unit == 'ft':
            factor = 0.304
            self.data.length = self.data.length * factor
            self.data.height = self.data.height * factor
            self.data.thickness = self.data.thickness * factor                      
            self.set_unit_system('m')
            logging.info("Measurement system Converted from feet to meters." )  
        else:
            self.set_unit_system('m')    

    @property 
    def area(self):
        return round(self.data.height * self.data.length, 2)
    
    @property
    async def process_materials(self):   
            
        self.blocks = {
            "amount": {
                "value": int(self.area / self.block.get('area').get('value')),
                "unit": "each"
            }
        } 

    @property
    async def generate_report(self):
        await self.process_materials
        concrete = await lib.get_resource(f'structure-grades-{self.data.concrete.lower()}') 
        
        self.report = {
            "title": f"Structural Engineering Report for Building Wall {self.data.tag}",
            "wall_type": self.data.type,
            "uri": f'{self.data.type}-{int(self.data.thickness)}',
            "dimension": {
                    "length": self.data.length,
                    "height": self.data.height,
                    "thickness": self.data.thickness,
                    "unit": self.data.unit,
                    "area": {
                    "value": self.area,
                    "unit" : self.usys.get('area')
                    },
                    "volume": {
                            "value": round(self.area * self.data.thickness, 3),
                            "unit": self.usys.get('volume')
                    }
            },            
            "quantities": self.blocks,
            "notes":{                
                "material": {
                    "type": self.data.type,
                    "data": self.block
                },               
                "concrete": {
                    "qc": concrete.get('quality_controll'),
                    #"cement": concrete.get('cement'),
                    #"aggregates": concrete.get('aggregates'),
                    "target_strength": {
                        "value": concrete.get('mix_procedure').get('target_strength').get('value'),
                        "unit": concrete.get('mix_procedure').get('target_strength').get('unit')
                    },
                    "water_ratio": {
                        "condition": concrete.get('mix_procedure').get('water_ratio').get('condition'),
                        "max": concrete.get('mix_procedure').get('water_ratio').get('max'),
                        "min": concrete.get('mix_procedure').get('water_ratio').get('min')
                    },
                    "aggregate_content": {
                        "nominal": concrete.get('mix_procedure').get('aggregate_content').get('nominal'),
                        "fine": concrete.get('mix_procedure').get('aggregate_content').get('fine')
                    },
                    "cement_content": concrete.get('mix_procedure').get('cement_content')
                   
                }                                 
               
                   
            }
            

        }
    
    def __repr__(self):
        return json.dumps(self.data.to_primitive())
    

def test():
    openings = {'openings: [{"tag": "D1", "unit":"mm", "width": 957.3, "height": 2150, "amount": 5}, {"tag": "WA1", "unit":"mm", "width": 1200, "height": 1200, "amount": 4}]'}
    wall = Wall(dict(   
    height= 3800,
    length=4022,
    tag='W23',
    unit='mm'    
    ))
    
    data = {
        "wall": wall.data.to_primitive,
        "area": wall.area,
        "thickness": wall.data.thickness


    }
    print(data)

if __name__ == '__main__':
    test()