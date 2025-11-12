import json
import os
import socket
from threading import Thread

from dataclasses import dataclass
import struct

from ..common.Messages import Message, RequestClientList, IdentificationMessage, ClientToClientMessage, IdentificationSuccessMessage, ResponseClientList, BroadcastMessage

@dataclass
class Client:
    id: str
    name: str
    address: str
    socket: socket.socket

class Server:
    clients: dict[str, Client] = {}

    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server = None
        self.threads: list[Thread] = []
        self.request_handler = RequestHandler(self)

    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        except Exception:
            pass
        self.server.bind((self.host, self.port))
        self.server.listen()

        self.accept_connections()


    def recv_all(self, socket: socket.socket, n: int):
        data = b''
        while len(data) < n:
            print(n - len(data))
            chunk = socket.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data
    
    def send_message(self, socket: socket.socket, message: str):
        message = message.encode('utf-8')
        msg = bytes(message)
        msg_len = struct.pack('>I', len(msg))
        socket.sendall(msg_len + msg)

    def handle_message(self, client_socket: socket.socket) -> str | None:
        raw_len = self.recv_all(client_socket, 4)
        if not raw_len:
            return None
        msg_len = int.from_bytes(raw_len, byteorder='big')
        data = self.recv_all(client_socket, msg_len)

        return data.decode('utf-8')

    def accept_connections(self):
        while True:
            try:
                client_socket, client_address = self.server.accept()
            except KeyboardInterrupt:
                print("Server is shutting down.")
                self.handle_close()
                exit(0)

            thread = Thread(target=self.handle_client, args=(client_socket, client_address), daemon=True)
            thread.start()
            self.threads.append(thread)

    def handle_welcome_message(self, client_socket: socket.socket, client_address) -> Client:
        try:
            message = self.handle_message(client_socket)
            decoded_message = json.loads(message)
            if (decoded_message.get("type") != IdentificationMessage.type):
                print(f"First message from {client_address} is not identification. Closing connection.")
                print("Message content:", message)
                client_socket.close()
                return

            message = IdentificationMessage.from_dict(decoded_message)
            self.clients[message.client_id] = Client(
                id=message.client_id,
                name=message.name,
                address=client_address[0],
                socket=client_socket
            )

            self.send_welcome(self.clients[message.client_id])
        except Exception as e:
            print("Message content:", message)
            print(f"Error processing identification message from {client_address}: {e}")
            print(e.args)
            client_socket.close()
            return

        return self.clients[message.client_id]

    def send_welcome(self, client: Client):
        welcome_message = f"Welcome {client.name}!"
        message = IdentificationSuccessMessage(
            welcome_message=welcome_message
        )
        self.send_message(client.socket, message.to_json())

    def handle_client(self, client_socket: socket.socket, client_address: tuple):
        try:
            print(f"Connection from {client_address} has been established.")

            client = self.handle_welcome_message(client_socket, client_address)

            while True:
                message = self.handle_message(client_socket)
                if message is None:
                    break
                try:
                    decoded_message = json.loads(message)
                    self.request_handler.handle(client, decoded_message)

                except (json.JSONDecodeError, TypeError) as e:
                    print("Message content:", message)  
                    print(f"Error decoding message from {client.address}: {e}")
                    continue
        finally:
            client_socket.close()
            if client and client.id in self.clients:
                del self.clients[client.id]
            print(f"Connection from {client_address} has been closed.")

    def handle_close(self):
        self.server.close()
        for client in self.clients.values():
            client.socket.close()

        for thread in self.threads:
            try:
                thread.join(timeout=1.0)
            except Exception:
                pass

class RequestHandler:
    def __init__(self, server: Server):
        self.server = server

    def handle(self, client: Client, message: dict):
        print(f"Handling message from {client.address}: {message}")
        match message.get("type"):
            case ClientToClientMessage.type:
                message = ClientToClientMessage.from_dict(message)
                recipient = self.server.clients.get(message.recipient_id)
                if recipient:
                    self.send_to_client(recipient, message)

            case RequestClientList.type:
                self.send_response_client_list(client)
            
            case BroadcastMessage.type:
                message = BroadcastMessage.from_dict(message)
                self.broadcastMessage(client, message)

    def broadcastMessage(self, client: Client, message: Message):
        for client in self.server.clients.values():
            self.send_to_client(client, BroadcastMessage.from_dict({
                "sender_id": client.id,
                "sender_name": client.name,
                "content": message.content
            }))

    def send_response_client_list(self, client: Client):
        client_list = [{"id": c.id, "name": c.name} for c in self.server.clients.values()]
        message = ResponseClientList.from_dict({"clients": client_list})
        self.server.send_message(client.socket, message.to_json())
    
    def send_to_client(self, client: Client, message: Message):
        self.server.send_message(client.socket, message.to_json())
