import argparse
import pathlib

from .http_server import Server, Request, Response


def process_request(request, directory):

    if request.path == "/":
        response = Response(status=200)

    elif request.path.startswith("/echo/"):
        response_body = request.path.replace("/echo/", "", 1)
        response = Response(status=200)
        response.add_header("Content-Type", "text/plain")
        response.set_body(response_body)

    elif request.path.startswith("/files/"):
        filename = request.path.replace("/files/", "", 1)
        match request.method:
            case "GET":
                if (
                    directory is None
                    or not (directory / filename).exists()
                    or not (directory / filename).is_file()
                ):
                    response = Response(status=404)
                else:
                    response = Response(status=200)
                    response.set_body(directory / filename)
            case "POST":
                if directory is None:
                    response = Response(status=424)
                else:
                    with open(directory / filename, "wb") as destination_file:
                        destination_file.write(request.body)
                    response = Response(status=201)
                
    elif request.path == "/user-agent":
        response_body = request.headers.get("User-Agent", "")
        response = Response(status=200)
        response.add_header("Content-Type", "text/plain")
        response.set_body(response_body)

    else:
        response = Response(status=404)
    return response


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=str, help="Directory for files IO")
    args = parser.parse_args()
    directory = None
    if args.directory:
        directory = pathlib.Path(args.directory)
        if not directory.exists():
            raise OSError(f"directory {directory} does not exist.")
        directory = directory.absolute()
    server = Server(("localhost", 4221), process_request, directory)
    server.serve()
