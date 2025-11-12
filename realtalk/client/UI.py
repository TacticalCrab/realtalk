from threading import Thread
import customtkinter as ctk

from .views.Connection import ConnectionView
from .views.Chat import ChatView

from .Context import UIContext
from .Client import Client

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class UI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.uiContext = UIContext()
        self.client_thread = None
    
        self.title("RealTalk Client")
        self.geometry("400x300")

        self.connection_view = ConnectionView(self, on_submit=self.on_connection_submit)
        self.show_view(self.connection_view)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def show_view(self, view: ctk.CTkFrame):
        for widget in self.winfo_children():
            if widget is view:
                continue
            widget.destroy()

        view.pack(fill="both", expand=True)

    def start(self):
        self.mainloop()
    
    def on_close(self):
        if self.uiContext.client:
            self.uiContext.client.disconnect()

        self.destroy()
        exit(0)

    def init_client(self, name: str, server_ip: str):
        self.uiContext.client = Client(name=name)
        host, port_str = server_ip.split(":")

        self.client_thread = Thread(target=self.uiContext.client.connect, args=(host, int(port_str)))
        self.client_thread.start()
        self.uiContext.client.on("ready", self.on_client_ready)

    def on_connection_submit(self, name: str, server_ip: str):
        self.init_client(name, server_ip)
        self.show_view(ChatView(self, uiContext=self.uiContext))

    def on_client_ready(self):
        self.uiContext.client.on("client_list_updated", self.on_client_list_updated)
        self.uiContext.client.request_client_list()

    def on_client_list_updated(self, client_list):
        print("Client list updated:", client_list)
    
