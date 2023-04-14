"""
 HTTP Server
 Author: Omer Dagry
"""

import io
import os
import PIL
import time
import socket
import threading
import traceback
import urllib.parse

from PIL import Image


# Constants
WEB_ROOT = "webroot"
HTTP = "HTTP/1.1 "
STRINGS = {"up": "/uploads/", "400": "/imgs/400.png", "404": "/imgs/404.png", "403": "/imgs/403.png",
           "500": "/imgs/403.png"}
CONTENT_TYPE = "Content-Type: "
CONTENT_LENGTH = "Content-Length: "
STATUS_CODES = {"ok": "200 OK\r\n", "bad": "400 BAD REQUEST\r\n", "not found": "404 NOT FOUND\r\n",
                "forbidden": "403 FORBIDDEN\r\n", "moved": "302 FOUND\r\n",
                "server error": "500 INTERNAL SERVER ERROR\r\n"}
FILE_TYPE = {"html": "text/html;charset=utf-8\r\n", "jpg": "image/jpeg\r\n", "css": "text/css\r\n",
             "js": "text/javascript; charset=UTF-8\r\n", "txt": "text/plain\r\n", "ico": "image/x-icon\r\n",
             "gif": "image/jpeg\r\n", "png": "image/png\r\n", "svg": "image/svg+xml"}
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
NOT_ALLOWED = [">", "<", ":", '"', "/", "\\", "|", "?", "*"]
HTTP_TYPE = ["GET", "POST"]
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2

# Globals
print_ = print
printing_lock = threading.Lock()


def print(*values: object, sep: str | None = " ", end: str | None = "\n", file=None, flush: bool = False) -> None:
    printing_lock.acquire()
    print_(*values, sep=sep, end=end, file=file, flush=flush)
    printing_lock.release()


def read_file(file_name):
    """ Read A File """
    with open(file_name, "rb") as f:
        data = f.read()
    return data


def bad():
    """
    assembles a http 400 bad-request response
    """
    uri = WEB_ROOT + STRINGS["400"]
    # html = f"""<div style='background-image: url("{uri}");'></div>"""
    html = f"""<a href="{uri}"><img style="width:100%; height:100%;" src="{uri}"></a>"""
    content_length = CONTENT_LENGTH + str(len(html)) + "\r\n"
    http_response = (HTTP + STATUS_CODES["bad"] + FILE_TYPE["html"] + content_length + "\r\n" + html).encode()
    return http_response


def not_found():
    """
    assembles a http 404 not found response
    """
    uri = WEB_ROOT + STRINGS["404"]
    # html = f"""<div style='background-image: url("{uri}");'></div>"""
    html = f"""<a href="{uri}"><img style="width:100%; height:100%;" src="{uri}"></a>"""
    content_length = CONTENT_LENGTH + str(len(html)) + "\r\n"
    http_response = (HTTP + STATUS_CODES["not found"] + FILE_TYPE["html"] + content_length + "\r\n" + html).encode()
    return http_response


