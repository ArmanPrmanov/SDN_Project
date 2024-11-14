import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json

from ManagerApp import ManagerApp

class AppServerHandler(BaseHTTPRequestHandler):
    Framework = None
    man_app = ManagerApp()

    def do_GET(self):
        if self.path == '/status':
            from NetworkGraph import NetworkGraph
            self.man_app.network_graph = NetworkGraph('10.0.2.15')
            self.man_app.network_graph.create_topo()

            # Respond with a JSON message for the status check
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            response = {"status": "AppServer running"}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        elif self.path == '/fetch':
            responses = []
            parsed_hosts = self.man_app.network_graph.parsed_hosts
            # parsed_hosts = [{}]
            for i in range(len(parsed_hosts)):
                host_ip = parsed_hosts[i]['ipv4']  # Get the IP of each host
                url = f"http://{host_ip}:8000/status"  # Assuming hosts serve on port 8000
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
            # response = {"data": self.man_app.network_graph.CONTROLLER_IP}
            response = {"data": self.man_app.network_graph.parsed_hosts}
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            # Handle undefined endpoints
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/get-mec":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                request_data = json.loads(post_data)
                task_from_device = request_data.get('task', {})

                # Extract task properties
                task_id = task_from_device.get('id')
                cpu_cycles = task_from_device.get('cpu_cycles')
                memory = task_from_device.get('memory')
                # Modify the string as required

                # TODO: process task_from_device

                # Prepare the response JSON
                response = {"data": '10.0.0.2'}
                response_json = json.dumps(response).encode('utf-8')

                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(response_json)
            except (json.JSONDecodeError, KeyError):
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'{"error": "Invalid JSON"}')
            
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

