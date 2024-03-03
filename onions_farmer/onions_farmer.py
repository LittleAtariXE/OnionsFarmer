import threading

from time import sleep
from typing import Union

from .app.onion import Onion
from .app.constructor import TorConstructor
from .app.onions_bag import OnionsBag



class OnionFarmer:
    """
    OnionFarmer is responsible for creating and managing Onion objects. It utilizes the Constructor
    to configure each Onion instance. Each created Onion object, along with its external stop event,
    is accessible within the OnionFarmer class, allowing for individual or collective control over
    the Onion instances.
    """
    def __init__(self):
        """
        Initializes the OnionFarmer with a Constructor for setting up Onion configurations.
        Prepares dictionaries to hold Onion objects and their corresponding stop events. Also
        initializes a list to hold OnionsBag objects for managing collections of Onion instances.
        """
        self.Constructor = TorConstructor()
        self.Onions = {}
        self.StopEvents = {}
        self.Bags = []
        self._tmpOnion = []

    def plantOnion(self, name: str = None, local_socks_port: Union[str, int] = None, outside_socks_ip: str = None, torrc: str = None, print_log: bool = False, http_bridge: str = None, config: dict = {}) -> object:
        conf = config
        if not name:
            conf["Name"] = f"myOnion{len(self.Onions) + 1}"
        else:
            conf["Name"] = name
        conf["LocalSocks"] = local_socks_port
        conf["OutSocks"] = outside_socks_ip
        conf["Torrc"] = torrc
        conf["PrintLog"] = print_log
        if http_bridge:
            conf["HttpBridge"] = http_bridge
        onion_cfg = self.Constructor.makeConfig(conf)
        if not onion_cfg:
            return None
        stop = threading.Event()
        onion = Onion(onion_cfg, stop)
        self.Onions[onion_cfg["Name"]] = onion
        self.StopEvents[onion_cfg["Name"]] = stop
        return onion
    
    def getOnion(self, name: str = None) -> Union[bool, object, dict]:
        if not name:
            return self.Onions
        return self.Onions.get(name)
    
    def stopOnion(self, name: str = None) -> None:
        if not name:
            for stop in self.StopEvents.values():
                stop.set()
            return
        stop = self.StopEvents.get(name)
        if not stop:
            print(f"[!!] ERROR: Onion: {name} does not exists [!!]")
            return
        stop.set()
    
    def makeOnionsBag(self, onions_count: int = 1, name: str = None, local_sock_port_num_start: int = 8000, out_proxy_ip: str = None, torrc: str = None, print_log: bool = False, http_bridge_ip: str = None) -> object:
        self._tmpOnion = []
        if not name:
            name = "myOnion"
        for _ in range(onions_count):
            onion_id = len(self.Onions) + 1
            newname = f"{name}{onion_id}"
            port = str(local_sock_port_num_start + (onion_id * 20))
            if out_proxy_ip:
                out_proxy = f"{out_proxy_ip}:{port}"
            else:
                out_proxy = out_proxy_ip
            onion = self.plantOnion(newname, port, out_proxy, torrc, print_log, http_bridge_ip)
            if onion:
                self._tmpOnion.append(onion)
        bag = OnionsBag(self._tmpOnion)
        self.Bags.append(bag)
        self._tmpOnion = []
        return bag

        
