from mininet.net import Mininet
from mininet.node import OVSSwitch, RemoteController
from mininet.log import info

import networkx as nx
import requests
import json

class NetworkGraph:
    def __init__(self, controller_ip="127.0.0.1", controller_port="8080"):
        self.CONTROLLER_IP = controller_ip
        self.CONTROLLER_PORT = controller_port
        self.BASE_URL = f"http://{self.CONTROLLER_IP}:{self.CONTROLLER_PORT}"

        self.NEW_IP = "127.0.0.2"
        self.NEW_PORT = "8080"
        
        self.SWITCH_PROTOCOL = 'OpenFlow13'
        
        self.net = None
        self.hosts = []
        self.switches = []
        
        self.parsed_hosts = []
        self.parsed_links = []
        self.parsed_switches = []

        self.G = nx.Graph()

    def fetch_hosts(self):
        hosts_url = f"{self.BASE_URL}/wm/device/"
        response = requests.get(hosts_url)
        hosts = response.json()

        return hosts['devices']
        
    def fetch_switches(self):
        switches_url = f"{self.BASE_URL}/wm/core/controller/switches/json"
        switches_response = requests.get(switches_url)
        switches = switches_response.json()
        
        return switches

    def fetch_links(self):
        links_url = f"{self.BASE_URL}/wm/topology/links/json"
        links_response = requests.get(links_url)
        links = links_response.json()
        
        return links
        
    def enable_statistics(self):
        url = f"{self.BASE_URL}/wm/statistics/config/enable/json"
        requests.post(url, json='')
        
    def get_statistics(self, switchId, portId):
        url = f"{self.BASE_URL}/wm/statistics/bandwidth/{switchId}/{portId}/json"
        response = requests.get(url)
        
        return response
        
    #def get_switchId_portId
    #def get_link    #btwn 2 switches
    #def get_links    #along path
    #def get_path_tot_cost
    #def get_all_paths
    #def get_path_min_cost
        
    def get_cost(self, switchId, portId):
        port_stats = self.get_statistics(switchId, portId).json()
        print(f"stats:\n {port_stats}")
        if port_stats == [None]:
            print(f"port_stats is [None]")
            return 0
                
        tx = int(port_stats[0]['bits-per-second-tx'])
        rx = int(port_stats[0]['bits-per-second-rx'])
        
        cost = tx - rx
        return cost
        

    def parse_hosts(self):
        hosts = self.fetch_hosts()
        recreated_hosts = []

        for host in hosts:
            if len(host['attachmentPoint']) == 0:
                continue
            mac = host['mac'][0]
            ipv4 = host['ipv4'][0] if host['ipv4'] else None
            ipv6 = host['ipv6'][0] if host['ipv6'] else None
            attachment_point = host['attachmentPoint'][0] if host['attachmentPoint'] else None
            attached_switch = attachment_point['switch'] if attachment_point else ''
            attached_port = attachment_point['port'] if attachment_point else ''

            recreated_hosts.append({
                'mac': mac,
                'ipv4': ipv4,
                'ipv6': ipv6,
                'switch': attached_switch,
                'port': attached_port
            })
        return recreated_hosts
        
    def parse_switches(self):
        switches = self.fetch_switches()
        recreated_switches = []

        for switch in switches:
            inet_address = switch['inetAddress'].split('/')[1]
            connected_since = switch['connectedSince']
            openflow_version = switch['openFlowVersion']
            switch_dpid = switch['switchDPID']

            # Simulate the switch creation based on gathered information
            recreated_switches.append({
                'inet_address': inet_address,
                'connected_since': connected_since,
                'openflow_version': openflow_version,
                'switch_dpid': switch_dpid
            })

        return recreated_switches
        
    def parse_links(self):
        fetched_links = self.fetch_links()
        links = []
        
        for l in fetched_links:
            src_switch = l['src-switch']
            src_port = l['src-port']
            dst_switch = l['dst-switch']
            dst_port = l['dst-port']
            latency = l['latency']
            link_type = l['type']
            direction = l['direction']
            
            links.append({
                'src_switch': src_switch,
                'src_port': src_port,
                'dst_switch': dst_switch,
                'dst_port': dst_port,
                'link_type': link_type,
                'direction': direction,
                'latency': latency
            })
        
        return links
        
    def create_topo(self):
        fetched_hosts = self.parse_hosts()
        print("Get Hosts:")
        print(json.dumps(fetched_hosts, indent=4))
        self.parsed_hosts = fetched_hosts
        
        fetched_switches = self.parse_switches()
        print("\Get Switches:")
        print(json.dumps(fetched_switches, indent=4))
        self.parsed_switches = fetched_switches
        
        fetched_links = self.parse_links()
        print("\Get Links:")
        print(json.dumps(fetched_links, indent=4))
        self.parsed_links = fetched_links

        info('Creating Network \n')
        self.net = Mininet(controller=RemoteController, switch=OVSSwitch)
        
        info('Adding Controller \n')
        c0 = self.net.addController('c0', ip=self.CONTROLLER_IP)
        
        info('Adding Hosts \n')
        for i in range(0, len(fetched_hosts)):
            h = self.net.addHost(f'd{i+100}', ip=fetched_hosts[i]['ipv4'], dimage="ubuntu:trusty", cpu_shares=20) #cls=DOCKER
            self.hosts.append(h)
            
        info('Adding Switches \n')
        for i in range(0, len(fetched_switches)):
            s = self.net.addSwitch(f's{i+100}', protocols=self.SWITCH_PROTOCOL)
            self.switches.append(s)
        
        info('Adding HSLinks \n')
        for i in range(0, len(fetched_hosts)):
            f_h = fetched_hosts[i]
            s_to_connect = self.get_switch_idx_by_id(self.switches, fetched_switches, f_h['switch'])
            if s_to_connect is None:
                print(f'Can\'t find switch of host[{i}]')
                continue
            #print(f"h: {hosts[i].name} connects to switch: {switches[s_to_connect].name} via port: {int(f_h['port'])}")
            self.net.addLink(self.hosts[i], self.switches[s_to_connect], port=int(f_h['port']))
            
        info('Adding SSLinks \n')
        for i in range(0, len(fetched_links)):
            f_l = fetched_links[i]
            src_switch = self.get_switch_idx_by_id(self.switches, fetched_switches, f_l['src_switch'])
            dst_switch = self.get_switch_idx_by_id(self.switches, fetched_switches, f_l['dst_switch'])
            #print(f"{switches[src_switch].name}:{f_l['src_port']} connects to {switches[dst_switch].name}:{f_l['dst_port']}")
            if src_switch == -1 or dst_switch == -1:
                print(f"Error occurred: switch idx-s are {src_switch}, {dst_switch}")
            self.net.addLink(self.switches[src_switch], self.switches[dst_switch],
                        port1=int(f_l['src_port']), port2=int(f_l['dst_port']))

        info('Building NX Graph \n')
        self.build_nx_graph()

        info('Starting Network \n')
        for s in self.switches:
            s.start([c0])

    def build_nx_graph(self):
        # Build the network graph using NetworkX
        self.G = nx.Graph()
        for link in self.net.links:
            src = link.intf1.node
            dst = link.intf2.node
            self.G.add_edge(src, dst)

    def get_all_paths(self, src_host, dst_host):
        return list(nx.all_simple_paths(self.G, source=src_host, target=dst_host))

    def get_path_tot_cost(self, path):
        total_cost = 0
        links = self.get_links(path)
        print(f'{links=}')
        for link in links:
            switch_dpid = link['src_switch']
            port_id = link['src_port']
            total_cost += self.get_cost(switch_dpid, port_id)
        return total_cost

    def get_links(self, path):
        links = []
        print(f"parsed_links:\n{self.parsed_links}")
        print(f"switches:\n{self.switches}")
        print(f"parsed_switches:\n{self.parsed_switches}")

        for i in range(len(path) - 1):
            link = self.get_link(path[i], path[i + 1])
            if link:
                links.append(link)
        return links

    def get_link(self, src_switch, dst_switch):
        src_name = str(src_switch).split(':')[0].split()[-1]
        dst_name = str(dst_switch).split(':')[0].split()[-1]
        print(f"from {src_name=} to {dst_name=}")

        # Parse the fetched links to find the link between src_switch and dst_switch
        for link in self.parsed_links:
            if link['src_switch'] == self.get_switch_dpid_by_name(src_name) and link[
                'dst_switch'] == self.get_switch_dpid_by_name(dst_name):
                return link
        return None  # Return None if no link is found

    def get_switch_dpid_by_name(self, name):
        print(f"get_switch_dpid for {name=}")
        ss = self.switches
        for i in range(0, len(ss)):
            if ss[i].name == name:
                return self.parsed_switches[i]['switch_dpid']

        return None
        
    @staticmethod
    def get_switch_idx_by_id(switches, fetched_switches, dpid):
        for i in range(0, len(switches)):
            if fetched_switches[i]['switch_dpid'] == dpid:
                return i
        return None

