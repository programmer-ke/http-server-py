import unittest
import pathlib
import tempfile

from . import http_server


class RequestTestCase(unittest.TestCase):
    def test_can_parse_no_headers_no_body(self):
        request_bytes = b"GET /foo HTTP/1.1\r\n\r\n"
        req = http_server.Request(request_bytes)
        self.assertTrue(
            all(
                [
                    req.method == "GET",
                    req.path == "/foo",
                    req.http_version == "HTTP/1.1",
                    req.headers == None,
                ]
            )
        )

    def test_can_parse_only_headers(self):
        request_bytes = (
            b"GET /foo HTTP/1.1\r\nContent-Type: plain-text\r\n\r\n"
        )
        req = http_server.Request(request_bytes)
        self.assertEqual(req.headers, {"Content-Type": "plain-text"})

        request_bytes = b"GET /foo HTTP/1.1\r\nContent-Type: plain-text\r\nContent-Length: 0\r\n\r\n"
        req = http_server.Request(request_bytes)
        self.assertEqual(
            req.headers, {"Content-Type": "plain-text", "Content-Length": "0"}
        )

    def test_can_parse_header_and_body(self):
        request_bytes = (
            b"POST /foo HTTP/1.1\r\n"
            b"Content-Length: 6\r\n"
            b"\r\n"
            b"abc123"
        )
        req = http_server.Request(request_bytes)
        self.assertEqual(req.headers, {"Content-Length": "6"})
        self.assertEqual(req.body, b"abc123")

class ResponseTestCase(unittest.TestCase):
    def test_can_add_status_code(self):
        response = http_server.Response(status=200)
        self.assertEqual(bytes(response), b"HTTP/1.1 200 OK\r\n\r\n")

    def test_can_add_headers(self):
        response = http_server.Response(status=200)
        response.add_header("Content-Type", "text/plain")

        self.assertEqual(
            bytes(response),
            b"HTTP/1.1 200 OK\r\n" b"Content-Type: text/plain\r\n" b"\r\n",
        )

        response.add_header("Vary", "*")
        self.assertEqual(
            bytes(response),
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Vary: *\r\n"
            b"\r\n",
        )

    def test_can_add_body_as_text(self):
        response = http_server.Response(status=200)
        response.add_header("Content-Type", "text/plain")
        body_text = "abcde"
        response.set_body(body_text)

        self.assertEqual(
            bytes(response),
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 5\r\n"
            b"\r\n"
            b"abcde",
        )

    def test_can_add_body_as_file_path(self):

        with tempfile.TemporaryDirectory() as tmpdirname:
            file_path = pathlib.Path(tmpdirname) / "foobar.txt"
            with open(file_path, "w") as destfile:
                destfile.write("abc123")

            response = http_server.Response(status=200)
            response.set_body(file_path)

            self.assertEqual(
                bytes(response),
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/octet-stream\r\n"
                b"Content-Length: 6\r\n"
                b"\r\n"
                b"abc123",
            )


if __name__ == "__main__":
    unittest.main()
