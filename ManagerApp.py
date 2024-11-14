import requests
import json
import networkx
import asyncio
from NetworkGraph import NetworkGraph

def estimate_data_transfer_latency( task, path ):
    latency = 0.0
    data = task[2] + task[3]
    
    for link in path:
        latency += data / link['latency']

    return latency

def estimate_task_processing_latency( task, resource ):
    d_cpu = task[-2]
    d_mem = task[2] + task[3]
    r_cpu, r_mem = resource

    if d_mem > r_mem:
        return float('inf')
        
    return d_cpu / r_cpu

def estimate_candidate_paths( task, paths ):
    for path in paths:
        latency = estimate_data_transfer_latency(task, path)
        

class ManagerApp:
    network_graph = None

    def __init__(self):
        self. CONTROLLER_IP   = '127.0.0.1'
        self. CONTROLLER_PORT = '8080'
        self. controller_url  = f'http://{self.CONTROLLER_IP}:{self.CONTROLLER_PORT}'

        self. devices = None # map < device id#, ip address >
        self. servers = None # map < server id#, ip address >

        self. priority_table = None # map < device id#, priority >
        self. resource_table = None # map < server id#, tuple < CPU, MEM > >

        self. device_task_table = None # map < device id#, list <tasks> >
        self. server_task_table = None # map < server id#, list <tasks> >

    def retrieve_network_graph( self ):
        self. network_graph = NetworkGraph()
        self. network_graph. create_topo( )

    def retrieve_host_info( self ):
        self. devices = {}
        self. servers = {}
        for host in self. network_graph.parsed_hosts:
            # send HTTP 'status request' message to host
            reply = {}# reply should contain device class and relevant information
            if reply['class'] == 'device':
                self. devices[ reply['id'] ] = host['ipv4']
                self. priority_table[ reply['id'] ] = reply['priority']
            if reply['class'] == 'server':
                self. servers[ reply['id'] ] = host['ipv4']
                self. resource_table[ reply['id'] ] = ( reply['cpu'], reply['mem'] )

    def retrieve_device_task_table( self ):
        self. device_task_table = {}
        for d_id in self. devices:
            # send HTTP 'task list request' message to self. devices[d_id]
            reply = []# HTTP response is list of tasks the device is waiting for
            self. device_task_table[d_id] = reply
            
    def retrieve_server_task_table( self ):
        self. server_task_table = {}
        for s_id in self. servers:
            # send HTTP 'task list request' message to self. servers[s_id]
            reply = []# HTTP response is list of task the server is assigned for
            self. server_task_table[s_id] = reply

    def update_network_state( self ):
        self. retrieve_network_graph( )
        self. retrieve_host_info( )
        self. retrieve_device_task_table( )
        self. retrieve_server_task_table( )
    
    def estimate_candidate_servers( self, device_id, task ):
        candidate_servers = { } # map < server id#, tuple < latency, path > >
        
        for s_id in self. servers:
            candidate_paths = []# find all candidate paths between self. devices[device_id] and self. servers[s_id]
            # estimate data transfer latency up and down stream

            latencies = []
            for path in candidate_paths:
                latencies. append(0.0)
                latencies[-1] += estimate_data_transfer_latency( task, path )
                latencies[-1] += estimate_task_processing_latency( task, self. resource_table[s_id] )

            if min( latencies ) <= task[-1]:
                latency = min(latencies)
                path = candidate_paths[ latencies. index(latency) ]
                candidate_servers[s_id] = ( latency, path )
        
        return candidate_servers



'''
ManagerApp side:
    Status request:
        POST: https://<ip>:<port>/status_request
        Data: json object { id = <number>, ip = <address of manager application >

Device side:
    Status reply:
        Data: json object { class = 'device', id = <device id#>, priority = <device priority> }

Server(MEC) size:
    Status reply:
        Data: json object { class = 'server', id = <server id#>, cpu = <cpu cyles per sec>, mem = <memory> }
'''

'''
ManagerApp side:
    Task list request:
        POST: https://<ip>:<port>/task_list_request

Device side:
    Task list reply:
        Data: json object { 0 = <task1>, 1 = <task2>, ..., n = <taskn> } // list of tasks the device is wigting for

Device side:
    Task list reply:
        Data json object { 0 = <task1>, 1 = <task2>, ..., n = <taskn> } // list of tasks the server is assigned

'''


'''
Device side:
    Resource request:
        Post: http://<manager application url>/resource_request
        Data: json object for task { d_id = <device id#>, t_id = <task id#>, input_data_size, output_data_size, cpu_cycles, memory }

ManagerApp side:
    Resource reply:
        Data: json object { server_address }
'''
