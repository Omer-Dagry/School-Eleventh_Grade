import socket

client_socket = socket.socket()
try:
    # HTTP client
    client_socket.connect(('127.0.0.1', 8080))
    client_socket.sendall('GET /randevus?id=123456789 HTTP/1.1\r\nAuthorization: darth-vader\r\n\r\n'.encode())
    res = client_socket.recv(1024).decode()
    # get the port
    port = int(res[-5:])
    # server code
    server_socket = socket.socket()
    try:
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(1)
        client_socket, client_address = server_socket.accept()
        try:
            # receive and print the message
            msg = client_socket.recv(1024).decode()
            print(msg)
        except socket.error as err:
            print('received socket error' + str(err))
        finally:
            client_socket.close()
    except socket.error as err:
        print('received socket error' + str(err))
    finally:
        server_socket.close()
except socket.error as err:
    print('received socket error' + str(err))
finally:
    client_socket.close()
