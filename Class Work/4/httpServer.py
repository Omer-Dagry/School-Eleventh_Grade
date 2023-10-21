"""
 HTTP Server Shell
 Author: Omer Dagry
 Purpose: Provide a basis for Ex. 4
 Note: The code is written in a simple way, without classes, log files or
 other utilities, for educational purpose
 Usage: Fill the missing functions and constants
"""
# TO DO: import modules

import socket
import os

# TO DO: set constants

DEFAULT_URL = "webroot/index.html"
HTTP = "HTTP/1.1 "
STATUS_CODES = {"ok": "200 OK\r\n", "bad": "400 BAD REQUEST\r\n", "not found": "404 NOT FOUND\r\n",
                "forbidden": "403 FORBIDDEN\r\n", "moved": "302 FOUND\r\n",
                "server error": "500 INTERNAL SERVER ERROR\r\n"}
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
    file = open(file_name, "rb")
    data = file.read()
    file.close()
    return data


def handle_client_request(resource, client_socket):
    """
    Check the required resource, generate proper HTTP response and send
    to client
    :param resource: the required resource
    :param client_socket: a socket for the communication with the client
    :return: None
    """
    """ """
    resource = resource.split(' ')[1]
    if resource == '/':
        uri = DEFAULT_URL
        status_code = STATUS_CODES["ok"]
        http_header = "Content-Type: text/html;charset=utf-8\r\n"
        content_length = "Content-Length: " + str(os.path.getsize(uri)) + "\r\n"
        data = get_file_data(uri)
        http_response = (HTTP + status_code + http_header + content_length + "\r\n").encode() + data
    elif resource == '/forbidden':
        uri = "webroot" + "/imgs/403.png"
        status_code = STATUS_CODES["forbidden"]
        data = get_file_data(uri)
        content_type = "Content-Type: image/png\r\n"
        content_length = "Content-Length: " + str(os.path.getsize(uri)) + "\r\n"
        http_response = (HTTP + status_code + content_type + content_length + "\r\n").encode() + data
    elif resource == "/moved":
        uri = ""
        status_code = STATUS_CODES["moved"]
        http_response = (HTTP + STATUS_CODES["moved"] + "location: /" + "\r\n\r\n").encode()
    elif resource == "/error":
        uri = "webroot" + "/imgs/500.png"
        status_code = STATUS_CODES["server error"]
        data = get_file_data(uri)
        content_type = "Content-Type: image/png\r\n"
        content_length = "Content-Length: " + str(os.path.getsize(uri)) + "\r\n"
        http_response = (HTTP + status_code + content_type + content_length + "\r\n").encode() + data
    else:
        uri = "webroot" + resource
        if os.path.isfile(uri):
            file_type = uri.split('.')[-1]
            http_header = "Content-Type: "
            if file_type == 'html':
                http_header += "text/html;charset=utf-8\r\n"
            elif file_type == 'jpg':
                http_header += "image/jpeg\r\n"
            elif file_type == 'css':
                http_header += "text/css\r\n"
            elif file_type == 'js':
                http_header += "text/javascript; charset=UTF-8\r\n"
            elif file_type == 'txt':
                http_header += "text/plain\r\n"
            elif file_type == 'ico':
                http_header += "image/x-icon\r\n"
            elif file_type == 'gif':
                http_header += "image/jpeg\r\n"
            elif file_type == 'png':
                http_header += "image/png\r\n"
            status_code = STATUS_CODES["ok"]
            http_response = HTTP + status_code + http_header
        else:
            uri = "webroot" + "/imgs/404.png"
            status_code = STATUS_CODES["not found"]
            data = get_file_data(uri)
            content_type = "Content-Type: image/png\r\n"
            content_length = "Content-Length: " + str(os.path.getsize(uri)) + "\r\n"
            http_response = (HTTP + status_code + content_type + content_length + "\r\n").encode() + data
    if status_code == STATUS_CODES["ok"] and uri != DEFAULT_URL:
        data = get_file_data(uri)
        content_length = "Content-Length: " + str(os.path.getsize(uri)) + "\r\n"
        http_response = (http_response + content_length + "\r\n").encode() + data
    client_socket.send(http_response)


def validate_http_request(request):
    """
    Check if request is a valid HTTP request and returns TRUE / FALSE and
    the requested URL
    :param request: the request which was received from the client
    :return: a tuple of (True/False - depending if the request is valid,
    the requested resource )
    """
    # TO DO: write function
    get = request.split(" ")
    if get[0] == "GET" and len(get[1]) > 0 and "HTTP/1.1" in get[2] and "\r\n\r\n" in request:
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
        # TO DO: insert code that receives client request
        # ...
        client_request = ""
        while True:
            client_request += client_socket.recv(1).decode()
            if "\r\n\r\n" in client_request:
                break
            if client_request == "":
                client_socket.close()
                break
        if client_request != "":
            valid_http, resource = validate_http_request(client_request)
            if valid_http:
                print('Got a valid HTTP request')
                handle_client_request(resource, client_socket)
            else:
                print('Error: Not a valid HTTP request')
                uri = "webroot" + "/imgs/400.png"
                status_code = STATUS_CODES["bad"]
                data = get_file_data(uri)
                content_type = "Content-Type: image/png\r\n"
                content_length = "Content-Length: " + str(os.path.getsize(uri)) + "\r\n"
                http_response = (HTTP + status_code + content_type + content_length + "\r\n").encode() + data
                client_socket.send(http_response)
                break
    print('Closing connection')


def main():
    # Open a socket and loop forever while waiting for clients
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind((IP, PORT))
        server_socket.listen(QUEUE_SIZE)
        print("Listening for connections on port %d" % PORT)
        while True:
            client_socket, client_address = server_socket.accept()
            try:
                print('New connection received')
                client_socket.settimeout(SOCKET_TIMEOUT)
                handle_client(client_socket)
            except socket.error as err:
                print('received socket exception - ' + str(err))
            finally:
                client_socket.close()
    except socket.error as err:
        print('received socket exception - ' + str(err))
    finally:
        server_socket.close()


if __name__ == "__main__":
    # Call the main handler function
    main()
