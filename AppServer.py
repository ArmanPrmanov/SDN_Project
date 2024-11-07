import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from queue import Queue
import requests
import json

class AppServerHandler(BaseHTTPRequestHandler):
    Framework = None
    # Separate queues for GET and POST requests
    get_request_queue = Queue()
    post_request_queue = Queue()
    response_dict = {}

    def do_GET(self):
        # Queue the request and wait for a response
        request_id = self.path
        AppServerHandler.get_request_queue.put(request_id)

        # Wait until the main loop processes and stores a response
        while request_id not in AppServerHandler.response_dict:
            time.sleep(0.1)  # Polling delay

        """Handles GET requests."""
        if self.path == '/status':
            # Respond with a JSON message for the status check
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            response = {"status": "AppServer running"}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        elif self.path == '/fetch':
            responses = []
            parsed_hosts = ['10.0.0.1', '10.0.0.2', '10.0.0.3']
            for i in range(len(parsed_hosts)):
                host_ip = parsed_hosts[i]  # Get the IP of each host
                url = f"http://{host_ip}:8000/api/get/state"  # Assuming hosts serve on port 8000
                try:
                    response = requests.get(url)
                    responses.append(response)
                except:
                    print(f"Failed to fetch from {url}")
            self.wfile.write(json.dumps(responses).encode("utf-8"))
        else:
            # Handle undefined endpoints
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        # Queue the request and wait for a response
        request_id = self.path
        AppServerHandler.post_request_queue.put(request_id)

        # Wait until the main loop processes and stores a response
        while request_id not in AppServerHandler.response_dict:
            time.sleep(0.1)  # Polling delay

        response_data = AppServerHandler.response_dict.pop(request_id)

        """Handles POST requests."""
        if self.path == '/data':
            # Read data from the request
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            print("Received POST data:", post_data.decode("utf-8"))

            # Send a success response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")
            
