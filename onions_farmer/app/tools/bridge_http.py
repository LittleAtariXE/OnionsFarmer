import socket
import socks
import threading

from threading import Thread
from time import sleep
from typing import Union
from random import randint


class BridgeHTTP(Thread):
    def __init__(self, onion: object, proxy_ip_port: str = None):
        super().__init__()
        self.cfg = onion.conf
        self.name = f"HTTP_{self.cfg['Name']}"
        self.stopEvent = onion.stopEvent
        self._proxy = proxy_ip_port
        self.raw_len = self.cfg.get("RawLen", 1024)
        self.format = self.cfg.get("FormatCode", "utf-8")
        self.pause_conn = 1
        self.ip = None
        self.port = None
        self.socksIP = None
        self.socksPORT = None
        self.specifyIP()
        self.specifySocks()

    def specifyIP(self) -> None:
        if not self._proxy:
            self.ip = "127.0.0.1"
            self.port = randint(30000, 40000)
        else:
            if ":" in self._proxy:
                addr = self._proxy.split(":")
                self.ip = addr[0]
                try:
                    self.port = int(addr[1])
                except (ValueError, TypeError):
                    print(f"[{self.name}] [!!] ERROR: BridgeHTTP proxy port error: {addr[1]} ... use random port number [!!]")
                    self.port = randint(30000, 40000)
            else:
                self.ip = "127.0.0.1"
                self.port = int(self._proxy)
    
    def specifySocks(self) -> None:
        if self.cfg.get("LocalSocks"):
            self.socksPORT = self.cfg.get("LocalSocks")
            self.socksIP = self.ip
        elif self.cfg.get("OutSocks"):
            addr = self.cfg["OutSocks"].split(":")
            self.socksIP = addr[0]
            self.socksPORT = addr[1]


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
        self.http.settimeout(self.pause_conn)
        while not self.stopEvent.is_set():
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
    
    def sendSocksReq(self, addr: str, msg: str) -> Union[str, bool]:
        try:
            mySocks = socks.socksocket()
            mySocks.set_proxy(socks.PROXY_TYPE_SOCKS5, self.socksIP, int(self.socksPORT))
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
        print("SOCKS RESP: ", resp)
        return resp
    
    def constructor(self) -> bool:
        if not self.ip or not self.socksIP:
            return False
        if not self.buildHttpSocket():
            return False
        return True
    
    def run(self) -> None:
        if not self.constructor():
            return
        if not self.acceptConn():
            return
        print(f"[{self.name}] Start Listening: {self.ip}:{self.port}")