from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import re
import requests
import sys
from task import Task

host_priority = random.randint(1, 5)
app_ip = '127.0.0.1'
MEC_ip = '10.0.0.2'

class HostClientHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if re.search('/api/get/*', self.path):
            webhook = self.path.split('/')[-1]
            if webhook == "init":
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                
                body = {"priority": host_priority}
                body_json = json.dumps(body).encode('utf-8')  # Encode to bytes
                self.wfile.write(body_json)
            else:
                self.send_response(404, f'Not Found webhook {webhook}')
        else:
            self.send_response(403)
        self.end_headers()
        
    def do_create_task(self):
        rand_task_id = random.randint(1,100000)
        task = Task(rand_task_id)

def main(ip='127.0.0.1', port=8000):
    # Check for command-line arguments for IP and port
    if len(sys.argv) > 1:
        ip = sys.argv[1]  # Get IP from command-line argument
    if len(sys.argv) > 2:
        port = int(sys.argv[2])  # Get port from command-line argument, if provided


    server_address = (ip, port)
    httpd = HTTPServer(server_address, HostClientHandler)
    print(f"Starting server on {ip}:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    main()


