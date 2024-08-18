#slab.py
import json, math, logging
from logging.handlers import TimedRotatingFileHandler
from modules.estimator.schema import SlabSchema, RebarSchema
from modules.estimator.library import Library
from config import (LOG_PATH ,SYSTEM_LOG_PATH ,SERVER_LOG_PATH, APP_LOG_PATH )


lib = Library()

logging.basicConfig(
    filename=APP_LOG_PATH , 
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s',  
    datefmt='%m/%d/%Y %I:%M:%S %p'
    )
root_logger = logging.getLogger('')
logger = logging.handlers.TimedRotatingFileHandler(
    filename=APP_LOG_PATH,
    when='h',
    interval= 12,
    encoding='utf-8')
root_logger.addHandler(logger)

def convert_bar(bar):
    converter = {
        "m6": "1/4",
        "m10": "3/8",
        "m12": "1/2",
        "m16": "5/8",
        "m20": "3/4",
        "3/4": "m20",
        "5/8": "m16",
        "1/2": "m12",
        "3/8": "m10",
        "1/4": "m6"
    }
    return converter.get(bar, '1/2')

class Slab:
    def __init__( 
        self,
        data:dict=None
        ):
        if data:
            self.data = SlabSchema(data)
            self.set_span
            self.set_unit_system(self.data.unit)
        else:
            logging.info("Empty Slab Object Initializd")
                
    # -- Set Up -----  
    
    def set_unit_system(self, unit):
        self.usys = lib.set_unit_system(unit)

    def set_rebars(self, data:dict=None):
        if data:
            self.rebar = RebarSchema(data)            

    @property
    def process_rebars(self):
        unit = self.usys.get('length')
        try:
            if unit == self.rebar.unit:
                pass
            elif unit == "m" and self.rebar.unit== 'mm':
                factor = 1000
                self.rebar.unit = "m"
                self.rebar.b0_spacing = round(self.rebar.b0_spacing / factor,2)
                self.rebar.b1_spacing = round(self.rebar.b1_spacing / factor,2)
                self.rebar.b2_spacing = round(self.rebar.b2_spacing / factor,2)
                self.rebar.t0_spacing = round(self.rebar.t0_spacing / factor,2)
                self.rebar.t1_spacing = round(self.rebar.t1_spacing / factor,2)
                self.rebar.t2_spacing = round(self.rebar.t2_spacing / factor,2)
            elif unit == "m" and self.rebar.unit== 'ft':
                factor = 0.3048
                self.rebar.unit = "m"
                self.rebar.b0_spacing = round(self.rebar.b0_spacing * factor,2)
                self.rebar.b1_spacing = round(self.rebar.b1_spacing * factor,2)
                self.rebar.b2_spacing = round(self.rebar.b2_spacing * factor,2)
                self.rebar.t0_spacing = round(self.rebar.t0_spacing * factor,2)
                self.rebar.t1_spacing = round(self.rebar.t1_spacing * factor,2)
                self.rebar.t2_spacing = round(self.rebar.t2_spacing * factor,2)
                self.rebar.b0 = convert_bar(self.rebar.b0)
                self.rebar.b1 = convert_bar(self.rebar.b1)
                self.rebar.b2 = convert_bar(self.rebar.b2)
                self.rebar.t0 = convert_bar(self.rebar.t0)
                self.rebar.t1 = convert_bar(self.rebar.t1)
                self.rebar.t2 = convert_bar(self.rebar.t2)

            elif unit == "ft" and self.rebar.unit== 'mm':
                factor = 304.8
                self.rebar.unit = "ft"
                self.rebar.b0_spacing = round(self.rebar.b0_spacing / factor,2)
                self.rebar.b1_spacing = round(self.rebar.b1_spacing / factor,2)
                self.rebar.b2_spacing = round(self.rebar.b2_spacing / factor,2)
                self.rebar.t0_spacing = round(self.rebar.t0_spacing / factor,2)
                self.rebar.t1_spacing = round(self.rebar.t1_spacing / factor,2)
                self.rebar.t2_spacing = round(self.rebar.t2_spacing / factor,2)
                self.rebar.b0 = convert_bar(self.rebar.b0)
                self.rebar.b1 = convert_bar(self.rebar.b1)
                self.rebar.b2 = convert_bar(self.rebar.b2)
                self.rebar.t0 = convert_bar(self.rebar.t0)
                self.rebar.t1 = convert_bar(self.rebar.t1)
                self.rebar.t2 = convert_bar(self.rebar.t2)
            elif unit == "ft" and self.rebar.unit== 'm':
                factor = 3.048
                self.rebar.unit = "ft"
                self.rebar.b0_spacing = round(self.rebar.b0_spacing * factor,2)
                self.rebar.b1_spacing = round(self.rebar.b1_spacing * factor,2)
                self.rebar.b2_spacing = round(self.rebar.b2_spacing * factor,2)
                self.rebar.t0_spacing = round(self.rebar.t0_spacing * factor,2)
                self.rebar.t1_spacing = round(elf.rebar.t1_spacing * factor,2)
                self.rebar.t2_spacing = round(self.rebar.t2_spacing * factor,2)
                self.rebar.b0 = convert_bar(self.rebar.b0)
                self.rebar.b1 = convert_bar(self.rebar.b1)
                self.rebar.b2 = convert_bar(self.rebar.b2)
                self.rebar.t0 = convert_bar(self.rebar.t0)
                self.rebar.t1 = convert_bar(self.rebar.t1)
                self.rebar.t2 = convert_bar(self.rebar.t2)
        except Exception as e:
            logging.warning(e)        


    # -- Converters ----- 
    @property
    def to_meter(self):
        unit = self.data.unit
        if unit == 'mm':
            factor = 1000
            self.data.length = self.data.length / factor
            self.data.width = self.data.width / factor
            self.data.thickness = self.data.thickness / factor
            self.set_span
            self.set_quarter_span
            self.set_unit_system('m') 
            logging.info("Measurement system Converted from millimeters to meters." )         
        elif unit == 'ft':
            factor = 0.304
            self.data.length = self.data.length * factor
            self.data.width = self.data.width * factor
            self.data.thickness = self.data.thickness * factor
            self.set_span
            self.set_quarter_span            
            self.set_unit_system('m')
            logging.info("Measurement system Converted from feet to meters." )  
        else:
            self.set_unit_system('m')            
        
    @property
    def set_span(self):
        if self.data.length > self.data.width:
            self.main_span = self.data.width
            self.dist_span = self.data.length
        else:
            self.main_span = self.data.length
            self.dist_span = self.data.width
        
    @property
    def area(self):
        return self.data.width * self.data.length

    @property
    def perimeter(self):
        return math.fsum([self.data.width * 2, self.data.length * 2])          
        
    @property
    def set_quarter_span(self):
        self.main_quarter = self.main_span / 4
        self.dist_quarter = self.dist_span / 4
    
    @property
    def calculate_rebars(self):
        try:
            lib = Library(index='rebar')
            self.rebar_spec = {
                "mainbar_length": round(self.main_span,2),
                "distbar_length": round(self.dist_span ,2),

                "topmain_length": round(self.main_quarter,2),
                "topdist_main_length": round(self.dist_quarter ,2),
                "topmain_dist_length": round((self.main_quarter * 2),2),                
                "topdist_dist_length": round((self.dist_quarter * 2) ,2),

                "quantity": {
                    "mainbars": round(self.main_span / self.rebar.b1_spacing),
                    "distbars": round(self.dist_span / self.rebar.b2_spacing),
                    "topmain": round(self.main_span / self.rebar.t1_spacing),
                    "topdist_main": round(self.dist_span / self.rebar.t1_spacing),
                    "topmain_dist": round((self.main_quarter * 2) / self.rebar.t2_spacing),                
                    "topdist_dist": round((self.dist_quarter * 2)/ self.rebar.t2_spacing)
                },
                "lib": lib.index
            }
            self.rebar_quantites = {}
            self.rebar_report = {
                "notes": {
                    "bottom_bars": {
                    "main": f"{self.rebar_spec.get('quantity').get('mainbars')}-{self.rebar.b1} Bars@{self.rebar.b1_spacing}L-{self.rebar_spec.get('mainbar_length')}(B1)",
                    "distribution": f"{self.rebar_spec.get('quantity').get('distbars')}-{self.rebar.b2} Bars@{self.rebar.b2_spacing}L-{self.rebar_spec.get('distbar_length')}(B2)"
                    },
                    "top_bars": {
                    "main_over": f"{self.rebar_spec.get('quantity').get('topmain')}-{self.rebar.t1} Bars@{self.rebar.t1_spacing}L-{self.rebar_spec.get('topmain_length')}(T1)",
                    "distribution-over": f"{self.rebar_spec.get('quantity').get('topdist_main')}-{self.rebar.t1} Bars@{self.rebar.t1_spacing}L-{self.rebar_spec.get('topdist_main_length')}(T1)",
                    "main_temp": f"{self.rebar_spec.get('quantity').get('topmain_dist')}-{self.rebar.t2} Bars@{self.rebar.t2_spacing}L-{self.rebar_spec.get('topmain_dist_length')}(T2)",
                    "distribution-temp": f"{self.rebar_spec.get('quantity').get('topdist_dist')}-{self.rebar.t2} Bars@{self.rebar.t2_spacing}L-{self.rebar_spec.get('topdist_dist_length')}(T2)"
                   
                    },
                "data": self.rebar_spec
                }
            }

        except Exception as e:
            logging.info(e)

    @property
    async def process_slab(self):       
        self.slab_report = {
            "notes":{
                "dimension": {
                    "length": self.data.length,
                    "width": self.data.width,
                    "thickness": self.data.thickness,
                    "unit": self.data.unit
                },
                "area": {
                    "value": self.area,
                    "unit" : self.usys.get('area')
                },
                "volume": {
                    "value": round(self.area * self.data.thickness, 3),
                    "unit": self.usys.get('volume')
                },                
                "concrete": await lib.get_resource(f'structure-grades-{self.data.concrete}'),
                
                "formwork": {
                    "data": {
                        "wailer_spacing": 0,
                        "joists_spacing": 0,
                        "prop_spacing": 0
                    },
                    "ply": 0,
                    "wailer": 0,
                    "joists": 0,
                    "props": 0,
                    "backup": self.perimeter
                }
            }
        }
               

    def __repr__(self):
        return json.dumps(self.data.to_native())
        



