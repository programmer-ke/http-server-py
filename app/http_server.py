import pathlib
import re
import socket
import threading


HEADER_ENCODING = "ISO-8859-1"
UTF_8_ENCODING = "utf-8"
RECV_SIZE_BYTES = 4096
CHUNK_SIZE = 4096


class Server:
    def __init__(self, address, request_handler, directory=None):
        self._address = address
        self._request_handler = request_handler
        self._directory = directory

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
        response = self._request_handler(Request(byte_msg), self._directory)
        for chunk in response:
            client_socket.sendall(chunk)
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

        end_of_header_idx = request_bytes.find(b"\r\n\r\n") + len(b"\r\n")
        header_bytes = request_bytes[:end_of_header_idx]
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

        self.body = b""
        if self.headers and "Content-Length" in self.headers:
            self.body = request_bytes[end_of_header_idx + len(b"\r\n"):]

    @staticmethod
    def _parse_headers(header_str):
        headers = [h for h in header_str.strip().split("\r\n")]
        headers = [h.split(":", maxsplit=1) for h in headers]
        return {k.strip(): v.strip() for k, v in headers}


class Response:

    _status_mapping = {
        200: "200 OK",
        201: "Created",
        404: "404 Not Found",
        424: "424 Failed Dependency",
        500: "500 Internal Server Error",
    }

    def __init__(self, status):
        self._status = status
        self._headers = {}
        self._body = None

    def add_header(self, name, value):
        self._headers[name] = value

    def set_body(self, body):
        self._body = body

    def _raw(self):
        status_code = self._status_mapping[self._status]
        response_parts = [f"HTTP/1.1 {status_code}\r\n"]

        body = b""
        if self._body and isinstance(self._body, pathlib.Path):
            self.add_header("Content-Type", "application/octet-stream")
            self.add_header("Content-Length", self._get_file_size(self._body))
        elif self._body:
            body = self._body.encode(UTF_8_ENCODING)
            self.add_header("Content-Length", len(body))

        headers = [f"{k}: {v}\r\n" for k, v in self._headers.items()]
        response_parts.extend(headers)
        response_parts.append("\r\n")
        full_header = "".join(response_parts).encode(HEADER_ENCODING)
        yield full_header

        if isinstance(self._body, pathlib.Path):
            # body is a file, yield chunks until complete
            with open(self._body, "rb") as file_to_send:
                sentinel = b""
                for chunk in iter(
                    lambda: file_to_send.read(CHUNK_SIZE),
                    sentinel,
                ):
                    yield chunk
        else:
            # body is bytes in memory, simply yield
            yield body

    @staticmethod
    def _get_file_size(path):
        return path.stat().st_size

    def __bytes__(self):
        return b"".join([chunk for chunk in self._raw()])

    def __iter__(self):
        return self._raw()
