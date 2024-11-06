from mininet.cli import CLI
from NetworkGraph import NetworkGraph
from AppServer import AppServerHandler
import networkx as nx
import requests
from http.server import HTTPServer
import json
import threading

# Define the controller's IP and port (assuming it's running locally)
CONTROLLER_IP = "127.0.0.1"
CONTROLLER_PORT = "8080"
BASE_URL = f"http://{CONTROLLER_IP}:{CONTROLLER_PORT}"
SWITCH_PROTOCOL = 'OpenFlow13'


class CustomCLI(CLI):
    """Custom Mininet CLI to add commands for showing paths."""
    
    def __init__(self, net, graph, hosts, topo):
        """Initialize with the graph and hosts."""
        self.graph = graph
        self.hosts = hosts
        self.topo = topo
        CLI.__init__(self, net)

    def do_show_shortest_path(self, line):
        """Command to show the shortest path between specified host indices."""
        if not line.strip():
            print("Please provide source and destination node indices.")
            return
        
        try:
            src_index, dst_index = map(int, line.split())
            src_host = self.hosts[src_index]
            dst_host = self.hosts[dst_index]
        except (ValueError, IndexError):
            print("Invalid indices provided. Please enter valid host indices.")
            return

        # Calculate the shortest path between the specified hosts
        try:
            path = nx.shortest_path(self.graph, source=src_host, target=dst_host)
            print("Shortest path:", path)
        except nx.NetworkXNoPath:
            print(f"No path found between {src_host} and {dst_host}.")

    def do_show_all_paths(self, line):
        """Command to show all paths between specified host indices."""
        if not line.strip():
            print("Please provide source and destination node indices.")
            return
        
        try:
            src_index, dst_index = map(int, line.split())
            src_host = self.hosts[src_index]
            dst_host = self.hosts[dst_index]
        except (ValueError, IndexError):
            print("Invalid indices provided. Please enter valid host indices.")
            return

        # Calculate all simple paths between the specified hosts
        try:
            all_paths = list(nx.all_simple_paths(self.graph, source=src_host, target=dst_host))
            if not all_paths:
                print(f"No paths found between {src_host} and {dst_host}.")
            else:
                for path in all_paths:
                    print("Path:", path)
        except nx.NetworkXNoPath:
            print("No path found between the hosts.")
            
    def do_test(self):
        src_switch = "<Docker d100: d100-eth0:10.0.0.1 pid=14611>"
        src_name = str(src_switch).split(':')[0].split()[1]
        print(f"{src_name=}")
            
    def do_get_all_costs(self, line):
        """Get the cost of all paths between two hosts."""
        if not line.strip():
            print("Please provide source and destination host indices.")
            return

        try:
            src_index, dst_index = map(int, line.split())
            src_host = self.hosts[src_index]
            dst_host = self.hosts[dst_index]
        except (ValueError, IndexError):
            print("Invalid indices provided. Please enter valid host indices.")
            return

        all_paths = self.get_all_paths(src_host, dst_host)
        print(f'{all_paths=}')
        for path in all_paths:
            cost = self.get_path_tot_cost(path)
            print(f"Path: {path} | Total Cost: {cost}")
            
    
    def get_all_paths(self, src_host, dst_host):
        return list(nx.all_simple_paths(self.graph, source=src_host, target=dst_host))

    def get_path_tot_cost(self, path):
        total_cost = 0
        links = self.get_links(path)
        print(f'{links=}')
        for link in links:
            switch_dpid = link['src_switch']
            port_id = link['src_port']
            total_cost += self.topo.get_cost(switch_dpid, port_id)
        return total_cost
        
    def get_links(self, path):
        links = []
        print(f"parsed_links:\n{self.topo.parsed_links}")
        print(f"switches:\n{self.topo.switches}")
        print(f"parsed_switches:\n{self.topo.parsed_switches}")
        
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
        for link in self.topo.parsed_links:
            if link['src_switch'] == self.get_switch_dpid_by_name(src_name) and link['dst_switch'] == self.get_switch_dpid_by_name(dst_name):
                return link
        return None  # Return None if no link is found

    def get_switch_dpid_by_name(self, name):
        print(f"get_switch_dpid for {name=}")
        ss = self.topo.switches
        for i in range(0, len(ss)):
            if ss[i].name == name:
                return self.topo.parsed_switches[i]['switch_dpid']

        return None


class Framework():
    def start_server(self):
        AppServerHandler.MyParser = self
        server_address = ('127.0.0.1', 8000)
        httpd = HTTPServer(server_address, AppServerHandler)
        print(f"Starting AppServer")
        httpd.serve_forever()


    def main(self):
        # Start the server in a separate thread
        server_thread = threading.Thread(target=self.start_server)
        server_thread.daemon = True  # Daemonize thread to stop with main program
        server_thread.start()
        print("AppServer started in background.")

        topo = NetworkGraph(controller_ip=CONTROLLER_IP, controller_port=CONTROLLER_PORT)
        topo.create_topo()
        topo.enable_statistics()
        
        net = topo.net
        hosts = topo.hosts
        switches = topo.switches
        
        parsed_hosts = topo.parsed_hosts
        
        # Build the network graph using NetworkX
        G = nx.Graph()
        for link in net.links:
            src = link.intf1.node
            dst = link.intf2.node
            G.add_edge(src, dst)
        
        # Use the custom CLI with additional commands
        custom_cli = CustomCLI(net, G, hosts, topo)
        custom_cli.run()


if __name__ == "__main__":
    framework = Framework()
    framework.main()

