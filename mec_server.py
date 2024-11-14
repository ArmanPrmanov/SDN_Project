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
        if self.path == "/status":
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

        elif self.path == "/tasks":
            # New "tasks" endpoint for assigned task list
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()

            # Dictionary of indexed tasks
            tasks_dict = {i: str(task) for i, task in enumerate(assigned_tasks)}
            tasks_json = json.dumps(tasks_dict).encode('utf-8')
            self.wfile.write(tasks_json)


        else:
            # Handle undefined endpoints
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

    def do_POST(self):
        if self.path == "/exec-task":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)

            try:
                request_data = json.loads(post_data)
                string_from_device = request_data.get('data', '')

                # Modify the string as required
                modified_string = f"{string_from_device} executed on MEC"

                # Prepare the response JSON
                response = {"data": modified_string}
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
    httpd = HTTPServer(server_address, MECServerHandler)
    print(f"Starting server on {ip}:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    main()

