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
            
    @property
    def close(self)->None:
        """Resolves the Purchase Order 
        preventing further addition to its contents

        """
        self.resolved = True
        self.__items = tuple(self.__items)

    @property
    def items(self):
        return list(self.__items)
