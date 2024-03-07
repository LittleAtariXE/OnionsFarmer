import socket
import socks
import threading

from threading import Thread
from time import sleep
from typing import Union
from random import randint


class CarouselProxyHttp(Thread):
    def __init__(self, onions_bag: object, proxy_ip_port: str = None):
        super().__init__()
        self.name = "CarouselHTTP"
        self.onions = onions_bag.openBag()
        self.bag = onions_bag
        self._ip_port = proxy_ip_port
        self.stopEvents = [o.stopEvent for o in self.onions]
        self.ip = None
        self.port = None
        self.socksAddr = []
        self.raw_len = self.findConf("RawLen", 1024)
        self.format = self.findConf("FormatCode", "utf-8")
        self._pause_conn = 1
        self._lastUsed = None
        self.specifyIP()
        self.getSocksAddr()
        self.updateBagInfo()
    
    def specifyIP(self) -> None:
        if not self._ip_port:
            self.port = randint(50000, 60000)
            self.ip = "127.0.0.1"
        elif ":" in self._ip_port:
            addr = self._ip_port.split(":")
            self.ip = addr[0]
            self.port = int(addr[1])
        else:
            self.ip = "127.0.0.1"
            self.port = int(self._ip_port)
    
    def getSocksAddr(self) -> None:
        for onion in self.onions:
            loc = onion.conf.get("LocalSocks")
            if loc:
                self.socksAddr.append(("127.0.0.1", int(loc)))
                continue
            out = onion.conf.get("OutSocks")
            if out:
                addr = out.split(":")
                self.socksAddr.append(addr[0], int(addr[1]))
    
    def findConf(self, key: str, default: Union[str, int, bool]) -> Union[str, int, bool]:
        for o in self.onions:
            kfind = o.conf.get(key)
            if kfind:
                return kfind
        return default

    
    def checkStatus(self) -> bool:
        for onion in self.onions:
            if onion.status() == "working":
                continue
            else:
                return False
        return True
    
    def checkStopEvents(self) -> bool:
        for stop in self.stopEvents:
            if stop.is_set():
                return True
        return False
    
    def updateBagInfo(self) -> None:
        for onion in self.onions:
            onion._httpBridge = f"{self.ip}:{self.port}"
        
    
    
    def buildHttpSocket(self) -> bool:
        try:
            self.http = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.http.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.http.bind((self.ip, self.port))
            return True
        except OSError as e:
            print(f"[{self.name}] [!!] ERROR: Build Proxy Socket: {e} [!!]")
            return False
    
    def _acceptConn(self) -> None:
        self.http.settimeout(self._pause_conn)
        while not self.checkStopEvents():
            try:
                conn, addr = self.http.accept()
            except TimeoutError:
                continue
            handler = Thread(target=self.handleReq, args=(conn, ), daemon=True)
            handler.start()
        self.http.close()
        print(f"[{self.name}] Stop Working")
    
    def acceptConn(self) -> bool:
        try:
            self.http.listen()
        except OSError as e:
            print(f"[{self.name}] [!!] ERROR: Server Can not listening: {e} [!!]")
            return False
        ac = Thread(target=self._acceptConn)
        ac.start()
        return True
    
    def prepareProxy(self) -> bool:
        if not self.buildHttpSocket():
            return False
        while not self.checkStatus():
            sleep(self._pause_conn)
        print(f"[{self.name}] Starting...")
        if self.acceptConn():
            return True
        else:
            return False
    
    def reciveMsg(self, conn_object: object, decode: bool = False) -> Union[bytes, str, bool]:
        msg = b""
        while True:
            try:
                recv = conn_object.recv(self.raw_len)
            except (BrokenPipeError, ConnectionAbortedError, ConnectionResetError, OSError) as e:
                print(f"[{self.name}] [!!] ERROR: recive response: {e} [!!]")
                return None
            if recv:
                if len(recv) < self.raw_len:
                    msg += recv
                    break
                else:
                    msg += recv
            else:
                return None
        if decode:
            msg = msg.decode(self.format)
        return msg
    
    def readAddr(self, headers: str) -> Union[str, bool]:
        if headers.startswith("http://"):
            headers = headers[7:]
        else:
            return None
        return headers.rstrip("/")
        
    def handleReq(self, conn: object) -> None:
        resp = self.reciveMsg(conn, True)
        if not resp:
            conn.close()
            return
        headers = resp.split("\r\n")
        print(headers)
        head = headers[0].split(" ")
        method = head[0]
        if len(headers) > 1:
            addr = self.readAddr(head[1])
            if addr:
                socks_resp = self.sendSocksReq(addr, resp)
                if socks_resp:
                    conn.send(socks_resp.encode(self.format))
            else:
                print(f"[{self.name}] Unknown protocol")
        conn.close()
    
    def getSocks(self) -> tuple:
        if self._lastUsed:
            while True:
                sock = randint(0, len(self.socksAddr) - 1)
                if sock == self._lastUsed:
                    continue
                self._lastUsed = self.socksAddr[sock]
                return self.socksAddr[sock]
        sock = randint(0, len(self.socksAddr) - 1)
        self._lastUsed = self.socksAddr[sock]
        return self.socksAddr[sock]

    def sendSocksReq(self, addr: str, msg: str) -> Union[str, bool]:
        try:
            mySocks = socks.socksocket()
            socksAddr = self.getSocks()
            mySocks.set_proxy(socks.PROXY_TYPE_SOCKS5, socksAddr[0], socksAddr[1])
        except Exception as e:
            print(f"[{self.name}] [!!] ERROR: making Socks Proxy: {e} [!!]")
            return None
        try:
            mySocks.connect((addr, 80))
        except Exception as e:
            print(f"[{self.name}] [!!] ERROR: Can not connect: {addr}. error: {e} [!!]")
            return None
        try:
            mySocks.sendall(msg.encode(self.format))
        except Exception as e:
            print(f"[{self.name}] [!!] ERROR: send msg: {e} [!!]")
            return None
        resp = self.reciveMsg(mySocks, True)
        mySocks.close()
        return resp
    
    def run(self) -> None:
        if not self.prepareProxy():
            print(f"\n[{self.name}] [!!] ERROR: Proxy Carousel not working [!!]")
        else:
            print(f"\n[{self.name}] Start Listening: {self.ip}:{self.port}")
    


    

