import os
import sys
import subprocess

from pathlib import Path
from typing import Union


class TorConstructor:
    """
    The TorConstructor class is responsible for initializing the environment necessary for running
    multiple Tor instances. It ensures the presence of Tor, creates directories for logs, control sockets,
    and configuration files, and prepares configuration files accordingly. This class is a foundational
    component for managing Tor instances in a scalable and organized manner. Requires Tor to be installed
    and Python version 3.11 or newer.
    """

    def __init__(self, onions_dir_path: str = None):
        """
        Initializes the TorConstructor class with optional paths for the main directory. If no path is provided,
        it defaults to a directory named "Onions" in the parent directory of the script's location. This method
        initializes directory paths for main operations, control sockets, logs, configuration files, and Tor's
        library files. It also triggers the first stage of setup, which includes checking for Tor's installation
        and the creation of necessary directories.

        :param onions_dir_path: Optional. The path to the main directory where the Tor instances will be managed.
                                If not provided, a default path is used.
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
        """
        Determines the main directory for Tor instances. If no custom path is provided, it defaults to a directory
        named "Onions" in the grandparent directory of the script's location. If a custom path is provided but does
        not exist, an error message is displayed, and None is returned.

        :param onions_dir: The custom path for the main directory or False if no path is provided.
        :return: The path to the main directory as a string.
        """
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
        Creates the necessary directories for Tor operation if they do not already exist. This includes directories
        for main operations, control sockets, logs, configuration files, and library files. Also sets specific
        permissions for the control socket directory to enhance security.

        :return: True if all directories were successfully created and false otherwise.
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
        Verifies if Tor is installed by attempting to run the 'tor --version' command. It provides a clear indication
        if Tor is correctly installed on the system and accessible from the command line.

        :return: True if Tor is installed, False otherwise.
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
        Executes the initial setup phase, which includes checking for Tor's installation and creating necessary
        directories. If either check fails, the program prints an error message and exits to prevent further execution.

        :return: None
        """
        if  not self.isTorInstalled() or not self.makeDir():
            print("[!!] EXIT PROGRAM [!!]")
            sys.exit()
    
    def makeFile(self, target: str, data: str = None) -> bool:
        """
        Creates or overwrites a file at the specified target path with the provided data. If no data is provided,
        it creates an empty file. This method is primarily used for generating configuration files.

        :param target: The file path where the file should be created or overwritten.
        :param data: The content to be written into the file. If None, an empty file is created.
        :return: True if the file was successfully created or overwritten, False if an error occurred.
        """

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
        """
        Reads and returns the content of a file specified by the target path. If the file does not exist,
        it prints an error message and returns None.

        :param target: The file path of the file to be read.
        :return: The content of the file as a string if successful, None otherwise.
        """
        if not os.path.exists(target):
            print(f"[!!] TOR Constructor ERROR: file: {target} does not exist [!!]")
            return None
        with open(target, "r") as f:
            data = f.read() + "\n"
        return data
    
    def choseTorrc(self, conf: dict) -> str:
        """
        Selects a Tor configuration file (torrc) based on the provided configuration dictionary. If a specific
        torrc path is provided in the configuration, it attempts to load it; otherwise, it defaults to a
        custom torrc template.

        :param conf: A dictionary containing the configuration details.
        :return: The content of the chosen torrc file as a string.
        """

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
        """
        Prepares the Tor configuration content based on the provided dictionary. It can generate a full configuration
        or just a part of it, depending on the 'part' parameter. This method handles various configuration options
        such as local and outside socks ports, debug logging, etc.

        :param conf: A dictionary containing key configuration parameters.
        :param part: Boolean indicating whether to generate a partial or full configuration.
        :return: The prepared configuration content as a string.
        """

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
        Generates the complete Tor configuration file based on the provided 'config' dictionary and writes it
        to the filesystem. It also handles directory creation and permission setting for Tor's data directory.
        Returns a dictionary with paths and configuration details necessary to start Tor if successful, or None
        if an error occurs during the process.

        :param conf: A dictionary containing the configuration details for a Tor instance.
        :return: A dictionary with configuration details and paths if successful, None otherwise.
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

