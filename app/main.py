import socket


def main():
    # You can use print statements as follows for debugging,
    # they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept()  # accept connection
    print(f"Received client connection via {client_address}")
    # read data from socket
    chunks = []
    while True:
        msg = client_socket.recv(4096)
        if not msg:
            break
        chunks.append(msg)
    print(f"message received: {chunks}")
    # write to socket
    response_text = "HTTP/1.1 200 OK\r\n\r\n"
    client_socket.sendall(bytes(response_text))
    # close socket - necessary?


if __name__ == "__main__":
    main()
