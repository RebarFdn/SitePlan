from pydantic import BaseModel
from flagman import Flagman

from modules.utils import timestamp, generate_id
from typing import List

class PurchaseItem(BaseModel):
    """Represents an item on a materials list or purchase order"""
    item_no: int
    description:str
    quantity: float
    unit: str


class PurchaseOrder(BaseModel):
    id:str = generate_id(name="Purchase Order")
    title: str = "Purchase Order"
    site: str | None = None
    location: str | None = None
    date: int = timestamp()
    __items: List[PurchaseItem] = []
    resolved: bool = False
    
    @property
    def items(self)->list:
        """Material items to be purchased

        Returns:
            list: List of dictionary with material description, 
            amount, and unit of measurement
        """
        return list(self.__items)
    

    def add_item(self, item:PurchaseItem )->None:
        """Add an item to the purchases list 

        Args:
            item (PurchaseItem): A dictionary with Fields [ item_no,
            description, quantity, unit]

        """
        if self.resolved:
            Flagman(title='Closed Order', message='Sorry, The Purchase Order is Closed!').send
            print('Sorry, The Purchase Order is Closed!')
            return False
        else:
            try:
                item.item_no = self.__items.__len__() + 1
                self.__items.append(item)
                return True
            except:
                return False
            
    
    def get_item(self, item_no: int)->PurchaseItem:
        """Get a single item from the Purchase order

        Args:
            item_no (int): Assigned item number on The purchase order list0

        Returns:
            PurchaseItem: _description_
        """
        return [item for item in self.items if item.item_no == item_no][0]
    

    def update_item(self, 
            item_no:int, 
            description:str=None,
            quantity:float=None,
            unit:str=None)->PurchaseItem:    
        if self.resolved:
            Flagman(title='Update Purchase Item', message='Sorry, You cannot operate on a closed Purchase Order !').send
        else:
            try:
                record = self.get_item(item_no)
                if description:
                    record.description = description
                elif quantity:
                    record.quantity = quantity
                elif unit:
                    record.unit = unit
                else:
                    pass
                return record
            except Exception as e:
                Flagman(title='Update Purchase Item', message=str(e)).send
      

    def delete_item(self, item_no:int):
        if self.resolved:
            Flagman(title='Delete Purchase Item', message='Sorry, You cannot operate on a closed Purchase Order !').send
        else:
            try:
                for item in self.__items:
                    if item.item_no == item_no:
                        self.__items.remove(item)
            except Exception as e:
                Flagman(title='Delete Purchase Item', message=str(e)).send    
            
    @property
    def close(self)->None:
        """Resolves the Purchase Order 
        preventing further addition to its contents

        """
        self.resolved = True
        self.__items = tuple(self.__items)

    @property
    def open(self)->None:
        """Opens a Resolved Purchase Order
        for modification in change order situations
        """
        if not self.resolved:
            Flagman(title='Open Order', message='The Purchase Order is already Open to Modification!').send
        else:
            self.resolved = False
            self.__items = list(self.__items)

    
    @property
    def __repr__(self):
        data = self.model_dump()
        try:
            data['items'] = self.items
            return data
        finally:
            del data