def report():
    slab = Slab({
    "roomname": 'Garage',
    "concrete": "M30",
    "unit": "mm",
    "width": 6000,
    "length":3800,
    "thickness": .125
    })
    slab.set_rebars(dict(
        unit = 'mm',
        b1 = 'm12',
        b2 = 'm12',
        b0 = 'm16',
        t0 = 'm16',
        t1 = 'm12',
        t2 = 'm12',
        b1_spacing = 150,
        b2_spacing = 200,
        b0_spacing = 300,
        t0_spacing = 300,
        t1_spacing = 200,
        t2_spacing = 200
    ))

    slab.set_quarter_span
    slab.process_rebars
    slab.calculate_rebars
    print(slab)
    #slab.data.unit = 'ft'
    print(f"Length {slab.data.length}{slab.usys['length']} Width {slab.data.width}{slab.usys['length']}")
    print(f"Area {slab.area}{slab.usys['area']} Perimeter {slab.perimeter}{slab.usys['length']}")
    try:
        print(f"Main Span {slab.main_span}{slab.usys['length']} Distribution Span {slab.dist_span}{slab.usys['length']}")
        print(f"Main Quarter Span {slab.main_quarter}{slab.usys['length']} Distribution Quarter Span {slab.dist_quarter}{slab.usys['length']}")
        print(f"Rebar Specification {slab.rebar_spec}")
        print(f"Rebar Report {slab.rebar_report}")

        print(f"Rebars {json.dumps(slab.rebar.to_primitive())}")
    except:
        pass
    print()
    slab.to_meter
    slab.process_rebars
    slab.calculate_rebars

    print(f"Length {slab.data.length}{slab.usys['length']} Width {slab.data.width}{slab.usys['length']}")
    print(f"Area {slab.area}{slab.usys['area']} Perimeter {slab.perimeter}{slab.usys['length']}")
    print(f"Main Span {slab.main_span}{slab.usys['length']} Distribution Span {slab.dist_span}{slab.usys['length']}")
    print(f"Main Quarter Span {slab.main_quarter}{slab.usys['length']} Distribution Quarter Span {slab.dist_quarter}{slab.usys['length']}")
    print(f"Rebar Report {slab.rebar_report}")
    try:
        print(f"Rebar Specification {slab.rebar_spec}")
        print(f"Rebars {json.dumps(slab.rebar.to_primitive())}")
    except:
        pass

#report()


