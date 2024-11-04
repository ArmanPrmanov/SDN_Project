from mininet.net import Mininet
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from MyTopo import MyTopo

import networkx as nx

# Define the controller's IP and port (assuming it's running locally)
CONTROLLER_IP = "127.0.0.1"
CONTROLLER_PORT = "8080"
BASE_URL = f"http://{CONTROLLER_IP}:{CONTROLLER_PORT}"
SWITCH_PROTOCOL = 'OpenFlow13'


class CustomCLI(CLI):
    """Custom Mininet CLI to add commands for showing paths."""
    
    def __init__(self, net, graph, hosts):
        """Initialize with the graph and hosts."""
        self.graph = graph
        self.hosts = hosts
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


def main():
    topo = MyTopo(controller_ip=CONTROLLER_IP, controller_port=CONTROLLER_PORT)

    topo.create_topo()
    
    net = topo.net
    hosts = topo.hosts
    switches = topo.switches
    
    net.start()
    
    # Build the network graph using NetworkX
    G = nx.Graph()
    for link in net.links:
        src = link.intf1.node
        dst = link.intf2.node
        G.add_edge(src, dst)
    
    # Use the custom CLI with additional commands
    custom_cli = CustomCLI(net, G, hosts)
    custom_cli.run()

    net.stop()

if __name__ == "__main__":
    main()

