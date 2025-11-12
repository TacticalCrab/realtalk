# from random import randint
# from .Client import Client

# if __name__ == "__main__":
#     client = Client(f"Client_{randint(1000,9999)}")
#     client.connect("localhost", 12345)
#     client.send_request_client_list()


from .UI import UI

if __name__ == "__main__":
    ui = UI()
    ui.start()