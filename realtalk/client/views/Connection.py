import customtkinter as ctk
from typing import Callable
from random import randint

class ConnectionView(ctk.CTkFrame):
    def __init__(self, master=None, on_submit: Callable[[str, str], None] =None):
        super().__init__(master)

        self.on_submit = on_submit

        self.label = ctk.CTkLabel(self, text="Connection View")
        self.label.pack(pady=20)

        self.name_entry = ctk.CTkEntry(self, placeholder_text="Enter your name")
        self.name_entry.pack(pady=10)
        self.name_entry.insert(0, f"User_{randint(1000,9999)}")

        self.ip_entry = ctk.CTkEntry(self, placeholder_text="Enter server IP:PORT")
        self.ip_entry.pack(pady=10)
        self.ip_entry.insert(0, "localhost:12345")

        self.connect_button = ctk.CTkButton(self, text="Connect", command=self.connect)
        self.connect_button.pack(pady=20)
    
    def connect(self):
        print(f"Connecting as {self.name_entry.get()} to {self.ip_entry.get()}")

        if callable(self.on_submit):
            self.on_submit(self.name_entry.get(), self.ip_entry.get())

