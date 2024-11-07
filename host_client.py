from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random
import re
import requests
import sys

from mec_server import app_ip
from task import Task

device_id = random.randint(1, 1000)
host_priority = random.randint(1, 5)

# List to store pending tasks
pending_tasks = [Task(task_id=i) for i in range(1, 6)]  # Initialize with sample tasks


class HostClientHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if re.search('/api/get/*', self.path):
            webhook = self.path.split('/')[-1]

            if webhook == "status":
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

                # JSON response for the status
                status_body = {
                    "class": "device",
                    "id": device_id,
                    "priority": host_priority
                }
                status_body_json = json.dumps(status_body).encode('utf-8')
                self.wfile.write(status_body_json)

            elif webhook == "tasks":
                # New "tasks" endpoint for task list
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()

                # Create a dictionary with indexed tasks
                tasks_dict = {i: str(task) for i, task in enumerate(pending_tasks)}
                tasks_json = json.dumps(tasks_dict).encode('utf-8')
                self.wfile.write(tasks_json)

            else:
                self.send_response(404, f'Not Found webhook {webhook}')
        else:
            self.send_response(403)
        self.end_headers()

    def post_resource_request(self, task):
        # Randomly generate input/output data sizes for the task
        input_data_size = random.randint(10, 100)  # in MB, adjust as needed
        output_data_size = random.randint(10, 50)  # in MB, adjust as needed

        # Prepare JSON object for the task resource request
        resource_request_data = {
            "d_id": device_id,
            "t_id": task.task_id,
            "input_data_size": input_data_size,
            "output_data_size": output_data_size,
            "cpu_cycles": task.cpu_cycles,
            "memory": task.memory  # Replace with actual memory value if specific to task/device
        }

        # Send POST request to manager application
        try:
            response = requests.post(app_ip, json=resource_request_data)
            if response.status_code == 200:
                print(f"Resource request for task {task.task_id} sent successfully.")
            else:
                print(f"Failed to send resource request for task {task.task_id}. Status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error sending resource request: {e}")
        
    def do_create_task(self):
        rand_task_id = random.randint(1,100000)
        task = Task(rand_task_id)
        return task
    
    def do_ask_for_mec(self):
        task = self.do_create_task()
        # send request with Task info to Framework
        # get response from Framework about available MEC server
        # send request with Task body to MEC server
        # get response from MEC with Task result
        

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

