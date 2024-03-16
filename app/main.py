import socket

def main():
    # You can use print statements as follows for debugging,
    # they'll be visible when running tests.
    print("Logs from your program will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept()  # accept connection
    print(f"Received client connection via {client_address}")
    # read data from socket
    byte_msg = client_socket.recv(4096)
    response_text = process_request(byte_msg.decode("utf8"))
    # write to socket
    client_socket.sendall(bytes(response_text, "utf-8"))
    client_socket.close()


def process_request(request):
    first_line, *rest = request.split("\r\n")
    _, path, _ =  first_line.split(" ")
    if path == "/":
        response = "HTTP/1.1 200 OK\r\n"
    elif not path.startswith("/echo/"):
        response = "HTTP/1.1 404 Not Found\r\n"
    else:
        response_body = path.replace("/echo/", "")
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n\r\n"
            f"{response_body}"
        )
    return response


if __name__ == "__main__":
    main()
