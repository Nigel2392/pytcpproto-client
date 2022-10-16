from ..files import File

class BaseRqResp:
    headers:    dict    = {}
    content:    bytes   = b""
    file:       File    = None
    cookies:    dict    = {}
    command:    str     = ""
    vault:      dict     = {}

    def __dict__(self) -> dict:
        """
        data as dictionary
        """
        return {
            "command": self.command,
            "headers": self.headers,
            "content": self.content,
            "file": dict(self.file),
            "cookies": self.cookies,
            "vault": self.vault
        }

    def __init__(self, **kwargs):
        """
        Initialize the data
        """
        for key, value in kwargs.items():
            if hasattr(self, key.lower()):
                setattr(self, key.lower(), value)

    @property
    def ContentLength(self) -> int:
        """
        data content length
        """
        if self.file:
            if self.file.has_file:
                return len(self.content) + len(self.file.Generate())
        return len(self.content)

    def Generate(self) -> bytes:
        """
        Generate the data
        """
        if self.file:
            if self.file.has_file:
                return self.GenerateHeaders() + self.file.Generate() + self.content
        return self.GenerateHeaders() + self.content

    def GenerateHeaders(self) -> bytes:
        """
        Generate the data headers
        """
        headers = ""
        headers += f"CONTENT_LENGTH:{self.ContentLength}\r\n"
        headers += f"COMMAND:{self.command}\r\n"

        if self.file:
            if self.file.has_file:
                headers += "FILE_NAME:" + self.file.filename + "\r\n"
                headers += "FILE_SIZE:" + str(self.file.Size()) + "\r\n"
                headers += "FILE_BOUNDARY:" + self.file.border + "\r\n"
                headers += "HAS_FILE:" + "true" + "\r\n"

        for key, value in self.headers.items():
            headers += f"{key}: {value}\r\n"

        for key, value in self.cookies.items():
            headers += f"REMEMBER-{key}:{value}\r\n"

        for key, value in self.vault.items():
            headers += f"VAULT-{key}:{value}\r\n"

        headers += "\r\n"
        return headers.encode()
    