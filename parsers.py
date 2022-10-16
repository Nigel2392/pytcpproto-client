"""
    Basic utilities for parsing the requests and responses.
"""
from .files import File
import re

def parse_header(data: bytes):
    """
    Function for parsing headers
    """
    header_dict = {}
    # Split the last \r\n\r\n
    data_list = data.split(b'\r\n\r\n', 1)
    
    if len(data_list) != 2:
        raise Exception("Invalid header")
    header, content = data_list
    for line in header.split(b"\r\n"):
        
        line_list = line.split(b":")
        key = line_list[0].decode()
        value_list = []
        for item in line_list[1:]:
            value_list.append(item.decode())

        value = line_list[1:]
        value = ":".join(value_list)
        header_dict[key] = value
    return header_dict, content

def parse_file(header: dict, content: bytes):
    """
    Function for parsing files
    """
    has_file = header.get("HAS_FILE", "false")
    if has_file.lower() == "true":
        # Get the file border
        file_border = header["FILE_BOUNDARY"]
        # Split the content by the file border
        starting_b = b"--" + file_border.encode() + b"--"
        ending_b = b"----" + file_border.encode() + b"----"

        # regex to get the content in between the borders
        regex = re.compile(starting_b + b"(.*?)" + ending_b, re.DOTALL)
        file_content = regex.findall(content)[0]
        # Create a file object
        file = File(filename=header["FILE_NAME"], data=file_content, border=file_border)
        # replace the content with the content without the file
        content = content.replace(file_content, b"")
        content = content.replace(ending_b, b"")
        content = content.replace(starting_b, b"")
        return file, content
    else:
        return None, content
    