import unittest
from . import main


class RequestTestCase(unittest.TestCase):
    def test_can_parse_no_headers_no_body(self):
        request_bytes = b"GET /foo HTTP/1.1\r\n\r\n"
        req = main.Request(request_bytes)
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
        req = main.Request(request_bytes)
        self.assertEqual(req.headers, {"Content-Type": "plain-text"})

        request_bytes = b"GET /foo HTTP/1.1\r\nContent-Type: plain-text\r\nContent-Length: 0\r\n\r\n"
        req = main.Request(request_bytes)
        self.assertEqual(
            req.headers, {"Content-Type": "plain-text", "Content-Length": "0"}
        )


class ResponseTestCase(unittest.TestCase):
    def test_can_add_status_code(self):
        response = main.Response(status=200)
        self.assertEqual(response.raw(), b"HTTP/1.1 200 OK\r\n\r\n")

    def test_can_add_headers(self):
        response = main.Response(status=200)
        response.add_header("Content-Type", "text/plain")

        self.assertEqual(
            response.raw(),
            b"HTTP/1.1 200 OK\r\n" b"Content-Type: text/plain\r\n" b"\r\n",
        )

        response.add_header("Vary", "*")
        self.assertEqual(
            response.raw(),
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Vary: *\r\n"
            b"\r\n",
        )

    def test_can_add_body(self):
        response = main.Response(status=200)
        response.add_header("Content-Type", "text/plain")
        body_text = "abcde"
        response.set_body(body_text)

        self.assertEqual(
            response.raw(),
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: 5\r\n"
            b"\r\n"
            b"abcde",
        )


if __name__ == "__main__":
    unittest.main()
