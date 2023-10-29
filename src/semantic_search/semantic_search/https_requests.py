import json
import socket
import ssl


def create_ssl_socket(host, port):
    context = ssl.create_default_context()
    sock = socket.create_connection((host, port))
    return context.wrap_socket(sock, server_hostname=host)


def parse_http_response(raw_response):
    # Split response into headers and body
    headers, _, body = raw_response.partition('\r\n\r\n')
    # Parse the status line and headers
    header_lines = headers.split('\r\n')
    status_line = header_lines[0]
    status_code = int(status_line.split()[1])  # Extract status code
    header_dict = {k: v for k, v in (line.split(': ', 1) for line in header_lines[1:])}
    return status_code, status_line, header_dict, body


def read_all_from_socket(ssock):
    buffer = b""
    while True:
        data = ssock.recv(4096)
        if not data:
            break
        buffer += data
    return buffer.decode()


def send_https_request(host, path, data, headers=None):
    if headers is None:
        headers = {}
    json_data = json.dumps(data)
    content_length = len(json_data)
    request_headers = {
        "Host": host,
        "Content-Type": "application/json",
        "Content-Length": str(content_length),
        "Connection": "close"
    }
    request_headers.update(headers)
    request = f"POST {path} HTTP/1.1\r\n"
    request += "".join(f"{key}: {value}\r\n" for key, value in request_headers.items())
    request += "\r\n" + json_data
    with create_ssl_socket(host, 443) as ssock:
        ssock.send(request.encode())
        raw_response = read_all_from_socket(ssock)

        status_code, status_line, response_headers, response_body = parse_http_response(raw_response)
        return status_code, status_line, response_headers, response_body
