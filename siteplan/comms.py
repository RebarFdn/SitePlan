import asyncio
import os
import platform
from websocket import create_connection, WebSocketException
import httpx 



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


async def get_connect(ip:str)->str:  
    url = f"http://{ip}:8004/handshake"
    try:
        res = httpx.get(url, timeout=0.5)
        return f"ws://{ip}:8004/peer"
    except Exception:
        return None
        
 
async def peer_connection():
    """Seeks to establish a peer connection 
        by a network wide search 
    defaults to localhost 
    """
    #uri = f"ws://{ip}:8004/peer"
    ips:list = ConnectedDevices().get_ip_addresses    
    for ip in ips:       
        res = await get_connect(ip)        
        continue
    print(res) 
    return res          
            


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