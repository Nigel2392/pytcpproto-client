import os

class BaseFile:
    """Represents a file object sent over the network via the tcpproto protocol."""
    filename = ""
    data = b""
    border = ""
    has_file = False

    def __init__(self, filename: str=None, data: bytes=None, border: str=None):
        self.filename = filename
        self.data = data
        if self.filename and not border:
            self.border = self.generate_border()
        else:
            self.border = border
        if self.filename and self.border and self.data:
            self.has_file = True

    def __repr__(self) -> str:
        """
        File representation
        """
        return f"{self.__class__.__name__}(filename={self.filename}, border={self.border}, data={not not self.data}, has_file={self.has_file})"

    def __dict__(self) -> dict:
        """
        File as dictionary
        """
        return {
            "filename": self.filename,
            "border": self.border,
            "data": self.data,
            "has_file": self.has_file
        }

    def generate(self) -> bytes:
        """
        File content -> prepend to the request content
        """
        return self.starting_border + self.data + self.ending_border

    def generate_border(self) -> bytes:
        """
        Generate the file border
        """
        return bytes("FILE_BORDER-" + self.filename + "-FILE_BORDER")

    def size(self) -> int:
        """
        File size
        """
        return len(self.data)

    @property
    def starting_border(self) -> bytes:
        """
        File starting border
        """
        return b"--" + self.border.encode() + b"--"
    
    @property
    def ending_border(self) -> bytes:
        """
        File ending border
        """
        return b"----" + self.border.encode() + b"----"

    def read(self, path: str):
        """
        Read the file from a path
        """
        if "/" in path:
            delim = "/"
        else:
            delim = "\\"
        with open(path, "rb") as file:
            self.data = file.read()
        file.close()
        self.filename = path.split(delim)[-1]
        self.has_file = True
        self.border = self.generate_border()
        return self
    
    def write(self, path: str):
        """
        Write the file to a path
        """
        path = os.path.join(path, self.filename)
        with open(path, "wb") as file:
            file.write(self.data)
        file.close()
