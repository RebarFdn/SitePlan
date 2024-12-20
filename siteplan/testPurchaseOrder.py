from time import sleep
import os
#from pympler import asizeof
from modules.utils import generate_id,timestamp
from datetime import date
from box import Box
from modules.purchase_order import ( PurchaseItem, PurchaseOrder, database, 
    get_order, all_order,save_order, update_order, delete_order )

# Test Data 
purchase1 = PurchaseItem(item_no=12, description='wire nails', quantity=10.5, unit='lb')
purchase2 = PurchaseItem(item_no=162, description='Concrete nails', quantity=30.5, unit='lb')
purchase3 = PurchaseItem(item_no=12, description='Portland Cement', quantity=50, unit='bag')
purchase4 = PurchaseItem(item_no=162, description='2x4x16 WPP Lubmer', quantity=120, unit='length')

order = PurchaseOrder(
        id='PO445',
        title="Perliminary Materials List", 
        site='D Daniels Dwelling', 
        location='89 Atrium Housing Development, Bushy Pk. St Catherine.',
        date=123495
        
        )
order2 = PurchaseOrder(        
        title="Beltcourse and Roofing Materials List", 
        site='D Daniels Dwelling', 
        location='89 Atrium Housing Development, Bushy Pk. St Catherine.',        
        
        )
order2.add_item(purchase3)
order2.add_item(purchase4)
 

def test_get_order(id='PO445'):
    order = get_order(id=id)
    try: print(order)
    finally: del order



def test_all_orders():
    all_es = all_order()
    try: print(all_es)
    finally: del all_es



def main():   
    interval = 20   
    print(f'WARNING!  Data will Disappear in { interval } seconds intervals....')
    #save_order(data=order2.__json__)
    order = get_order(id='PO445')
    #order.add_item(purchase1)
    #print(order.model_dump())  
    #print('closing order') 
    #order.close
   # sleep(1)
    order.add_item(purchase3) 
    #order.open
    #print('opening order') 
    #order.add_item(purchase2)
    #order.items.append(purchase2)
    sleep(1)
    
    #order.close
    
    #Item = order.get_item(2)
    #print('saved', save_order(data=order.__json__))
    #print('Order Item', order.get_item(2))
    #order.delete_item(2)
    #print('repr', order.__repr__)
    print()
    #print('json', order.__json__)
    #test_all_orders()
    #test_get_order(id='PO445')
    print(order.items)
   



    
    #print(database)
    sleep(interval)
    os.system('clear')
    
    


if __name__ == '__main__':
    
    main()    
    
    

