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
    Represents an individual Tor instance, extending the functionality of threading.Thread. This class
    manages the lifecycle of a Tor process, including its initiation with specific configurations, monitoring
    and logging its activities, and ensuring a graceful shutdown. Additionally, it features tools for exit node
    IP checking and an HTTPBridge, a simple HTTP proxy to SOCKS interface for Tor, enabling each Onion object
    to have its HTTP -> SOCKS_TOR proxy capability.
    """
    def __init__(self, config: dict, stop_event: threading.Event):
        """
        Initializes the Onion object with the necessary configuration and a threading event to signal stopping.
        The configuration includes paths and settings for Tor operation, logging details, and proxy settings.

        :param config: Configuration dictionary for the Tor instance, including paths and proxy settings.
        :param stop_event: A threading.Event object to signal the thread to stop running.
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
        """
        Prepares additional tools for the Tor instance, including IP checking and HTTPBridge setup. The IP
        Checker is initialized based on the local or outbound SOCKS settings, and the HTTPBridge is configured
        if enabled in the configuration. This method establishes the foundational tools necessary for extended
        functionalities beyond the Tor process management.
        """

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
        Creates or appends to a log file at the specified path, marking the start of a new logging session.
        This method is essential for tracking the lifecycle and activities of the Tor process over time.

        :param fpath: Path to the log file to be created or appended.
        """
        with open(fpath, "w") as f:
            _time = datetime.now()
            f.write(f"{_time.strftime('%d:%m:%Y  %H:%M')} - Make Log Files\n")

    def _printLog(self) -> None:
        """
        A private method that continuously monitors and prints the Tor log file's contents to the console.
        This function facilitates real-time monitoring of Tor's operational status and debugging.
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
        Initiates a daemon thread to continuously read and print the Tor process's log output, enabling
        real-time monitoring and logging of Tor activities to the console.
        """
        pl = Thread(target=self._printLog, daemon=True)
        pl.start()
    
    def onionStart(self) -> None:
        """
        Initiates the Tor process using the specified configuration, managing its lifecycle. This includes
        starting Tor with the provided configuration, logging its activities, and optionally starting the
        HTTPBridge if configured. It ensures the Tor process runs as intended and monitors for a stop signal.
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
        Attempts to gracefully terminate the Tor process. If unsuccessful, it forcefully kills the process.
        This method ensures that the Tor instance is correctly shut down, preventing any potential leaks or
        hanging processes.
        """
        try:
            self.procTOR.terminate()
            print(f"\n[!!] Terminate Process: {self.name} [!!]")
        except Exception as e:
            print(f"[!!] ERROR Terminate Process: {e} .... Try kill Process[!!]")
            self.procTOR.kill()
    
    def sendCMD(self, command: str) -> Union[str, bool]:
        """
        Sends a command to the Tor control port and waits for a response. This method allows for dynamic
        interaction with the Tor process, enabling functionalities such as creating new circuits or querying
        status information.

        :param command: The command to be sent to the Tor control port.
        :return: The response from the Tor control port or False if an error occurs.
        """
        return self.Farmer.sendCMD(command)
    
    def newCircuit(self, obtain_ip: bool = False) -> None:
        """
        Requests the creation of a new Tor circuit, optionally checking for a new exit node IP. This method
        can be used to refresh the Tor connection, potentially improving anonymity or bypassing network restrictions.

        :param obtain_ip: If True, checks and updates the exit node IP after establishing the new circuit.
        """
        self.Farmer.newCircuit(obtain_ip)
    
    def status(self) -> str:
        """
        Returns the current status of the Tor instance, such as ready to start, working, or terminated.
        This method provides a quick overview of the Tor process's state, aiding in monitoring and management.
        """
        if not self.is_alive() and not self._start:
            return "ready to start"
        elif self.is_alive():
            return "working"
        else:
            return "terminated"
    
    def infoConf(self) -> None:
        """
        Prints the current configuration and status information of the Tor instance. This method offers a
        convenient way to review the operational parameters and state of the Tor process.
        """
        for k, i in self.conf.items():
            print(f"{str(k):<20}{str(i):<40}")
    
    def info(self) -> str:
        """
        Compiles and returns a summary of the Tor instance's information, including configuration details,
        operational status, and proxy settings. This method facilitates a quick overview of the instance's
        state and settings.
        """
        return f"{self.name:<20}{str(self.localAddr):<25}{str(self.outSocks):<25}{str(self._ip):<20}{str(self.status()):<20}{str(self.isTorConn):<15}{str(self._httpBridge):<20}"
    
    def _getIP(self) -> Union[str, bool]:
        """
        Retrieves the current exit node IP address if the Tor connection is established and operational.
        This method is crucial for verifying the anonymity and operational status of the Tor instance.

        :return: The current exit node IP address or False if not connected or an error occurs.
        """
        if not self.isTorConn:
            self._ip = None
            return None
        if not self._ip:
            self._ip = self._ipChecker.getIP()
            return self._ip
        return self._ip
    
    def stop(self) -> None:
        """
        Signals the Onion thread to stop running, initiating the shutdown process for the Tor instance.
        This method allows for a controlled and graceful termination of the Tor process.
        """
        self.stopEvent.set()
    
    def run(self):
        """
        Overrides the Thread's run method, initiating the Tor process startup, including log file creation,
        starting the Tor process with the configured settings, and managing its lifecycle. This method
        represents the entry point for the Onion thread's execution.
        """
        self.makeLogFile(self.logFile)
        self.makeLogFile(self.logCtrl)
        self.onionStart()
