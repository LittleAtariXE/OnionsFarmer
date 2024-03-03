import socket
import os
import subprocess
import threading

from threading import Thread
from time import sleep
from datetime import datetime
from typing import Union

from .farmer import Farmer
from .tools.ip_check import IP_Checker
from .tools.bridge_http import BridgeHTTP


class Onion(Thread):
    """
    The Onion class extends threading.Thread and is responsible for managing the lifecycle
    of a Tor process. This includes starting Tor with a specific configuration, logging its output,
    and gracefully shutting it down upon request.
    """
    def __init__(self, config: dict, stop_event: threading.Event):
        """
        Initializes the Onion thread with a given configuration and a stop event.

        :param config: A dictionary containing configuration options for the Tor process and logging.
        :param stop_event: A threading.Event() object used to signal the thread to stop running.
        """
        super().__init__()
        self.stopEvent = stop_event
        self._start = False
        self._config = config
        self.name = config["Name"]
        self.torrc = config["Torrc"]
        self.logFile = config["LogFile"]
        self.logCtrl = config["LogSocketFile"]
        self.ctrlSocketPath = config["CtrlSocketPath"]
        self.localSocks = config.get("LocalSocks")
        self.localAddr = config.get("LocalAddr")
        self.outSocks = config.get("OutSocks")
        self.prints = config.get("PrintLog", False)
        self.procPID = None
        self.procTOR = None
        self.procPAUSE = config.get("ProcPause", 1)
        self._ip = None
        self._httpBridge = None
        self._httpBridgeFLAG = False
        self.httpBridge = None
        self.Farmer = Farmer(self._config, self)
        self.preapreTools()
        
        
    
    @property
    def conf(self) -> dict:
        conf = {
            "Name" : self.name,
            "Torrc" : self.torrc,
            "LogFile" : self.logFile,
            "LogSocketFile" : self.logCtrl,
            "CtrlSocketPath" : self.ctrlSocketPath,
            "DirLib" : self._config["DirLib"],
            "LocalSocks" : self.localSocks,
            "LocalAddr" : self.localAddr,
            "OutSocks" : self.outSocks,
            "PID_Proc" : self.procPID,
            "ProcPause" : self.procPAUSE,
            "PrintLog" :self.prints,
            "Status" : self.status(),
            "IsTorConn" : self.isTorConn,
            "ExitNodeIP" : self._ip,
            "HttpBridge" : self._httpBridge
        }
        return conf
    
    @property
    def isTorConn(self) -> bool:
        return self.Farmer.checkTorConn()
    
    @property
    def IP(self) -> Union[str, bool]:
        return self._getIP()
    
    def preapreTools(self) -> None:
        if not self.localAddr and self.outSocks:
            self._ipChecker = IP_Checker(self.outSocks)
        else:
            self._ipChecker = IP_Checker(self.localAddr)
        if self._config.get("HttpBridge"):
            self._httpBridgeFLAG = True
            if self._config.get("HttpBridge") == "random":
                self.httpBridge = BridgeHTTP(self)
            else:
                self.httpBridge = BridgeHTTP(self, self._config["HttpBridge"])
            self._httpBridge = f"{self.httpBridge.ip}:{self.httpBridge.port}"

        
    
    def makeLogFile(self, fpath: str) -> None:
        """
        Creates or appends a header to a log file indicating the start of a new log section.

        :param fpath: The file path to the log file.
        """
        with open(fpath, "w") as f:
            _time = datetime.now()
            f.write(f"{_time.strftime('%d:%m:%Y  %H:%M')} - Make Log Files\n")

    def _printLog(self) -> None:
        """
        Continuously reads and prints the Tor log file to the console.
        """
        try:
            with open(self.logFile, "r") as f:
                # move index to end file
                f.seek(0, 2)
                while True:
                    line = f.readline()
                    if not line:
                        sleep(0.1)
                        continue
                    else:
                        print(line, end="")
        except Exception as e:
            print(f"[!!] ERROR Reading Log File: {e} [!!]")
            return
    
    def printLog(self) -> None:
        """
        Starts a daemon thread to continuously print the Tor process's log output.
        """
        pl = Thread(target=self._printLog, daemon=True)
        pl.start()
    
    def onionStart(self) -> None:
        """
        Starts the Tor process using the specified configuration and manages its lifecycle.
        """
        self.stopEvent.clear()
        command = ["tor", "-f", self.torrc]
        self._start = True
        try:
            self.procTOR = subprocess.Popen(command, stdout=subprocess.PIPE, text=True)
            self.procPID = self.procTOR.pid
            print(f"Tor Starting from: {self.name} config file. Check log files: {self.logFile}")
            self.Farmer.work()
            if self.prints:
                self.printLog()
            if self._httpBridgeFLAG:
                self.httpBridge.start()
            while not self.stopEvent.is_set():
                sleep(self.procPAUSE)
        except Exception as e:
            print(f"\n[!!] ERROR Start Tor: {e} [!!]")
            return
        finally:
            self.terminateTorProcess()
    
    def terminateTorProcess(self) -> None:
        """
        Attempts to gracefully terminate the Tor process. If unsuccessful, tries to kill the process.
        """
        try:
            self.procTOR.terminate()
            print(f"\n[!!] Terminate Process: {self.name} [!!]")
        except Exception as e:
            print(f"[!!] ERROR Terminate Process: {e} .... Try kill Process[!!]")
            self.procTOR.kill()
    
    def sendCMD(self, command: str) -> Union[str, bool]:
        """
        Sends a command, wait and returns a response
        All available commands are described in the Tor documentation:
        https://spec.torproject.org/control-spec/commands.html

        return: STR contains response from Socket Control Port
        """
        return self.Farmer.sendCMD(command)
    
    def newCircuit(self, obtain_ip: bool = False) -> None:
        """
        Creates a separate thread to make a new circuit 
        """
        self.Farmer.newCircuit(obtain_ip)
    
    def status(self) -> str:
        if not self.is_alive() and not self._start:
            return "ready to start"
        elif self.is_alive():
            return "working"
        else:
            return "terminated"
    
    def infoConf(self) -> None:
        for k, i in self.conf.items():
            print(f"{str(k):<20}{str(i):<40}")
    
    def info(self) -> str:
        return f"{self.name:<20}{str(self.localAddr):<25}{str(self.outSocks):<25}{str(self._ip):<20}{str(self.status()):<20}{str(self.isTorConn):<15}{str(self._httpBridge):<20}"
    
    
    
    def _getIP(self) -> Union[str, bool]:
        if not self.isTorConn:
            self._ip = None
            return None
        if not self._ip:
            self._ip = self._ipChecker.getIP()
            return self._ip
        return self._ip
    
    def stop(self) -> None:
        self.stopEvent.set()
    
    def run(self):
        self.makeLogFile(self.logFile)
        self.makeLogFile(self.logCtrl)
        self.onionStart()
