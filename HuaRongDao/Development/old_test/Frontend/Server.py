import time
import zmq
import threading
import queue

class ZmqFrontendServer(threading.Thread):
    _port = 27132
    clients_addr = set()

    def __init__(self, server_port: int = None):
        threading.Thread.__init__(self)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.ROUTER)
        self.bindedClient = None
        self._receivedMessage: str = None
        self._messageTimeStamp: int = None
        self._sentTimeStamp: int = None
        self.msgQueue: queue.Queue = queue.Queue()

        if server_port is not None:
            self.port = server_port

        print(f"[FrontendServer] Hosting at port: {self._port}")
        self.t = threading.Thread(target=self.listen_queue)
        self.t.start()
        self.start()

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value: int):
        if value < 0 or value > 65535:
            raise ValueError("port must be between 0 and 65535!")
        self._port = value

    @property
    def messageTimeStamp(self) -> int:
        return -1 if self._messageTimeStamp is None else self._messageTimeStamp

    @messageTimeStamp.setter
    def messageTimeStamp(self, value: int):
        self._messageTimeStamp = value

    @property
    def receivedMessage(self) -> str:
        return "" if self._receivedMessage is None else self._receivedMessage

    @receivedMessage.setter
    def receivedMessage(self, value: str):
        self._receivedMessage = value

    @property
    def sentTimeStamp(self) -> int:
        return -1 if self._sentTimeStamp is None else self._sentTimeStamp

    @sentTimeStamp.setter
    def sentTimeStamp(self, value: int):
        self._sentTimeStamp = value

    def run(self):
        self.hosting()

    def hosting(self):
        self.socket.bind(f"tcp://127.0.0.1:{self.port}")
        while True:
            [address, contents] = self.socket.recv_multipart()
            address_str = address.decode()
            contents_str = contents.decode()
            self.clients_addr.add(address_str)
            self.messageTimeStamp = int(round(time.time() * 1000))
            self.receivedMessage = contents_str
            print(f"[FrontendServer] <- {address_str}: {contents_str}")

            if self.bindedClient is None:
                self.bindedClient = address_str

    def listen_queue(self):
        while True:
            if (not self.msgQueue.empty() and
                (int(round(time.time() * 1000)) - self.sentTimeStamp > 100)):
                self.sentTimeStamp = int(round(time.time() * 1000))
                self.__send_string(self.bindedClient, self.msgQueue.get())

    def send_string(self, msg: str):
        self.msgQueue.put(msg)

    def __send_string(self, address: str, msg: str):
        if not self.socket.closed:
            print(f"[FrontendServer] -> {address}: {msg}")
            self.socket.send_multipart([address.encode(), msg.encode()])
        else:
            print("[FrontendServer] Socket is closed, can't send message...")