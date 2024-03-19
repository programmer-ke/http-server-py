import re
import socket
import threading


HEADER_ENCODING = "ISO-8859-1"
UTF_8_ENCODING = "utf-8"


def main():

    with socket.create_server(
        ("localhost", 4221), reuse_port=True
    ) as server_socket:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Received new connection via {client_address}")
            handler_thread = threading.Thread(
                target=handle_connection, args=(client_socket,)
            )
            handler_thread.start()


def handle_connection(client_socket):
    byte_msg = client_socket.recv(4096)
    response = process_request(Request(byte_msg))
    client_socket.sendall(response.raw())
    client_socket.close()


def process_request(request):

    if request.path == "/":
        response = Response(status=200)
    elif request.path.startswith("/echo/"):
        response_body = request.path.replace("/echo/", "")
        response = Response(status=200)
        response.add_header("Content-Type", "text/plain")
        response.set_body(response_body)

    elif request.path == "/user-agent":
        response_body = request.headers.get("User-Agent", "")
        response = Response(status=200)
        response.add_header("Content-Type", "text/plain")
        response.set_body(response_body)
    else:
        response = Response(status=404)
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
        header_bytes = request_bytes[
            : request_bytes.find(b"\r\n\r\n") + len(b"\r\n")
        ]
        parsed_header = self.header_pattern.match(
            header_bytes.decode(HEADER_ENCODING)
        )

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


class Response:

    _status_mapping = {200: "200 OK", 404: "404 Not Found"}

    def __init__(self, status):
        self._status = status
        self._headers = {}
        self._body = None

    def add_header(self, name, value):
        self._headers[name] = value

    def set_body(self, body):
        self._body = body

    def raw(self):
        status_code = self._status_mapping[self._status]
        response_parts = [f"HTTP/1.1 {status_code}\r\n"]

        body = b""
        if self._body:
            body = self._body.encode(UTF_8_ENCODING)
            self.add_header("Content-Length", len(body))

        headers = [f"{k}: {v}\r\n" for k, v in self._headers.items()]
        response_parts.extend(headers)
        response_parts.append("\r\n")
        full_header = "".join(response_parts).encode(HEADER_ENCODING)

        return full_header + body


if __name__ == "__main__":
    main()
