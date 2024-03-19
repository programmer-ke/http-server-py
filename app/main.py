from .http_server import Server, Request, Response


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


if __name__ == "__main__":
    server = Server(
        ("localhost", 4221), request_handler=process_request
    )
    server.serve()
