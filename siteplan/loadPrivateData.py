import asyncio, json
from os import system
from pathlib import Path
from config import BASE_PATH
from modules.supplier import all_suppliers, backup_supplier
from modules.rate import all_rates, backup_industry_rate


private_path:Path = BASE_PATH / 'private'
if private_path.exists():
    pass
else:
    private_path.mkdir()



async def backup_rates():
    rates = await all_rates()
    if rates:
        for item in rates:
            if item.get('metric').get('price'):
                item['metric']['price'] = float(item['metric']['price']) * 1.2 # Raise rates by 20%
            else:
                 pass
            if item.get('imperial').get('price'):
                item['imperial']['price'] = float(item['imperial']['price']) * 1.2 # Raise rates by 20%
            else:
                 pass
            
            del item['_rev'] 
        payload = json.dumps(rates, indent=4)
        json_file = private_path / '2025rateSheet.json'
        
        try:
            if json_file.exists():
                print(f'{json_file} already exists.')
            else:
                print(f'Creating {json_file}')
                with open(json_file, 'w') as out_file:
                    out_file.write(payload)
        except Exception as exception:
                print(exception.__str__())
        finally:
                del rates
                del payload
                del json_file
                del item
                
                

async def backup_suppliers():
    suppliers = await all_suppliers()
    if suppliers:
        for item in suppliers:
            del item['value']['_rev'] 
        payload = json.dumps([item.get('value') for item in suppliers], indent=4)
        json_file = private_path / 'suppliers.json'
        
        try:
            if json_file.exists():
                print(f'{json_file} already exists.')
            else:
                print(f'Creating {json_file}')
                with open(json_file, 'w') as out_file:
                    out_file.write(payload)
        except Exception as exception:
                print(exception.__str__())
        finally:
                del suppliers
                del payload
                del json_file
               

async def load_rates()->None:
    """opens and reads a json file and 
        save items to couchdb datadase

    """
    json_file = private_path / '2025rateSheet.json'
    with open(json_file, 'r') as file:
        payload = json.load(file)
    for item in payload:
        await asyncio.sleep(0.5)
        await backup_industry_rate(data=item)
    
        



async def load_suppliers()->None:
    """opens and reads a json file and 
        save items to couchdb datadase

    """
    json_file = private_path / 'suppliers.json'
    with open(json_file, 'r') as file:
        payload = json.load(file)
    for item in payload:
        await asyncio.sleep(0.5)
        await backup_supplier(data=item)
    
        
        


if __name__ == '__main__':
    system('clear')
    #asyncio.run(backup_suppliers())
    #asyncio.run(backup_rates())
    print( [item for item in private_path.iterdir()] )
    #asyncio.run(load_suppliers())
