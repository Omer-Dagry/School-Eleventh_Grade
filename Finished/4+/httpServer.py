"""
 HTTP Server
 Author: Omer Dagry
"""

import socket
import os
import logging

# logging
LOG_FORMAT = "%(levelname)s | %(asctime)s | %(processName)s | %(message)s"
LOG_LEVEL = logging.DEBUG
LOG_DIR = 'log'
LOG_FILE = LOG_DIR + "/4+.log"

DEFAULT_URL = "webroot/index.html"
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
             "gif": "image/jpeg\r\n", "png": "image/png\r\n"}
NUMBERS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
NOT_ALLOWED = [">", "<", ":", '"', "/", "\\", "|", "?", "*"]
HTTP_TYPE = ["GET", "POST"]

QUEUE_SIZE = 10
IP = '0.0.0.0'
PORT = 80
SOCKET_TIMEOUT = 2


def get_file_data(file_name):
    """
    Get data from file
    :param file_name: the name of the file
    :return: the file data in a string
    """
    if not os.path.isfile(file_name):
        return
    else:
        file = open(file_name, "rb")
        data = file.read()
        file.close()
        return data


def bad():
    """
    assembles a http 400 bad-request response
    """
    uri = WEB_ROOT + STRINGS["400"]
    status_code = STATUS_CODES["bad"]
    data = get_file_data(uri)
    content_type = CONTENT_TYPE + FILE_TYPE["png"]
    content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
    http_response = (HTTP + status_code + content_type + content_length + "\r\n")
    logging.debug("[Server]: " + http_response)
    http_response = http_response.encode() + data
    return http_response


def not_found():
    """
    assembles a http 404 not found response
    """
    uri = WEB_ROOT + STRINGS["404"]
    status_code = STATUS_CODES["not found"]
    data = get_file_data(uri)
    content_type = CONTENT_TYPE + FILE_TYPE["png"]
    content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
    http_response = (HTTP + status_code + content_type + content_length + "\r\n")
    logging.debug("[Server]: " + http_response)
    http_response = http_response.encode() + data
    return http_response


