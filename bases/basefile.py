import os

class BaseFile:
    """Represents a file object sent over the network via the tcpproto protocol."""
    filename = ""
    data = b""
    border = ""
    has_file = False

    def __init__(self, filename: str=None, data: bytes=None, border: str="FILE_BORDER-FILE_BORDER"):
        self.filename = filename
        self.data = data
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

    def Generate(self) -> bytes:
        """
        File content -> prepend to the request content
        """
        return self.starting_border + self.data + self.ending_border

    def Generate_Border(self) -> bytes:
        """
        Generate the file border
        """
        return "FILE_BORDER-" + self.filename.encode() + b"-FILE_BORDER"

    def Size(self) -> int:
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

    def Read(self, path: str):
        """
        Read the file from a path
        """
        with open(path, "rb") as file:
            self.data = file.read()
            self.filename = path.split("/")[-1]
            self.has_file = True
            self.border = self.Generate_Border()
    
    def Write(self, path: str):
        """
        Write the file to a path
        """
        path = os.path.join(path, self.filename)
        with open(path, "wb") as file:
            file.write(self.data)
