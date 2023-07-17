import time
import socket
import ssl
import os

from flask import jsonify
from services.slack_service import (
  process_event_payload
)
from threading import Thread

def resolve_host(host):
  start = time.time()
  ip_address = socket.gethostbyname(host)
  end = time.time()
  return end - start

def make_ssl_connection(host, port):
  start = time.time()
  sock = socket.create_connection((host, port))
  ssl_sock = ssl.wrap_socket(sock)
  end = time.time()
  return end - start

# POST /slack/events
def post_event(request):
    # host = "api.openai.com"
    # resolution_time = resolve_host(host)
    # print("It took %.2f seconds to resolve %s." % (resolution_time, host))
    # port = 443
    # connection_time = make_ssl_connection(host, port)
    # print("It took %.2f seconds to make an SSL connection to %s." % (connection_time, host))
    
    if request.get("type") == "url_verification":
        return request.get("challenge")

    Thread(target=process_event_payload, args=(request,)).start()
    return jsonify({"message": "success"}), 200
