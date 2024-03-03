import socket
import os
import re

from time import sleep
from datetime import datetime
from threading import Thread
from typing import Union



class Farmer:
    """
    Farmer class manages the communication with the Tor control socket to authenticate, 
    send commands, and monitor the status of the Tor connection. It supports operations 
    like checking Tor connectivity, renewing the Tor circuit, and logging messages.
    """
    def __init__(self, config: dict, onion_callback: object):
        """
        Initializes the Farmer with configuration and a reference to the Onion object.

        :param config: Configuration dictionary for Tor and control socket settings.
        :param onion_callback: Reference to the Onion object for callbacks and control.
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
        Adds a log entry to the log file specified in the configuration.

        :param text: The text message to log.
        """
        with open(self.logFile, "a") as f:
            _time = datetime.now()
            f.write(f"{_time.strftime('%d:%m:%Y  %H:%M')} -- {text}\n")
    
    def socketConnect(self) -> bool:
        """
        Attempts to connect to the Tor control socket using the path specified in the config.
        Authenticates with the control socket upon connection.

        :return: True if the connection and authentication are successful, False otherwise.
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
        Sends a message to the Tor control socket.

        :param msg: The message to send to the control socket.
        """
        if not msg.endswith("\r\n"):
            msg += "\r\n"
        self.socket.sendall(msg.encode(self.format))
        self.addLog(f"Send Command: {msg}\n")
    
    def reciveMsg(self) -> str:
        """
        Receives a message from the Tor control socket.

        :return: The received message as a string.
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
        Sends a command to the Tor control socket and returns the response.

        :param msg: The command to send.
        :param silence: If True, suppresses error messages to the console.
        :return: The response from the control socket, or None if not connected.
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
        Checks the Tor connection status by querying the bootstrap phase.

        :return: True if Tor is fully connected (bootstrap phase is 100), False otherwise.
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
        Continuously checks for Tor connectivity in a loop until connected.
        """
        while True:
            sleep(self._pauseLoop)
            if self.checkTorConn():
                print(f"\n[{self.name}] Connected to Tor")
                break
        
    def isTorConn(self) -> None:
        """
        Starts a daemon thread to monitor Tor connectivity.
        """
        check = Thread(target=self._isTorConn, daemon=True)
        check.start()
    
    def _newCircuit(self, obtain_ip: bool = False) -> None:
        """
        Requests a new Tor circuit and clears the cached IP address in the Onion object.
        Waits until Tor connectivity is re-established.
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
        Starts a daemon thread to request a new Tor circuit.
        """
        circuit = Thread(target=self._newCircuit, args=(obtain_ip, ), daemon=True)
        circuit.start()
    
    def _work(self) -> None:
        """
        Attempts to establish a connection to the Tor control socket in a loop until successful.
        """
        while not self._isCtrlConn:
            self._isCtrlConn = self.socketConnect()
            sleep(self._pauseLoop)
        
    
    def work(self) -> None:
        """
        Starts the main daemon thread to manage the Tor control socket connection and monitor Tor connectivity.
        """
        work = Thread(target=self._work, daemon=True)
        work.start()
        self.addLog("Farmer Start")
        while not self._isCtrlConn:
            sleep(self._pauseLoop)
        self.isTorConn()