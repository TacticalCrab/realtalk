from .Client import Client
from dataclasses import dataclass

@dataclass
class UIContext:
    client: Client | None = None