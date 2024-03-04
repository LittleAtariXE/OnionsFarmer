import threading

from time import sleep
from typing import Union

from .app.onion import Onion
from .app.constructor import TorConstructor
from .app.onions_bag import OnionsBag



class OnionsFarmer:
    """
    The OnionsFarmer class acts as a central manager for creating, configuring, and controlling multiple Tor instances,
    referred to as Onion objects. Utilizing the TorConstructor for initial setup, it facilitates the creation of Onion
    instances based on user-defined or default configurations. This class supports individual control of each Onion,
    as well as collective management through the concept of an OnionsBag, which groups multiple Onions for convenient
    bulk operations. Key functionalities include creating single Onion instances, managing collections of Onions,
    and performing actions like starting, stopping, and configuring Onion instances.
    """
    def __init__(self, onions_dir_path: str = None):
        """
        Initializes the OnionsFarmer with optional directory path settings for Tor configurations.
        It sets up the environment necessary for managing Onion instances by initializing the TorConstructor,
        preparing storage for Onion objects and their corresponding stop events, and a list to hold OnionsBag
        objects for group management of Onions.

        :param onions_dir_path: Optional. Specifies the base directory path for storing Tor configurations and related files.
        """
        self.Constructor = TorConstructor(onions_dir_path)
        self.Onions = {}
        self.StopEvents = {}
        self.Bags = []
        self._tmpOnion = []

    def plantOnion(self, name: str = None, local_socks_port: Union[str, int] = None, outside_socks_ip: str = None, torrc: str = None, print_log: bool = False, http_bridge: str = None, config: dict = {}) -> object:
        """
        Creates a new Onion (Tor instance) with specified configurations. If certain parameters are not provided,
        defaults are applied. Each Onion is assigned a unique name and configuration, including local and outside
        SOCKS settings, Tor configuration file (torrc), and optional HTTP bridge support.

        :param name: Optional. A unique name for the Onion instance. If not specified, a default name is generated.
        :param local_socks_port: Optional. The local SOCKS port number for the Onion's proxy.
        :param outside_socks_ip: Optional. The IP address for an outside SOCKS proxy.
        :param torrc: Optional. Path to a custom Tor configuration file.
        :param print_log: Optional. Enables printing Tor logs to the console.
        :param http_bridge: Optional. Specifies if and how an HTTP bridge should be configured.
        :param config: Optional. A dictionary of additional configuration options.
        :return: The created Onion object or None if the creation failed.
        """

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
        """
        Retrieves an Onion object by name. If no name is provided, returns a dictionary of all Onion objects managed by
        OnionsFarmer. This method allows for direct access to individual Onion instances or a collection of all instances
        for inspection or management.

        :param name: Optional. The name of the Onion instance to retrieve.
        :return: An Onion object, a dictionary of Onion objects, or False if the specified Onion does not exist.
        """

        if not name:
            return self.Onions
        return self.Onions.get(name)
    
    def stopOnion(self, name: str = None) -> None:
        """
        Stops an Onion (Tor instance) by name. If no name is provided, stops all Onions managed by OnionsFarmer.
        This method signals the Onion instances to terminate their Tor processes, offering a way to gracefully
        shut down individual or all Tor instances.

        :param name: Optional. The name of the Onion instance to stop. If not specified, all Onions are stopped.
        """

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
        """
        Creates a collection of Onion instances, known as an OnionsBag, with the ability to configure each Onion
        in the bag with sequential local SOCKS port numbers and optional parameters. This method streamlines the
        process of initializing multiple Tor instances for bulk management.

        :param onions_count: The number of Onion instances to create and add to the OnionsBag.
        :param name: Optional. Base name for Onion instances. Unique identifiers are appended to each instance.
        :param local_sock_port_num_start: The starting port number for the local SOCKS configuration. Sequential ports are used for each Onion.
        :param out_proxy_ip: Optional. The IP address for an outside SOCKS proxy.
        :param torrc: Optional. Path to a custom Tor configuration file for the Onions.
        :param print_log: Optional. Enables printing Tor logs to the console for each Onion.
        :param http_bridge_ip: Optional. Specifies if and how an HTTP bridge should be configured for each Onion.
        :return: The created OnionsBag object containing the newly created Onion instances.
        """
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

        
