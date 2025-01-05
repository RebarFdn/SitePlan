import asyncio
import os
import platform
from websocket import create_connection, WebSocketException



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

        
def coms(uri, args:str=None):
    try:
        ws = create_connection(uri)
        print(f"Successfully Connected to Peer at:")
        ws.send("Employee Anuk moncrieffe")
        res = ws.recv()
        print("Received '%s'" % res)
    except WebSocketException as wex:
        print(wex)
    


       


if __name__ == "__main__":
    print(ConnectedDevices().get_ip_addresses)
    uri = "ws://localhost:8004/peer"
    coms(uri )    