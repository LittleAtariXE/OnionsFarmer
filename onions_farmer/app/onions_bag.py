
from threading import Thread
from time import sleep


class OnionsBag:
    """
    The OnionsBag class is designed to manage a collection of Onion objects, allowing for bulk operations
    such as starting Tor processes, stopping them, and obtaining IP addresses. It can automatically 
    handle IP retrieval for each Onion upon start if specified.
    """
    def __init__(self, onions: list, get_ip: bool = True):
        """
        Initializes the OnionsBag with a list of Onion objects.

        :param onions: A list of Onion objects to be managed.
        :param get_ip: A boolean indicating whether to automatically retrieve IP addresses for each Onion. Defaults to True.
        """
        self._onions = onions
        self._get_ip = get_ip
        print("\n** Make Onions Bag Successfull **")
        print(self.__str__())
    
    @property
    def len(self) -> int:
        """
        Returns the number of Onion objects within the bag.

        :return: The count of Onion objects.
        """
        return len(self._onions)
    
    @property
    def isTorConn(self) -> bool:
        """
        Checks if all Onion instances are connected to the Tor network.

        :return: True if all Onion instances are connected; False otherwise.
        """
        for onion in self._onions:
            if onion.isTorConn:
                continue
            else:
                return False
        return True
    
    def openBag(self) -> list:
        """
        Provides access to the list of Onion objects.

        :return: The list of Onion objects.
        """
        return self._onions
    
    def start(self) -> None:
        """
        Starts all Onion instances within the bag. Optionally initiates IP retrieval if set during initialization.
        """
        for onion in self._onions:
            onion.start()
        if self._get_ip:
            getip = Thread(target=self._autoGetIP)
            getip.start()
    
    def stop(self) -> None:
        """
        Stops all Onion instances within the bag.
        """
        for onion in self._onions:
            onion.stop()
    
    def _autoGetIP(self) -> None:
        """
        A private method that waits for all Onion instances to connect before initiating the IP retrieval process.
        """
        while not self.isTorConn:
            sleep(0.3)
        self.getIP()

    
    def _getIP(self) -> None:
        """
        A private method that starts threads for each Onion to retrieve their exit node IP addresses concurrently.
        """
        th = []
        for onion in self._onions:
            t = Thread(target=onion._getIP, daemon=True)
            th.append(t)
            t.start()
        for t in th:
            t.join()
        print("All IP address is obtained")

    def getIP(self) -> None:
        """
        Initiates the process to obtain the exit node IP addresses for all Onion instances within the bag.
        """
        ip = Thread(target=self._getIP)
        ip.start()
        print("Start obtain IP address")
    
    
    def newCircuit(self) -> None:
        """
        Initiates the creation of a new circuit for all Onion instances within the bag.
        """
        for onion in self._onions:
            onion.newCircuit()


    def showOnions(self) -> str:
        info = f"\n{'Name:':<20}{'Local Proxy':<25}{'Out Proxy':<25}{'ExitNodeIP':<20}{'Status':<20}{'IsTorConn':<15}{'BridgeHTTP':<20}\n"
        for onion in self._onions:
            info += onion.info() + "\n"
        return info
    
    def __str__(self) -> str:
        """
        Provides a string representation of the OnionsBag, detailing the contained Onion objects and their statuses.

        :return: A string detailing the OnionsBag's contents and the status of each Onion.
        """
        return self.showOnions()
    

