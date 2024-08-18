# Column.py
import json
import asyncio
#from pycal import Water
from modules.estimator.schema import ColumnSchema, RebarSchema
from modules.estimator.slab import lib, logging

class Column:
    def __init__(self, data:dict=None):
        if data:
            self.data=ColumnSchema(data)
            self.set_unit_system(self.data.unit)
           
        else:
            logging.info("Empty column Object Initializd")
    
    def set_unit_system(self, unit): 
        ''' Establish or convert the system of measurement units'''       
        self.usys = lib.set_unit_system(unit)
        logging.info(f"System units converted to {unit}.")
    
    def set_rebars(self, data:dict=None):
        ''' Inserts reinforcing rebars in column system. '''
        if data:
            self.rebar = RebarSchema(data) 
        else:
            logging.info("Failed to insert reinforcements to column system.")

    
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
                self.rebar.hb_length = round(srebar.hb_length / factor,2)                
            elif unit == "m" and self.rebar.unit== 'ft':
                factor = 0.3048
                self.rebar.unit = "m"
                self.rebar.vb_spacing = round(self.rebar.vb_spacing * factor,2)
                self.rebar.hb_spacing = round(self.rebar.hb_spacing * factor,2)
                self.rebar.vb_height = round(self.rebar.vb_height * factor,2)
                self.rebar.hb_length = round(srebar.hb_length * factor,2)                
                self.rebar.vb = await lib.convert_bar(self.rebar.vb)
                self.rebar.hb = await lib.convert_bar(self.rebar.hb)
            elif unit == "ft" and self.rebar.unit== 'mm':
                factor = 304.8
                self.rebar.unit = "ft"
                self.rebar.vb_spacing = round(self.rebar.vb_spacing / factor,2)
                self.rebar.hb_spacing = round(self.rebar.hb_spacing / factor,2)
                self.rebar.vb_height = round(self.rebar.vb_height / factor,2)
                self.rebar.hb_length = round(srebar.hb_length / factor,2)
                self.rebar.vb = await lib.convert_bar(self.rebar.vb)
                self.rebar.hb = await lib.convert_bar(self.rebar.hb) 
            elif unit == "ft" and self.rebar.unit== 'm':
                factor = 3.048
                self.rebar.unit = "ft"
                self.rebar.vb_spacing = round(self.rebar.vb_spacing * factor,2)
                self.rebar.hb_spacing = round(self.rebar.hb_spacing * factor,2)
                self.rebar.vb_height = round(self.rebar.vb_height * factor,2)
                self.rebar.hb_length = round(srebar.hb_length * factor,2)                
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
            self.data.width = self.data.width / factor
            self.data.height = self.data.height / factor
            self.data.depth = self.data.depth / factor            
            self.set_unit_system('m') 
            logging.info("Measurement system Converted from millimeters to meters." )         
        elif unit == 'ft':
            factor = 0.304
            self.data.width = self.data.width * factor
            self.data.height = self.data.height * factor
            self.data.depth = self.data.depth  * factor                      
            self.set_unit_system('m')
            logging.info("Measurement system Converted from feet to meters." )  
        else:
            self.set_unit_system('m')    

    @property 
    def area(self):
        return round(self.data.depth * self.data.width, 2)
    
    @property
    async def process_materials(self):        
        pass

    @property
    async def generate_report(self):
        await self.process_materials
        concrete = await lib.get_resource(f'structure-grades-{self.data.concrete.lower()}') 
        dim = {
                    "width": self.data.width,
                    "height": self.data.height,
                    "depth": self.data.depth,
                    "unit": self.data.unit,
                    "area": {
                    "value": self.area,
                    "unit" : self.usys.get('area')
                    },
                    "dry_volume": {
                            "value": round(self.area * self.data.height, 3),
                            "unit": self.usys.get('volume')
                    },
                    "wet_volume": {
                            "value": round(self.area * self.data.height, 3),
                            "unit": self.usys.get('volume')
                    }
            }
        dim['wet_volume']['value'] = dim.get('dry_volume').get('value') * 1.54
        
        self.report = {
            "title": f"Structural Engineering Report for Building column {self.data.tag}",
            #"column_type": self.data.type,
            #"uri": f'{self.data.type}-{int(self.data.thickness)}',
            "dimension": dim,            
           
            "notes":{                
                "material": {
                   "type": self.data.concrete,
                   
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

    async def html_ui(self):
        return f"""<div class="text-xl font-semibold bg-gray-300 mb-1">Column Estimator</div>
                        <section class="bg-gray-2 rounded-xl">
                            <div class="p-2 shadow-lg">
                                <form 
                                    class="space-y-4" 
                                   
                                >
                                    <div class="w-full">
                                        <label class="sr-only" for="tag">Tag</label>
                                        <input class="input input-solid max-w-full" placeholder="Column Tag" type="text" id="tag" name="tag" />
                                    </div>
                                     <div class="w-full">
                                        <label class="sr-only" for="grid">Grid Label</label>
                                        <input class="input input-solid max-w-full" placeholder="A1" type="text" id="grid" name="grid" />
                                    </div>
                                    
                                    <div class="w-full">
                                        <label class="sr-only" for="type">Type</label>
                                        <input class="input input-solid max-w-full" placeholder="Concrete Type" type="text" id="tconcrete" name="concrete" />
                                    </div>


                                    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2">
                                        <div>
                                            <label class="sr-only" for="unit">Unit</label>
                                            <input class="input input-solid" placeholder="Unit of measurement" type="text" id="unit" name="unit" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="depth">Depth</label>
                                            <input class="input input-solid" placeholder="Depth of the Column" type="number" step="0.1" id="depth" name="depth" />
                                        </div>
                                        <div>
                                            <label class="sr-only" for="width">Width</label>
                                            <input class="input input-solid" placeholder="Width of the Column" type="number" step="0.1" id="width" name="width" />
                                        </div>

                                        <div>
                                            <label class="sr-only" for="height">Height</label>
                                            <input class="input input-solid" placeholder="Height of the Column" type="number" step="0.1" id="height" name="height" />
                                       </div>
                                        <div>
                                            <label class="sr-only" for="amount">Amount</label>
                                            <input class="input input-solid" placeholder="Amount" type="number" step="0.1" id="amount" name="amount" />
                                       </div>
                                    </div>

                                    <div class="w-full">
                                        <label class="sr-only" for="notes">Notes</label>

                                        <textarea class="textarea textarea-solid max-w-full" placeholder="Notes" rows="3" id="notes" name="notes"></textarea>
                                    </div>

                                    <div class="mt-4">
                                        <button 
                                        type="button" 
                                        class="rounded-lg btn btn-primary btn-block"
                                         hx-post="/column"
                                        hx-target="#e-content"
                                        >Send Enquiry</button>
                                    </div>
                                </form>
                            </div>
                        </section>
                        
                        """
    
    async def html_report(self):
        await self.generate_report
        return f""" <div class="card">
                        <div class="card-body">
                            <h2 class="card-header">{self.report.get('title')}</h2>
                            <p class="text-content2">{self.report.get('dimension')}</p>
                            <p class="text-sm">{self.report.get('notes')}</p>
                            <div class="card-footer">
                                <button class="btn-secondary btn">Learn More</button>
                            </div>
                        </div>
                    </div>
                """
    
    def __repr__(self):
        return json.dumps(self.data.to_primitive())
    

def test():    
    column = Column(dict(   
    height= 3800,
    width=402,
    depth=450,
    tag='W23',
    unit='mm'    
    ))
    
    data = {
        "column": column.data.to_primitive,
        "area": column.area,
        "thickness": column.data.thickness


    }
    print(data)

if __name__ == '__main__':
    test()