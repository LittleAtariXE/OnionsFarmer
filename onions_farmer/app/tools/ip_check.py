import socket
import socks
from typing import Union

class IP_Checker:
    def __init__(self, socks_addr: str, conf: dict = {}):
        self.socks_addr = socks_addr
        self.getAddr()
        self.raw_len = conf.get("RawLen", 512)
        self.format = conf.get("FormatCode", "utf-8")
        self.sockTimeout = 3
    
    def getAddr(self) -> None:
        addr = self.socks_addr.split(":")
        self.socksIP = addr[0]
        self.socksPORT = int(addr[1])

    def buildSocket(self) -> bool:
        try:
            self.SOCKS = socks.socksocket()
            self.SOCKS.set_proxy(socks.PROXY_TYPE_SOCKS5, self.socksIP, self.socksPORT)
            return True
        except Exception as e:
            print(f"[!!] ERROR Build SOCKS5 Proxy Socket: {e} [!!]")
            return None
    
    def sendRequest(self, target: str) -> Union[str, bool]:
        try:
            self.SOCKS.connect((target, 80))
        except OSError as e:
            print(f"[!!] ERROR: Cant connect: {target}. Error: {e} [!!]")
            return None
        try:
            req = f"GET / HTTP/1.1\r\nHost: {target}\r\nConnection: close\r\n\r\n".encode(self.format)
            self.SOCKS.sendall(req)
        except Exception as e:
            print(f"[!!] ERROR Send IP request: {e} [!!]")
            return None
        self.SOCKS.settimeout(self.sockTimeout)
        
        resp = b""
        while True:
            try:
                recv = self.SOCKS.recv(self.raw_len)
            except (TimeoutError, BrokenPipeError, ConnectionRefusedError, ConnectionAbortedError):
                print("[!!] ERROR: Timeout Response [!!]")
                return None
            if recv:
                if len(recv) < self.raw_len:
                    resp += recv
                    break
                else:
                    resp += recv
            else:
                return None
        resp = resp.decode(self.format)
        return resp
    
    def _checkIpAmazonaws(self) -> Union[str, bool]:
        _ip = self.sendRequest("checkip.amazonaws.com")
        if not _ip:
            return None
        tmp = _ip.split("\r\n")
        ip = tmp[-1].strip("\n")
        self.SOCKS.close()
        return ip
    
    def _checkIpIpify(self) -> Union[str, bool]:
        _ip = self.sendRequest("api.ipify.org")
        if not _ip:
            return None
        tmp = _ip.split("\r\n")
        ip = tmp[-1].strip("\n")
        self.SOCKS.close()
        return ip

    def getIP(self):
        if not self.buildSocket():
            return None
        ip = self._checkIpIpify()
        if ip:
            return ip
        else:
            ip = self._checkIpAmazonaws()
            if ip:
                return ip
        self.SOCKS.close()
        return None