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

    def __init__(self, headers: dict={}, content: bytes=b"", file: File=None, cookies: dict={}, command: str="", vault: dict={}):
        """
        Initialize the data
        """
        self.headers = headers
        self.content = content
        self.file = file
        self.cookies = cookies
        self.command = command
        self.vault = vault

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
        def add_header(key: str, value) -> bytes:
            return f"{key}:{value}\r\n"

        headers = ""
        headers += add_header("CONTENT_LENGTH", str(self.ContentLength))
        headers += add_header("COMMAND", self.command)

        if self.file:
            if self.file.has_file:
                headers += add_header("FILE_NAME", self.file.filename)
                headers += add_header("FILE_SIZE", str(self.file.Size()))
                headers += add_header("FILE_BOUNDARY", self.file.border)
                headers += add_header("HAS_FILE", "true" if self.file.has_file else "false")


        for key, value in self.headers.items():
            headers += add_header(key, value)

        for key, value in self.cookies.items():
            headers += add_header(f"REMEMBER-{key}", value)

        for key, value in self.vault.items():
            headers += add_header(f"VAULT-{key}", value)

        headers += "\r\n"
        return headers.encode()
    