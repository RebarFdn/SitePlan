import asyncio
import os
import platform
import httpx
from websocket import create_connection, WebSocketException
from tinydb import TinyDB, Query
from config import DATA_PATH, PORT
from modules.utils import  timestamp

# Database Operations
def ip_database(db_name:str=None)->str:
    return TinyDB(DATA_PATH / db_name)
database = ip_database(db_name="ip.json")

def save_ip_list(ip_lst:list):
    data = {
        "id": timestamp(),
        "title": "Connected Peer Device List",
        "peers": ip_lst 
        }
    database.insert(data)  

class ConnectedDevices:
    def __init__(self):
        self.ips:list = []

    @property
    def get_win_ips(self) -> list:
        """_summary_

        Returns:
            list: _description_
        """        
        out = os.popen('arp -a').read().splitlines()
        for i, line in enumerate(out, start=1):
            if i == 0:
                continue
            ip = line.split()
            if ip:
                ip = ip[0]
                if '192.' in ip:
                    self.ips.append(ip)
        return self.ips

    @property
    def get_unix_ips(self)->list:
        """Find  Devices connected to the local network

        Returns:
            list: list of IP addresses of connected devices
        """       
        out = os.popen('ip neigh show').read().splitlines()
        for i, line in enumerate(out, start=1):
            ip = line.split(' ')[0]        
            self.ips.append(ip)
        return self.ips

    @property
    def get_ip_addresses(self):
        addr = platform.uname()
        if addr.system == 'Linux':
            return self.get_unix_ips
        elif addr.system == 'Windows':
            return self.get_win_ips
        else:
            return []
        
    
    def generate_ips(self, range_max:int=55):
        ips:list = []
        for i in range(0, range_max):
            ips.append(f"192.168.0.{i + 1}")
        del ips[0]
        return ips


async def get_connect(ip:str)->bool: 
    """Verify if the ip address is a peer connection""" 
    url = f"http://{ip}:{PORT}/handshake"
    try:
        res = httpx.get(url, timeout=0.5)
        return True
    except Exception:
        return False        
 
async def peer_connection()->list:
    """Search the local network for connected peer devices  
         
    Returns a list of ip address and websocket path tuple
    """  
    peer_ips:list = []  
    ips:list = ConnectedDevices().generate_ips(24)   
    for ip in ips:       
        if await get_connect(ip):
            peer_ips.append((ip , f"ws://{ip}:{PORT}/peer" ))  
    # save peer list
    if peer_ips:
       save_ip_list(peer_ips)         
    return peer_ips    
            


def coms(uri, args:str=None):
    try:
        ws = create_connection(uri)
        print(f"Successfully Connected to Peer at: {uri}")
        ws.send(args)
        return ws.recv()        
    except WebSocketException as wex:
        print(wex)
    finally:
        ws.close()
    
async def peer_client(args):
    uri = await peer_connection()
    if uri:
        json_data = coms(uri=uri, args=args) 
        print(json_data)  
        return json_data
    else:
        return {"no_protocol": 'Failed to establish a peer connection'} 

if __name__ == "__main__":
    asyncio.run(peer_client('worker Delroy Lewis'))
    
    
    
    
    #coms(uri , 'worker Anuk Moncrieffe')    