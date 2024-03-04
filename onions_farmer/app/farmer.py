import socket
import os
import re

from time import sleep
from datetime import datetime
from threading import Thread
from typing import Union



class Farmer:
    """
    The Farmer class is responsible for managing communication with the Tor control port. It facilitates
    authentication, sending commands, and monitoring the status of the Tor connection. This class enables
    operations such as checking Tor connectivity, renewing Tor circuits for new identities, and logging
    interactions with the control port for debugging and monitoring purposes.
    """
    def __init__(self, config: dict, onion_callback: object):
        """
        Initializes the Farmer object with Tor configuration and a callback reference to the associated Onion object.
        It sets up the path to the control socket, log file locations, and other necessary configurations for managing
        the Tor process.

        :param config: A dictionary containing configuration details for the Tor process, including paths and settings.
        :param onion_callback: A reference to the Onion object that this Farmer instance will manage and interact with.
        """

        self.onion = onion_callback
        self.conf = config
        self.name = self.conf["Name"]
        self.sockPath = self.conf["CtrlSocketPath"]
        self.logFile = self.conf["LogSocketFile"]
        self.raw_len = self.conf.get("RawLen", 2048)
        self.format = self.conf.get("FormatCode", "utf-8")
        self._isCtrlConn = False
        self.stopEvent = self.onion.stopEvent
        self._pauseLoop = self.conf.get("PauseLoop", 0.5)
    
    def addLog(self, text: str) -> None:
        """
        Appends a new log entry to the specified log file. This method is used for tracking events, operations,
        and interactions with the Tor control port over time.

        :param text: The log message to be recorded.
        """
        with open(self.logFile, "a") as f:
            _time = datetime.now()
            f.write(f"{_time.strftime('%d:%m:%Y  %H:%M')} -- {text}\n")
    
    def socketConnect(self) -> bool:
        """
        Attempts to establish a connection to the Tor control socket as specified in the configuration. It handles
        the initial authentication process with the control port upon successful connection.

        :return: True if successfully connected and authenticated with the Tor control socket, False otherwise.
        """
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect(self.sockPath)
            self.socket.settimeout(2)
            print(f"[{self.name}] Connect to Control Socket")
            self.addLog("Connect to Control Socket")
            self.sendMsg('AUTHENTICATE ""\r\n')
            print(f"[{self.name}] Recive Authenticate: {self.reciveMsg()}")
            return True
        except:
            return False
    
    def sendMsg(self, msg: str) -> None:
        """
        Sends a command message to the Tor control socket. This method is essential for issuing commands and
        requests to the Tor process via the control port.

        :param msg: The command message to be sent to the Tor control socket.
        """
        if not msg.endswith("\r\n"):
            msg += "\r\n"
        self.socket.sendall(msg.encode(self.format))
        self.addLog(f"Send Command: {msg}\n")
    
    def reciveMsg(self) -> str:
        """
        Receives and returns a message from the Tor control socket. This method is crucial for retrieving responses
        and status updates from the Tor process in response to issued commands.

        :return: The received message from the Tor control socket as a string.
        """
        msg = b""
        while not self.stopEvent.is_set():
            try:
                recv = self.socket.recv(self.raw_len)
            except TimeoutError:
                return None
            if recv:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
            else:
                return None
        msg = msg.decode(self.format)
        self.addLog(f"Recive: {msg}\n")
        return msg
    
    def sendCMD(self, msg: str, silence: bool = False) -> Union[str, bool]:
        """
        Sends a command to the Tor control socket and awaits a response. This method simplifies interaction with
        the control port by encapsulating message sending and response retrieval into a single operation.

        :param msg: The command to be sent to the control socket.
        :param silence: If True, suppresses printing error messages to the console.
        :return: The response from the Tor control socket as a string, or False if an error occurs.
        """
        if not self._isCtrlConn:
            if not silence:
                print("[!!] ERROR: Not connected to Socket Control [!!]")
            return None
        try:
            self.sendMsg(msg)
            recv = self.reciveMsg()
            return recv
        except Exception as e:
            self.addLog(f"[!!] ERROR Send Command: {e} [!!]")
            return f"ERROR: {e}"
    
    def checkTorConn(self) -> bool:
        """
        Verifies the current connection status with the Tor network by querying the bootstrap phase from the
        control socket. It determines whether the Tor process has successfully established a network connection.

        :return: True if the Tor network connection is fully established, False otherwise.
        """
        if not self._isCtrlConn:
            return False
        cmd = self.sendCMD("GETINFO status/bootstrap-phase\r\n", silence=True)
        if not cmd:
            return False
        buff = re.search(r"PROGRESS=(\d+)", cmd)
        if buff:
            progress = buff.group(1)
            if progress == "100":
                return True
        else:
            return False
    
    def _isTorConn(self) -> None:
        """
        A private method that continuously checks for Tor connectivity until a connection is established. It
        is designed to run in a loop, facilitating automatic reconnection attempts or confirmation of initial
        connection success.
        """
        while True:
            sleep(self._pauseLoop)
            if self.checkTorConn():
                print(f"\n[{self.name}] Connected to Tor")
                break
        
    def isTorConn(self) -> None:
        """
        Initiates a background daemon thread to monitor the connection status with the Tor network. This method
        ensures continuous connectivity checks without blocking the main execution flow.
        """
        check = Thread(target=self._isTorConn, daemon=True)
        check.start()
    
    def _newCircuit(self, obtain_ip: bool = False) -> None:
        """
        Internally requests the creation of a new Tor circuit and optionally updates the cached IP address. This
        method is called to renew the Tor connection for a new identity or IP address.

        :param obtain_ip: If True, updates the cached exit node IP address after establishing a new circuit.
        """
        cmd = self.sendCMD("SIGNAL NEWNYM\r\n", silence=True)
        self.onion._ip = None
        while not self.checkTorConn():
            sleep(self._pauseLoop)
        print(f"\n[{self.name}] New Circuit complete.")
        if obtain_ip:
            print(f"\n[{self.name}] New IP Address: {self.onion.IP}")
    
    def newCircuit(self, obtain_ip: bool = False) -> None:
        """
        Starts a background daemon thread to request a new Tor circuit. This allows for non-blocking operation
        and immediate return to the calling process while the circuit renewal is handled in the background.

        :param obtain_ip: If True, indicates that obtaining a new exit node IP address is desired after the circuit is renewed.
        """
        circuit = Thread(target=self._newCircuit, args=(obtain_ip, ), daemon=True)
        circuit.start()
    
    def _work(self) -> None:
        """
        A private method that attempts to establish and maintain a connection to the Tor control socket. It runs
        in a loop, continuously trying to connect until successful, and then enters a state of monitoring Tor connectivity.
        """
        while not self._isCtrlConn:
            self._isCtrlConn = self.socketConnect()
            sleep(self._pauseLoop)
        
    
    def work(self) -> None:
        """
        Starts the main operation of the Farmer class as a daemon thread. This includes establishing a connection
        to the Tor control socket, authenticating, and continuously monitoring the Tor connection status. It serves
        as the primary method for initiating and managing Tor control port interactions.
        """
        work = Thread(target=self._work, daemon=True)
        work.start()
        self.addLog("Farmer Start")
        while not self._isCtrlConn:
            sleep(self._pauseLoop)
        self.isTorConn()