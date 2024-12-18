from pydantic import BaseModel, Field
from notifypy import Notify 
from config import STATIC_PATH


class Flagman(BaseModel):
    title:str 
    message: str 
    __icon_path:str = STATIC_PATH / 'imgs' / 'logo.png'


    @property
    def send(self):
        notifier = Notify()
        notifier.title = self.title 
        notifier.message= self.message 
        notifier.icon = self.__icon_path
        notifier.send()

if __name__ == '__main__':
    flagman = Flagman(title="Testing the Flagman", message="This is a test of our newest Notification Module!").send
    #flagman.send