import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import re
import requests
import sys
from task import Task

# Initialize random CPU cycles and memory specifications for the server
cpu_cycles = random.randint(100000, 1000000)
memory = 2048  # Example memory in MB
server_id = random.randint(1000, 9999)  # Random server ID for this example
app_ip = '127.0.0.1'

# List to store tasks assigned to the server
assigned_tasks = [Task(task_id=i) for i in range(1, 6)]  # Sample tasks assigned to the server


class MECServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if re.search('/api/get/*', self.path):
            webhook = self.path.split('/')[-1]

            if webhook == "status":
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

                # JSON response for the server status
                status_body = {
                    "class": "server",
                    "id": server_id,
                    "cpu": cpu_cycles,
                    "mem": memory
                }
                status_body_json = json.dumps(status_body).encode('utf-8')
                self.wfile.write(status_body_json)

            elif webhook == "tasks":
                # New "tasks" endpoint for assigned task list
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

                # Dictionary of indexed tasks
                tasks_dict = {i: str(task) for i, task in enumerate(assigned_tasks)}
                tasks_json = json.dumps(tasks_dict).encode('utf-8')
                self.wfile.write(tasks_json)

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


