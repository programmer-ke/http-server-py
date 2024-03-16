import socket
import re


def main():

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client_socket, client_address = server_socket.accept()  # accept connection

    # read data from socket
    byte_msg = client_socket.recv(4096)
    response_text = process_request(byte_msg)
    # write to socket
    client_socket.sendall(bytes(response_text, "utf-8"))
    client_socket.close()


def process_request(request_bytes):
    request = Request(request_bytes)

    if request.path == "/":
        response = "HTTP/1.1 200 OK\r\n\r\n"
    elif request.path.startswith("/echo/"):
        response_body = path.replace("/echo/", "")
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n\r\n"
            f"{response_body}"
        )
    elif request.path == "/user-agent":
        response_body = request.headers.get("User-Agent", "")
        response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(response_body)}\r\n\r\n"
            f"{response_body}"
        )
    else:
        response = "HTTP/1.1 404 Not Found\r\n\r\n"
    return response


class Request:

    header_pattern = re.compile(
        r"""
        (?P<first_line>(?P<method>[a-zA-Z]+)\s(?P<path>.+)\s(?P<version>HTTP\/1.1))  # first line
        \r\n
        (?P<headers>(.+:.+\r\n)*)  # match zero or more headers
        """,
        re.VERBOSE,
    )

    def __init__(self, request_bytes):
        header_bytes = request_bytes[:request_bytes.find(b"\r\n\r\n") + len(b"\r\n")]
        parsed_header = self.header_pattern.match(header_bytes.decode("ISO-8859-1"))

        self.method = parsed_header.group("method")
        self.path = parsed_header.group("path")
        self.http_version = parsed_header.group("version")

        if header_str := parsed_header.group("headers"):
            self.headers = self._parse_headers(header_str)
        else:
            self.headers = None

    @staticmethod
    def _parse_headers(header_str):
        headers = [h for h in header_str.strip().split("\r\n")]
        headers = [h.split(":", maxsplit=1) for h in headers]
        return {k.strip(): v.strip() for k, v in headers}

if __name__ == "__main__":
    main()