def handle_client_request(resource, client_socket: socket.socket, data: bytes):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :param data: in case the request of the client is a POST request
    :return: None
    """
    """ """
    resource = urllib.parse.unquote_plus(resource.split(' ')[1])
    status_code = ""
    uri = ""
    # if data is not None:
    #     pass  # POST request
    if resource == "/":
        resource = "/index.html"
    if "calculate-next?num=" in resource:
        num = resource.split("calculate-next?num=")[-1]
        if num.isnumeric():
            num = str(int(num) + 1)
            status_code = STATUS_CODES["ok"]
            http_header = CONTENT_TYPE + FILE_TYPE["txt"] + CONTENT_LENGTH + str(len(num)) + "\r\n"
            http_response = (HTTP + status_code + http_header + "\r\n" + num).encode()
        else:
            http_response = bad()
    elif "calculate-area?height=" in resource and "&width=" in resource:
        height = resource.split("calculate-area?height=")[-1]
        height, width = height.split("&width=")[-2:]
        if height.isnumeric() and width.isnumeric():
            area = str((int(width) * int(height)) / 2)
            status_code = STATUS_CODES["ok"]
            http_header = CONTENT_TYPE + FILE_TYPE["txt"] + CONTENT_LENGTH + str(len(area)) + "\r\n"
            http_response = (HTTP + status_code + http_header + "\r\n" + area).encode()
        else:
            http_response = bad()
    elif "upload?file-name=" in resource:
        file_name = resource.split("upload?file-name=")[-1]
        msg, content_type, content_length, http_response = "", "", "", ""
        file_name = file_name.split(".")
        file_type = file_name[-1]
        fn = ".".join(file_name[:-1])
        file_name = WEB_ROOT + STRINGS["up"] + fn
        if file_type not in FILE_TYPE:  # במקרה שהפורמט של הקובץ לא פורמט שנתמך משנה את הפורמט ל"jpg"
            try:
                im = Image.open(io.BytesIO(data))
                im = im.convert("RGB")
                im.save(f"{file_name}.jpg")
                msg = f'<br><br>!!  File type not supported, file type changed to "jpg"  !!' \
                      f'<br><br>file name: {f"{fn}.jpg"}'
                content_type = CONTENT_TYPE + FILE_TYPE["jpg"]
                content_length = CONTENT_LENGTH + str(len(msg)) + "\r\n"
                http_response = (HTTP + status_code + content_type + content_length + "\r\n" + msg).encode()
            except PIL.UnidentifiedImageError:
                http_response = bad()
        if http_response == "":
            with open(file_name, 'wb') as photo:
                photo.write(data)
            status_code = STATUS_CODES["ok"]
            content_length = CONTENT_LENGTH + "0\r\n"
            content_type = CONTENT_TYPE + FILE_TYPE[file_type]
            http_response = (HTTP + status_code + content_type + content_length + "\r\n").encode()
    elif "image?image-name=" in resource:
        file_name = resource.split("image?image-name=")[-1]
        file_name = WEB_ROOT + STRINGS["up"] + file_name
        if os.path.isfile(file_name):
            status_code = STATUS_CODES["ok"]
            http_header = CONTENT_TYPE + FILE_TYPE[file_name.split(".")[-1]]
            content_length = CONTENT_LENGTH + str(os.path.getsize(file_name)) + "\r\n"
            http_response = (HTTP + status_code + http_header + content_length + "\r\n").encode() + read_file(file_name)
        else:
            http_response = not_found()
    elif resource == '/forbidden':
        uri = WEB_ROOT + STRINGS["403"]
        status_code = STATUS_CODES["forbidden"]
        data = read_file(uri)
        content_type = CONTENT_TYPE + FILE_TYPE["png"]
        content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
        http_response = HTTP + status_code + content_type + content_length + "\r\n"
        http_response = http_response.encode() + data
    elif resource == "/moved":
        status_code = STATUS_CODES["moved"]
        http_response = HTTP + STATUS_CODES["moved"] + "location: /" + "\r\n\r\n"
        http_response = http_response.encode()
    elif resource == "/error":
        uri = WEB_ROOT + STRINGS["500"]
        status_code = STATUS_CODES["server error"]
        data = read_file(uri)
        content_type = CONTENT_TYPE + FILE_TYPE["png"]
        content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
        http_response = HTTP + status_code + content_type + content_length + "\r\n"
        http_response = http_response.encode() + data
    else:
        uri = WEB_ROOT + resource if not resource.startswith(f"/{WEB_ROOT}") else resource[1:]
        if os.path.isfile(uri):
            file_type = uri.split('.')[-1]
            http_header = CONTENT_TYPE
            http_header += FILE_TYPE[file_type]
            status_code = STATUS_CODES["ok"]
            http_response = HTTP + status_code + http_header
        else:
            http_response = not_found()
    if status_code == STATUS_CODES["ok"] and uri != "":
        data = read_file(uri)
        content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
        http_response += content_length + "\r\n"
        http_response = http_response.encode() + data
    while len(http_response) > 0:
        sent = client_socket.send(http_response)
        http_response = http_response[sent:]


def validate_http_request(request: str):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending on if the request is valid,
    the requested resource )
    """
    get = request.split(" ")
    if get[0] in HTTP_TYPE and len(get[1]) > 0 and "HTTP/1.1\r\n" in get[2] \
            and "\r\n\r\n" in request and request.count("\r\n") >= 4:
        return True, request
    else:
        return False, request


def handle_client(client_socket: socket.socket, client_address: tuple[str, int]):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :param client_address: the address of the client
    :return: None
    """
    stop = False
    while not stop:
        client_request = ""
        client_data = None
        while True:
            try:
                data = client_socket.recv(1).decode()
                client_request += data
            except socket.timeout:
                stop = True
                break
            if data == "":
                stop = True
                break
            if "\r\n\r\n" in client_request:
                break
            if client_request == "":
                client_socket.close()
                break
        if "POST" in client_request:
            headers = client_request.split("\r\n")
            for header in headers:
                if "Content-Length" in header:
                    headers = header
                    break
            data_length = int(headers[16:])
            client_data = b""
            while len(client_data) < data_length:
                client_data += client_socket.recv(data_length - len(client_data))
        if client_request != "":
            try:
                valid_http, resource = validate_http_request(client_request)
                if valid_http:
                    handle_client_request(resource, client_socket, client_data)
                else:
                    http_response = bad()
                    client_socket.send(http_response)
                    break
            except Exception as e:
                exc = traceback.format_exception(e)
                print(exc)
                http_response = bad()
                client_socket.send(http_response)
                break
    client_socket.close()
    print("Connection closed with '%s:%s'" % client_address)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen()
        print("Listening for connections on port %d" % PORT)
        while True:
            client_socket, client_address = server_socket.accept()
            client_socket: socket.socket
            client_address: tuple[str, int]
            print("New connection received from '%s:%s'" % client_address)
            client_socket.settimeout(SOCKET_TIMEOUT)
            t = threading.Thread(target=handle_client, args=(client_socket, client_address))
            t.start()
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()
    while threading.active_count() != 1:  # wait for all clients to close open connections
        time.sleep(0.1)


if __name__ == "__main__":
    main()
