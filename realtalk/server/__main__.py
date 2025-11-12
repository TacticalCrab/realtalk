import os

from .Server import Server

if __name__ == "__main__":
    #Python process
    print(os.getpid())

    server = Server("localhost", 12345)
    print("Starting server...")
    server.start()