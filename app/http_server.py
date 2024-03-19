import re
import socket
import threading


HEADER_ENCODING = "ISO-8859-1"
UTF_8_ENCODING = "utf-8"
RECV_SIZE_BYTES = 4096

class Server:
    def __init__(self, address, request_handler):
        self._address = address
        self._request_handler = request_handler

    def serve(self):

        with socket.create_server(
            self._address, reuse_port=True
        ) as server_socket:
            while True:
                client_socket, client_address = server_socket.accept()
                print(f"Received new connection via {client_address}")
                handler_thread = threading.Thread(
                    target=self.handle_connection, args=(client_socket,)
                )
                handler_thread.start()

    def handle_connection(self, client_socket):
        byte_msg = client_socket.recv(RECV_SIZE_BYTES)
        response = self._request_handler(Request(byte_msg))
        client_socket.sendall(bytes(response))
        client_socket.close()


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

    def __bytes__(self):
        return self.raw()