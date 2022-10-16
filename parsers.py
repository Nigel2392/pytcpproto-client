"""
    Basic utilities for parsing the requests and responses.
"""

def ParseHeader(data: bytes):
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

