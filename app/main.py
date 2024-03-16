import socket
import re

REQUEST_PATTERN = re.compile(r"""
(?P<first_line>(?P<method>[a-zA-Z]+)\s(?P<path>.+)\s(HTTP\/1.1))
\r\n
(?P<headers>(.+:.+\r\n)*)  # match zero or more headers
\r\n
(?P<body>.*)  # optional body
""", re.VERBOSE)


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
    matches = REQUEST_PATTERN.match(request)
    path = matches.group("path")
    headers = parse_headers(matches.group("headers"))

    if path == "/":
        response = "HTTP/1.1 200 OK\r\n\r\n"
    elif path.startswith("/echo/"):
        response_body = path.replace("/echo/", "")
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n\r\n"
            f"{response_body}"
        )
    elif path == "/user-agent":
        response_body = headers.get("User-Agent", "")
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n\r\n"
            f"{response_body}"
        )
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    return response


def parse_headers(header_str):
    headers = [h for h in header_str.strip().split("\r\n")]
    headers = [h.split(":", maxsplit=1) for h in headers]
    return {k.strip(): v.strip() for k, v in headers}


if __name__ == "__main__":
    main()
