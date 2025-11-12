from ..Context import UIContext
import customtkinter as ctk

class ChatView(ctk.CTkFrame):
    def __init__(self, master=None, uiContext: UIContext = None):
        super().__init__(master)
        master.geometry("600x500")
        self.uiContext = uiContext
        self.build_ui()

    def build_ui(self):
        self.name_label = ctk.CTkLabel(self, text=f"Chat View - User: {self.uiContext.client.name}")
        self.name_label.pack(pady=20)

        self.chat_messages = ctk.CTkTextbox(self, width=300, height=200)
        self.chat_messages.pack(pady=10)

        self.message_entry = ctk.CTkEntry(self, placeholder_text="Type your message here...")
        self.message_entry.pack(pady=10)
        self.send_button = ctk.CTkButton(self, text="Send", command=self.send_message)
        self.send_button.pack(pady=10)

        self.uiContext.client.on("message_received", self.on_message_received)

    def send_message(self):
        self.uiContext.client.send_chat_message(self.message_entry.get())
        self.message_entry.delete(0, ctk.END)
    
    def on_message_received(self, message):
        self.chat_messages.insert(ctk.END, f"{message.sender_name}: {message.content}\n")
        self.chat_messages.see(ctk.END)
        