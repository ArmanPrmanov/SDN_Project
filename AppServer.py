import sys
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from queue import Queue
import requests
import json
from NetworkGraph import NetworkGraph

# TODO: Replace later with real class
class ManagerApp:
    net_graph = None
    
    def __init__(self):
        self.net_graph = NetworkGraph()

class AppServerHandler(BaseHTTPRequestHandler):
    Framework = None
    # Separate queues for GET and POST requests
    get_request_queue = Queue()
    post_request_queue = Queue()
    response_dict = {}
    man_app = ManagerApp()

    def do_GET(self):
        # Queue the request and wait for a response
        #request_id = self.path
        #AppServerHandler.get_request_queue.put(request_id)

        # Wait until the main loop processes and stores a response
        #while request_id not in AppServerHandler.response_dict:
        #    time.sleep(0.1)  # Polling delay

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
                url = f"http://{host_ip}:8000/api/get/status"  # Assuming hosts serve on port 8000
                try:
                    response = requests.get(url)
                    responses.append(response.json())
                except:
                    print(f'Failed to fetch from {url}')
                    responses.append(f'Failed to fetch from {url}')

            # Respond with a JSON message for the status check
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(responses).encode("utf-8"))
        elif self.path == '/topo':
            # Respond with a JSON message for the status check
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"data": self.man_app.net_graph.CONTROLLER_IP}
            self.wfile.write(json.dumps(response).encode("utf-8"))
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
            
def main(ip='127.0.0.1', port=8000):
    # Check for command-line arguments for IP and port
    if len(sys.argv) > 1:
        ip = sys.argv[1]  # Get IP from command-line argument
    if len(sys.argv) > 2:
        port = int(sys.argv[2])  # Get port from command-line argument, if provided


    server_address = (ip, port)
    httpd = HTTPServer(server_address, AppServerHandler)
    print(f"Starting server on {ip}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

