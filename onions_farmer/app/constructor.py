import os
import sys
import subprocess

from pathlib import Path
from typing import Union


class TorConstructor:
    """
    The Constructor class is responsible for setting up the necessary directories and configurations
    for running Tor instances. It ensures that Tor is installed, directories for logs, control sockets,
    and configuration files are created, and that the configuration files are correctly prepared.
    """

    def __init__(self, onions_dir_path: str = None):
        """
        Initializes the Constructor class with paths for the main directory, templates, Torrc,
        control sockets, and logs. It also calls the firstStage method to check Tor installation
        and create necessary directories.
        """

        self.__dirName = Path(os.path.dirname(__file__))
        self.dirMainOnions = self.setOnionsDir(onions_dir_path)
        if not self.dirMainOnions:
            sys.exit()
        self.dirCtrlSocket = os.path.join(self.dirMainOnions, "_controls")
        self.dirLogs = os.path.join(self.dirMainOnions, "logs")
        self.dirTorrc = os.path.join(self.dirMainOnions, "config")
        self.dirTorLib = os.path.join(self.dirMainOnions, "lib")
        self.firstStage()

    
    def setOnionsDir(self, onions_dir: Union[bool, str]) -> str:
        if not onions_dir:
            main_dir = self.__dirName.parent.parent
            main_dir = os.path.join(main_dir, "Onions")
        else:
            if not os.path.exists(onions_dir):
                print(f"[!!] TOR Constructor ERROR: Onions dir: {onions_dir} does not exists [!!]")
                return None
            else:
                main_dir = os.path.join(onions_dir, "Onions")
        return main_dir
    
    def makeDir(self) -> bool:
        """
        Creates directories necessary for Tor's operation if they do not already exist.
        Sets permissions for the control socket directory. Returns True if successful,
        False otherwise.
        """
        dirs = [self.dirMainOnions, self.dirCtrlSocket, self.dirLogs, self.dirTorrc, self.dirTorLib]
        for d in dirs:
            if not os.path.exists(d):
                try:
                    os.mkdir(d)
                except OSError as e:
                    print(f"[!!] TOR Construtor ERROR: make {d} dirs : {e} [!!]")
                    return False
        
        # Set permissions for control socket directory
        try:
            out = subprocess.run(["chmod", "750", self.dirCtrlSocket], capture_output=True, check=True, text=True)
            if out.returncode == 0:
                print("Prepare Dir Successfull")
            else:
                print(f"[!!] ERROR: {out.stderr} [!!]")
                return False
        except Exception as e:
            print(f"[!!] ERROR: {e} [!!]")
            return False
        return True
    
    def isTorInstalled(self) -> bool:
        """
        Checks if Tor is installed by attempting to get its version. Returns True if Tor
        is found, False otherwise.
        """
        try:
            out = subprocess.run(["tor", "--version"], capture_output=True, check=True, text=True)
            print("Good. Tor is installed")
            print(out.stdout)
            return True
        except FileNotFoundError:
            print("[!!] ERROR: Tor is not installed. Please install Tor [!!]")
        except Exception as e:
            print(f"[!!] ERROR: {e} [!!]")
        return False
    
    def firstStage(self) -> None:
        """
        The first stage in setting up the environment for Tor. Checks if Tor is installed
        and necessary directories are made. Exits the program if either check fails.
        """
        if  not self.isTorInstalled() or not self.makeDir():
            print("[!!] EXIT PROGRAM [!!]")
            sys.exit()
    
    def makeFile(self, target: str, data: str = None) -> bool:
        try:
            with open(target, "w") as f:
                if data:
                    f.write(data)
                else:
                    f.write("")
            return True
        except Exception as e:
            print(f"[!!] TOR Construtor ERROR: make file: {target}. error: {e} [!!]")
            return False
    
    def loadFile(self, target: str) -> Union[bool, str]:
        if not os.path.exists(target):
            print(f"[!!] TOR Constructor ERROR: file: {target} does not exist [!!]")
            return None
        with open(target, "r") as f:
            data = f.read() + "\n"
        return data
    
    def choseTorrc(self, conf: dict) -> str:
        torrc = conf.get("Torrc")
        if not torrc:
            return "## CUSTOM TORRC FILE\n\n"
        match torrc:
            case "default":
                tor_data = self.loadFile("/etc/tor/torrc")
            case _:
                tor_data = self.loadFile(torrc)
        if not tor_data:
            return "## CUSTOM TORRC FILE\n\n"
        else:
            return tor_data
    
    def prepareConf(self, conf: dict, part=False) -> str:
        if part:
            buff = ""
        else:
            buff = f"\n## Custom Config: {conf['Name']}\n"
            buff += f"\n##Control Socket:\nControlSocket {conf['CtrlSocketPath']} GroupWritable RelaxDirModeCheck\nControlSocketsGroupWritable 1\n"
            buff += f"\n## Send all messages of level 'notice' or higher\nLog notice file {conf['LogFile']}\n"
            buff += f"\n##TOR data in 'lib' directory\nDataDirectory {conf['DirLib']}\n"
        for k, i in conf.items():
            match k:
                case "LocalSocks":
                    if i:
                        buff += f"\n## Local Proxy addr: 127.0.0.1:{i}\nSocksPort {i}\n"
                case "OutSocks":
                    if i:
                        buff += f"\n## Outside Proxy addr: {i}\nSocksPort {i}\n"
                case "DebugLog":
                    if i:
                        buff += f"\n## Send every possible message\nLog debug file {i}\n"
        return buff

        
    def makeConfig(self, conf: dict) -> Union[dict, bool]:
        """
        Prepares and writes the Tor configuration file based on the provided 'config' dictionary.
        Returns a dictionary with paths and configuration details necessary to start Tor, or None
        if an error occurs during the process.
        """

        name = conf["Name"]
        if not conf.get("LocalSocks") and not conf.get("OutSocks"):
            conf["LocalSocks"] = "9050"
        if conf.get("LocalSocks"):
            conf["LocalAddr"] = f"127.0.0.1:{conf['LocalSocks']}"
        conf["CtrlSocketPath"] = os.path.join(self.dirCtrlSocket, name)
        conf["LogFile"] = os.path.join(self.dirLogs, f"{name}_logs.txt")
        conf["LogSocketFile"] = os.path.join(self.dirLogs, f"{name}_control_log.txt")
        if conf.get("DebugLog"):
            conf["DebugLog"] = os.path.join(self.dirLogs, f"{name}_debug.txt")
        conf["DirLib"] = os.path.join(self.dirTorLib, name)
        if not os.path.exists(conf["DirLib"]):
            try:
                os.mkdir(conf["DirLib"])
            except OSError as e:
                print(f"[!!] TOR Constructor ERROR: make Tor lib directory: {e} [!!]")
                return None
        try:
            check = subprocess.run(["chmod", "g+s,g-x", conf["DirLib"]], capture_output=True, check=True, text=True)
            if check.returncode != 0:
                print(f"[!!] TOR Constructor ERROR: chmod Lib Dir: {check.stderr} [!!]")
                return None
        except Exception as e:
            print(f"[!!] TOR Construtcor ERROR: {e} [!!]")
            return None

        temp = self.choseTorrc(conf)
        tor_conf = temp + self.prepareConf(conf)
        conf["Torrc"] = os.path.join(self.dirTorrc, name)
        if self.makeFile(conf["Torrc"], tor_conf):
            return conf
        else:
            return None

