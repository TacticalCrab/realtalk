import socket
import struct
from threading import Thread, Event
import json

from ..common.Messages import IdentificationMessage, RequestClientList, ResponseClientList, IdentificationSuccessMessage, BroadcastMessage

class EventEmitter:
    def __init__(self):
        self.events = {}

    def on(self, event_name: str, listener):
        if event_name not in self.events:
            self.events[event_name] = []
        self.events[event_name].append(listener)

    def emit(self, event_name: str, *args, **kwargs):
        if event_name in self.events:
            for listener in self.events[event_name]:
                listener(*args, **kwargs)

class Client(EventEmitter):
    def __init__(self, name: str):
        super().__init__()
        self.id = abs(hash(name))
        self.name = name
        self.thread_stop_event = Event()

    def connect(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((host, port))
        self.client.settimeout(2.0)
        print(f"Connected to server at {host}:{port}")

        self.messages_thread = Thread(target=self.__handle_messages)
        self.messages_thread.start()
        self.__send_identification()
    
    def disconnect(self):
        self.client.close()
        self.thread_stop_event.set()
        self.messages_thread.join()

        print("Disconnected from server")

    def __emit_ready(self):
        self.emit("ready")

    def __send_identification(self):
        message = IdentificationMessage(
            client_id=self.id,
            name=self.name
        )
        self.__send_message(message.to_json())

    def __recv_all(self,  n: int):
        data = b''
        while len(data) < n and not self.thread_stop_event.is_set():
            try:
                chunk = self.client.recv(n - len(data))
            except socket.timeout:
                continue

            if not chunk:
                raise ConnectionError("Connection closed")
            data += chunk
        return data

    def __handle_message(self) -> str | None:
        raw_len = self.__recv_all(4)
        if not raw_len:
            return None
        msg_len = int.from_bytes(raw_len, byteorder='big')
        data = self.__recv_all(msg_len)

        return data.decode('utf-8')

    def __handle_messages(self):
        while not self.thread_stop_event.is_set():
            message = self.__handle_message()

            if message is None:
                print("Connection closed by server")
                return

            message_data = json.loads(message)
            match message_data.get("type"):
                case IdentificationSuccessMessage.type:
                    self.__emit_ready()

                case ResponseClientList.type:
                    clientList: ResponseClientList["clients"] = message_data.get("clients", [])
                    self.emit("client_list_updated", clientList)
                case BroadcastMessage.type:
                    message = BroadcastMessage.from_dict(message_data)
                    self.emit("message_received", message)

            print(f"Received message: {message}")

    def __send_message(self, message: str):
        message = message.encode('utf-8')
        msg = bytes(message)
        msg_len = struct.pack('>I', len(msg))
        self.client.sendall(msg_len + msg)

    def send_chat_message(self, content: str):
        message = BroadcastMessage(
            sender_id=str(self.id),
            sender_name="",
            content=content
        )
        self.__send_message(message.to_json())

    def request_client_list(self):
        message = RequestClientList()
        self.__send_message(message.to_json())


    