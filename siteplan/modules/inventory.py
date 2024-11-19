# inventory.py
from datetime import date
from box import Box
from models.product_models import Supplier, InventoryItem, Inventory


def stock_material(item:dict=None, inventory:dict={})->dict:
    mat = Box(item)  
    inv_keys = inventory.keys()     
    if mat.name in inv_keys:
        material_inventory = inventory.get(mat.name)        
        material_inventory['items'].append(item)
        #print(material_inventory)
    else:
        material_inventory = Inventory(name=mat.name)
        material_inventory.items.append(item)
        inventory[mat.name] = material_inventory.model_dump()
    return inventory


def get_material_inventory(name:str, inventory:Inventory={} )->dict:
    return inventory.get(name)


def get_material_usage(name:str, inventory:Inventory={} )->dict:
    material_inventory:dict = inventory.get(name)
    return material_inventory.get('dispenced')


def log_material_usage(name:str, record:dict=None, inventory:Inventory={} )->dict:
    material_inventory:dict = inventory.get(name)
    material_inventory['dispenced'].append(record)
    return material_inventory.get('dispenced')





s = Supplier(name='Stewarts Hardware')

hp = Supplier(name='Homer Plus Hardware')

jj = Supplier(name="JJ's Depot")

p = InventoryItem(
        ref= 'H042245',
        name='Portland Cement', 
        amt=10, 
        unit='bag',
        stocking_date='2024-10-24',
        supplier=s)
p2 = InventoryItem(
        ref= 'H042255',
        name='Portland Cement', 
        amt=100, 
        unit='bag',
        stocking_date='2024-11-20',
        supplier=s)
p22 = InventoryItem(
        ref= 'H042255',
        name='2x6x14 wpp', 
        amt=10, 
        unit='length',
        stocking_date='2024-11-20',
        supplier=s)
p3 = InventoryItem(
        ref= '7755842',
        name='2x6x16 wpp', 
        amt=18, 
        unit='length',
        stocking_date='2024-11-21',
        supplier=hp)
data = dict(
    ref= '7755842',
    name='2x6x14 wpp', 
    amt=20, 
    unit='length',
    stocking_date='2024-11-21',
    supplier=hp)

p4 = InventoryItem(**data)
p5 = InventoryItem(
        ref= '222623',
        name='1/2x12 J Bolt', 
        amt=40, 
        unit='each',
        stocking_date='2024-04-17',
        supplier=jj)



def test_inventory():
    inv = stock_material(item=p.model_dump())
    #print(inv)
    #print()

    nnv = stock_material(item=p2.model_dump(), inventory=inv)
    #print(nnv)
    nnv = stock_material(item=p3.model_dump(), inventory=nnv)
    #print()
    #print(nnv)
    #print()
    #print(nnv.keys())
    nnv = stock_material(item=p4.model_dump(), inventory=nnv)
    nnv = stock_material(item=p5.model_dump(), inventory=nnv)
    nnv = stock_material(item=p22.model_dump(), inventory=nnv)
    disp = log_material_usage('Portland Cement', ('2024-11-21', 10), nnv)
    #print(nnv)
    #print()
    #print(nnv)
    gnv = Inventory(**get_material_inventory('Portland Cement', nnv)) 
    usage = get_material_usage('Portland Cement', nnv)
    print('Dispenced', usage)
    print('stocked', gnv.stock)

    

