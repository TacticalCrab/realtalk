from dataclasses import dataclass
import json
from abc import ABC, abstractmethod


class Message(ABC):
    @abstractmethod
    def to_json(self):
        pass

    @staticmethod
    @abstractmethod
    def from_dict(data: dict):
        pass


@dataclass
class IdentificationMessage(Message):
    type = "IDENTIFICATION"
    client_id: str
    name: str

    @staticmethod
    def from_dict(data: dict):
        return IdentificationMessage(
            client_id=data.get("client_id", ""),
            name=data.get("name", "")
        )

    def to_json(self):
        return json.dumps({
            "type": self.type,
            "client_id": self.client_id,
            "name": self.name
        })
    
@dataclass
class IdentificationSuccessMessage(Message):
    type = "IDENTIFICATION_SUCCESS"
    welcome_message: str

    @staticmethod
    def from_dict(data: dict):
        return IdentificationSuccessMessage(
            welcome_message=data.get("welcome_message", "")
        )
    
    def to_json(self):
        return json.dumps({
            "type": self.type,
            "welcome_message": self.welcome_message
        })

@dataclass
class ClientToClientMessage(Message):
    type = "CLIENT_TO_CLIENT"
    sender_id: str
    recipient_id: str
    content: str

    @staticmethod
    def from_dict(data: dict):
        return ClientToClientMessage(
            sender_id=data.get("sender_id", ""),
            recipient_id=data.get("recipient_id", ""),
            content=data.get("content", "")
        )
    
    def to_json(self):
        return json.dumps({
            "type": self.type,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "content": self.content
        })
    
@dataclass
class BroadcastMessage(Message):
    type = "BROADCAST_MESSAGE"
    sender_id: str
    sender_name: str
    content: str

    @staticmethod
    def from_dict(data: dict):
        return BroadcastMessage(
            sender_id=data.get("sender_id", ""),
            sender_name=data.get("sender_name", ""),
            content=data.get("content", "")
        )
    
    def to_json(self):
        return json.dumps({
            "type": self.type,
            "sender_id": self.sender_id,
            "sender_name": self.sender_name,
            "content": self.content
        })


@dataclass
class ClientData:
    id: str
    name: str

    def to_json(self):
        return json.dumps({
            "id": self.id,
            "name": self.name
        })

    @staticmethod
    def from_dict(data: dict):
        return ClientData(
            id=data.get("id", ""),
            name=data.get("name", "")
        )

@dataclass
class RequestClientList(Message):
    type = "REQUEST_CLIENT_LIST"

    @staticmethod
    def from_dict(data: dict):
        return RequestClientList()

    def to_json(self):
        return json.dumps({
            "type": self.type,
        })

@dataclass
class ResponseClientList(Message):
    type = "RESPONSE_CLIENT_LIST"
    clients: list[ClientData]

    @staticmethod
    def from_dict(data: dict):
        clients = [ClientData.from_dict(client) for client in data.get("clients", [])]
        return ResponseClientList(clients=clients)

    def to_json(self):
        return json.dumps({
            "type": self.type,
            "clients": [c.to_json() for c in self.clients]
        })