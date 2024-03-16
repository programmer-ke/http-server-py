import unittest
from . import main


class RequestTestCase(unittest.TestCase):
    def test_can_parse_no_headers_no_body(self):
        request_bytes = b"GET /foo HTTP/1.1\r\n\r\n"
        req = main.Request(request_bytes)
        self.assertTrue(all(
            [
                req.method == "GET",
                req.path == "/foo",
                req.http_version == "HTTP/1.1",
                req.headers == None
            ]
        ))
        
    def test_can_parse_only_headers(self):
        request_bytes = b"GET /foo HTTP/1.1\r\nContent-Type: plain-text\r\n\r\n"
        req = main.Request(request_bytes)
        self.assertEqual(req.headers, {"Content-Type": "plain-text"})

        request_bytes = b"GET /foo HTTP/1.1\r\nContent-Type: plain-text\r\nContent-Length: 0\r\n\r\n"
        req = main.Request(request_bytes)
        self.assertEqual(req.headers, {"Content-Type": "plain-text", "Content-Length": "0"})


if __name__ == "__main__":
    unittest.main()