def handle_client_request(resource, client_socket, data):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :param data: in case the request of the client is a POST request
    :return: None
    """
    """ """
    resource = resource.split(' ')[1]
    uri = ""
    status_code = ""
    http_response = ""
    flag = True
    if resource == '/':
        uri = DEFAULT_URL
        status_code = STATUS_CODES["ok"]
        http_header = CONTENT_TYPE + FILE_TYPE["html"]
        content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
        data = get_file_data(uri)
        http_response = (HTTP + status_code + http_header + content_length + "\r\n")
        logging.debug("[Server]: " + http_response)
        http_response = http_response.encode() + data
    elif "calculate-next?num=" in resource:
        is_ok = False
        for char in resource:
            if is_ok:
                if char not in NUMBERS:
                    is_ok = False
                    break
            else:
                if char in NUMBERS:
                    is_ok = True
        if is_ok:
            flag = False
            num = int(resource.split("=")[-1])
            num = str(num + 1)
            status_code = STATUS_CODES["ok"]
            http_header = CONTENT_TYPE + FILE_TYPE["txt"] + CONTENT_LENGTH + str(len(num)) + "\r\n"
            http_response = (HTTP + status_code + http_header + "\r\n")
            logging.debug("[Server]: " + http_response)
            http_response = http_response.encode() + num.encode()
        else:
            http_response = bad()
    elif "calculate-area?height=" in resource and "&width=" in resource:
        is_ok = False
        first_parameter = True
        count = 6
        height = ""
        width = ""
        for char in resource:
            if is_ok and first_parameter:
                if char not in NUMBERS:
                    if char != "&":
                        is_ok = False
                    first_parameter = False
                else:
                    height += char
            elif first_parameter:
                if char in NUMBERS:
                    is_ok = True
                    height += char
            else:
                if count == 0:
                    width += char
                    if char not in NUMBERS:
                        is_ok = False
                        break
                else:
                    count -= 1
        if is_ok:
            flag = False
            area = str((int(width) * int(height)) / 2)
            status_code = STATUS_CODES["ok"]
            http_header = CONTENT_TYPE + FILE_TYPE["txt"] + CONTENT_LENGTH + str(len(area)) + "\r\n"
            http_response = (HTTP + status_code + http_header + "\r\n")
            logging.debug("[Server]: " + http_response)
            http_response = http_response.encode() + area.encode()
        else:
            http_response = bad()
    elif "upload?file-name=" in resource:
        is_ok = False
        file_name = ""
        for char in resource:
            if is_ok:
                if char in NOT_ALLOWED:
                    is_ok = False
                    break
                else:
                    file_name += char
            else:
                if char == "=":
                    is_ok = True
        if is_ok:
            flag = False
            msg = ""
            content_type = ""
            content_length = ""
            file_name_type = file_name.split(".")
            file_name = file_name_type[0]
            file_type = file_name_type[1]
            if file_type not in FILE_TYPE:  # במקרה שהפורמט של הקובץ לא פורמט שנתמך משנה את הפורמט ל"jpg"
                file_type = "jpg"
                msg = '<br><br>!!  File type not supported, file type changed to "jpg"  !!'
                content_type = CONTENT_TYPE + FILE_TYPE["jpg"]
                content_length = CONTENT_LENGTH + str(len(msg)) + "\r\n"
            file_name = WEB_ROOT + STRINGS["up"] + file_name + "." + file_type
            with open(file_name, 'wb') as photo:
                photo.write(data)
            status_code = STATUS_CODES["ok"]
            http_response = (HTTP + status_code + content_type + content_length + "\r\n") + msg
            logging.debug("[Server]: " + http_response)
            http_response = http_response.encode()
    elif "image?image-name=" in resource:
        is_ok = False
        file_name = ""
        for char in resource:
            if is_ok:
                if char in NOT_ALLOWED:
                    is_ok = False
                    break
                else:
                    file_name += char
            else:
                if char == "=":
                    is_ok = True
        if is_ok:
            flag = False
            print(file_name)
            file_name = WEB_ROOT + STRINGS["up"] + file_name
            if file_name.split(".")[-1] not in FILE_TYPE:
                file_name = "no can do"
            if os.path.isfile(file_name):
                status_code = STATUS_CODES["ok"]
                http_header = CONTENT_TYPE + FILE_TYPE[file_name.split(".")[-1]]
                content_length = CONTENT_LENGTH + str(os.path.getsize(file_name)) + "\r\n"
                data = get_file_data(file_name)
                http_response = (HTTP + status_code + http_header + content_length + "\r\n")
                logging.debug("[Server]: " + http_response)
                http_response = http_response.encode() + data
            else:
                http_response = not_found()
    elif resource == '/forbidden':
        uri = WEB_ROOT + STRINGS["403"]
        status_code = STATUS_CODES["forbidden"]
        data = get_file_data(uri)
        content_type = CONTENT_TYPE + FILE_TYPE["png"]
        content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
        http_response = (HTTP + status_code + content_type + content_length + "\r\n")
        logging.debug("[Server]: " + http_response)
        http_response = http_response.encode() + data
    elif resource == "/moved":
        uri = ""
        status_code = STATUS_CODES["moved"]
        http_response = (HTTP + STATUS_CODES["moved"] + "location: /" + "\r\n\r\n")
        logging.debug("[Server]: " + http_response)
        http_response = http_response.encode()
    elif resource == "/error":
        uri = WEB_ROOT + STRINGS["500"]
        status_code = STATUS_CODES["server error"]
        data = get_file_data(uri)
        content_type = CONTENT_TYPE + FILE_TYPE["png"]
        content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
        http_response = (HTTP + status_code + content_type + content_length + "\r\n")
        logging.debug("[Server]: " + http_response)
        http_response = http_response.encode() + data
    else:
        uri = WEB_ROOT + resource
        if os.path.isfile(uri):
            file_type = uri.split('.')[-1]
            http_header = CONTENT_TYPE
            http_header += FILE_TYPE[file_type]
            status_code = STATUS_CODES["ok"]
            http_response = HTTP + status_code + http_header
        else:
            http_response = not_found()
    if status_code == STATUS_CODES["ok"] and uri != DEFAULT_URL and flag:
        data = get_file_data(uri)
        content_length = CONTENT_LENGTH + str(os.path.getsize(uri)) + "\r\n"
        http_response = (http_response + content_length + "\r\n")
        logging.debug("[Server]: " + http_response)
        http_response = http_response.encode() + data
    client_socket.send(http_response)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    get = request.split(" ")
    if get[0] in HTTP_TYPE and len(get[1]) > 0 and "HTTP/1.1\r\n" in get[2] \
            and "\r\n\r\n" in request and request.count("\r\n") >= 4:
        return True, request
    else:
        return False, request


def handle_client(client_socket):
    """
    Handles client requests: verifies client's requests are legal HTTP, calls
    function to handle the requests
    :param client_socket: the socket for the communication with the client
    :return: None
    """
    print('Client connected')
    while True:
        client_request = ""
        client_data = ""
        while True:
            client_request += client_socket.recv(1).decode()
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
        logging.debug("[Client]: " + client_request + " client_data, can't log")
        if client_request != "":
            valid_http, resource = validate_http_request(client_request)
            if valid_http:
                logging.debug('Got a valid HTTP request')
                print('Got a valid HTTP request')
                handle_client_request(resource, client_socket, client_data)
            else:
                logging.debug('Error: Not a valid HTTP request')
                print('Error: Not a valid HTTP request')
                http_response = bad()
                client_socket.send(http_response)
                break
    print('Closing connection')


def main():
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.basicConfig(format=LOG_FORMAT, filename=LOG_FILE, level=LOG_LEVEL)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        logging.info("Listening for connections on port %d" % PORT)
        print("Listening for connections on port %d" % PORT)
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                logging.info("Client Connected " + client_address[0] + str(client_address[1]))
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                logging.warning('received socket exception - ' + str(err))
                print('received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        logging.warning('received socket exception - ' + str(err))
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    main()
