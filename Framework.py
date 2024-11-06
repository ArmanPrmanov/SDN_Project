import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import re
import requests
import sys
from task import Task

cpu_cycles = random.randint(100000, 1000000)
memory = 2048
app_ip = '127.0.0.1'

class MECServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if re.search('/api/get/*', self.path):
            webhook = self.path.split('/')[-1]
            if webhook == "state":
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                body = {"cpu_cycles": cpu_cycles, "memory": memory}
                body_json = json.dumps(body).encode('utf-8')  # Encode to bytes
                self.wfile.write(body_json)
            else:
                self.send_response(404, f'Not Found webhook {webhook}')
        else:
            self.send_response(403)
        self.end_headers()

def main(ip='127.0.0.1', port=8000):
    # Check for command-line arguments for IP and port
    if len(sys.argv) > 1:
        ip = sys.argv[1]  # Get IP from command-line argument
    if len(sys.argv) > 2:
        port = int(sys.argv[2])  # Get port from command-line argument, if provided


    server_address = (ip, port)
    httpd = HTTPServer(server_address, MECServerHandler)
    print(f"Starting server on {ip}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()


