# inventory.py
from datetime import date
from box import Box
from models.product_models import Supplier, InventoryItem, Inventory


def stock_material(item:dict=None, inventories:dict={})->dict:
    mat = Box(item)  
    inv_keys = inventories.keys()     
    if mat.name in inv_keys:
        inventory = inventories.get(mat.name)     
        inventory['items'].append(item)
        #print(material_inventory)
    else:
        inventory = Inventory(name=mat.name)
        inventory.items.append(item)
        inventories[mat.name] = inventory.model_dump()
    return inventories


def get_material_inventory(name:str, inventories:dict={} )->dict:
    return inventories.get(name)


def get_material_usage(name:str, inventories:dict={} )->dict:
    material_inventory:dict = inventories.get(name)
    return material_inventory.get('dispenced')


def log_material_usage(name:str, record:dict=None, inventories:dict={} )->dict:
    material_inventory:dict = inventories.get(name)
    material_inventory['dispenced'].append(record)
    return material_inventory.get('dispenced')


def available_material(name:str, inventories:dict={} )->dict:
    material_inventory:dict = inventories.get(name)






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
    invs = stock_material(item=p.model_dump())
    #print(inv)
    #print()

    nnvs = stock_material(item=p2.model_dump(), inventories=invs)
    #print(nnv)
    nnvs = stock_material(item=p3.model_dump(), inventories=nnvs)
    #print()
    #print(nnv)
    #print()
    #print(nnv.keys())
    nnvs = stock_material(item=p4.model_dump(), inventories=nnvs)
    nnvs = stock_material(item=p5.model_dump(), inventories=nnvs)
    nnvs = stock_material(item=p22.model_dump(), inventories=nnvs)
    log_material_usage('Portland Cement', ('2024-11-21', 10), nnvs)
    log_material_usage('1/2x12 J Bolt', ('2024-04-20', 30), nnvs)
    log_material_usage('Portland Cement', ('2024-11-25', 72), nnvs)
    log_material_usage('1/2x12 J Bolt', ('2024-04-25', 6), nnvs)
    #print(nnv)
    #print()
    #print(nnv)
    gnv = Inventory(**get_material_inventory('Portland Cement', nnvs)) 
    usage = get_material_usage('Portland Cement', nnvs)
    print('Dispenced', usage)
    print('stocking', gnv.stocking)
    print('stocked', gnv.stock)
    print('Usage', gnv.stock_usage)
    print('Available', gnv.available_stock)

    

