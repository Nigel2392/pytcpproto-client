# Imports needed for the client.
import base64
import socket
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import (
    hashes,
    serialization 
)
from cryptography.hazmat.primitives.asymmetric import padding
import os
# Client imports
from .request import Request
from .response import Response
from .files import File
from .logger import Logger
from .parsers import parse_header,parse_file

"""
    Client module to connect to the server with.
"""

class Client():
    cookies: dict = {}
    vault: dict = {}
    client_vault: dict = {}

    def __init__(self, host: str, port: int, rsa_file: str="PUBKEY.pem", buffer_size: int=2048):
        """
        Initialize the client

        Private key is not required. 
        If it is not provided, you will not be able to encrypt (client.Lock()) data client-side.
        """
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        self.buffer_size = buffer_size
        try:
            os.chdir(os.path.dirname(os.path.abspath(__file__)))
            with open(".\\"+ rsa_file, "rb") as f:
                fdata = f.read()
                self.rsa_key = serialization.load_pem_public_key(fdata, backend=default_backend())
        except:
            pass

    def __dict__(self) -> dict:
        """
        Client as dictionary
        """
        return {
            "host": self.host,
            "port": self.port,
            "cookies": self.cookies,
            "vault": self.vault
        }

    def send(self, request: Request) -> Response:
        """
        Send a request to the server. 
        The server will return a response.
        """
        request.vault = self.vault
        request.cookies = self.cookies
        if hasattr(self, "rsa_key"):
            for key, value in self.client_vault.items():
                # Encrypt the client vault
                value = self.rsa_key.encrypt(value.encode(), 
                    padding.OAEP(
                        # Server uses sha512 to hash the key
                        mgf=padding.MGF1(algorithm=hashes.SHA512()), 
                        algorithm=hashes.SHA512(), 
                        label=None
                    )
                )
                # Encode the encrypted data to base64
                value = base64.b64encode(value)
                request.headers["CLIENT_VAULT-"+key] = value.decode()
        # Reset the client vault
        self.client_vault = {}
        # Send the request
        self.sock.send(request.generate())
        resp = self.receive()
        return resp

    def Close(self):
        """
        Close the connection
        """
        self.sock.close()

    def receive(self) -> Response:
        """
        Receive a response from the server
        """
        headers, content = self.rcv_header()
        content_length = int(headers["CONTENT_LENGTH"])
        content += self.rcv_content(content_length, content)

        resp = Response()
        file, content = parse_file(headers, content)
        if file:
            resp.file = file

        resp.headers = headers
        resp.content = content
        resp.cookies = self.cookies
        resp.vault = self.vault
        return resp


    def rcv_header(self, data: bytes=b""):
        """
        :param data: The data that has been received so far
        :return: [dict, bytes] Headers, content 
        """
        chunk = self.sock.recv(self.buffer_size)
        data += chunk
        if b"\r\n\r\n" in data:
            headers, content = parse_header(data)
            keys = list(headers.keys())
            for key in keys:
                if key.startswith("REMEMBER-"):
                    self.cookies[key[9:]] = headers[key]
                    del headers[key]
                elif key.startswith("VAULT-"):
                    self.vault[key[6:]] = headers[key]
                    del headers[key]
                elif key.startswith("CLIENT_VAULT-"):
                    self.client_vault[key[13:]] = headers[key]
                    del headers[key]
                elif key.startswith("FORGET-"):
                    del self.cookies[headers[key]]
                    del self.vault[headers[key]]
                    del headers[key]
            return headers, content
        else:
            return self.rcv_header(data)

    def rcv_content(self, content_length: int, data: bytes=b"") -> bytes:
        while len(data) < content_length:
            data += self.sock.recv(self.buffer_size)
        return data[content_length:]

    def Lock(self, key, value):
        self.client_vault[key] = value


if __name__ == "__main__":
    file = File(filename="test.txt", data=b"Hello World!", border="FILE_BOUDNAKSFDJBADFS")
    request = Request(file=file, content=b"sdfsdf Worfsdfsdfsdfld!", command="SET")
    request.headers["Content-Type"] = "text/plain"
    client = Client("127.0.0.1", 22392, "PUBKEY.pem", 4096)
    resp = client.send(request)
    logger = Logger("debug")
    logger.Test("Response 1:")
    print(resp.headers)
    print(resp.cookies)
    print(resp.vault)
    print(resp.content)
    request = Request(content=b"Hello world!", command="GET")
    response = client.send(request)
    logger.Test("Response 2:")
    print(response.headers)
    print(response.cookies)
    print(response.vault)
    print(response.content)
    def WillExcept():
        dict = {}
        dict["test"] = "test"
        key = dict["test2"]

    data, ok = logger.Except(WillExcept, [Exception])
    if ok:
        print("No error")
    else:
        print("Error")
        print(data)




