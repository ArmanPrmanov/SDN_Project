from mininet.cli import CLI
import networkx as nx
from test_topo import TestTopo

# Define the controller's IP and port (assuming it's running locally)
CONTROLLER_IP = "127.0.0.1"
CONTROLLER_PORT = "8080"
BASE_URL = f"http://{CONTROLLER_IP}:{CONTROLLER_PORT}"
SWITCH_PROTOCOL = 'OpenFlow13'


class CustomCLI(CLI):
    """Custom Mininet CLI to add commands for showing paths."""
    
    def __init__(self, topo):
        """Initialize with the graph and hosts."""
        self.topo = topo
        CLI.__init__(self, topo.net)

    def do_show_shortest_path(self, line):
        """Command to show the shortest path between specified host indices."""
        if not line.strip():
            print("Please provide source and destination node indices.")
            return
        
        try:
            src_index, dst_index = map(int, line.split())
            src_host = self.topo.hosts[src_index]
            dst_host = self.topo.hosts[dst_index]
        except (ValueError, IndexError):
            print("Invalid indices provided. Please enter valid host indices.")
            return

        # Calculate the shortest path between the specified hosts
        try:
            path = nx.shortest_path(self.topo.G, source=src_host, target=dst_host)
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
            src_host = self.topo.hosts[src_index]
            dst_host = self.topo.hosts[dst_index]
        except (ValueError, IndexError):
            print("Invalid indices provided. Please enter valid host indices.")
            return

        # Calculate all simple paths between the specified hosts
        try:
            all_paths = list(nx.all_simple_paths(self.topo.G, source=src_host, target=dst_host))
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
            src_host = self.topo.hosts[src_index]
            dst_host = self.topo.hosts[dst_index]
        except (ValueError, IndexError):
            print("Invalid indices provided. Please enter valid host indices.")
            return

        all_paths = self.topo.get_all_paths(src_host, dst_host)
        print(f'{all_paths=}')
        for path in all_paths:
            cost = self.topo.get_path_tot_cost(path)
            print(f"Path: {path} | Total Cost: {cost}")



class Framework:
    def start_test_topo(self):
        test_topo = TestTopo()
        test_topo.init_test_topo()

    def main(self):
        self.start_test_topo()

        # topo = NetworkGraph(controller_ip=CONTROLLER_IP, controller_port=CONTROLLER_PORT)
        # topo.create_topo()
        # topo.enable_statistics()
        #
        # # Use the custom CLI with additional commands
        # custom_cli = CustomCLI(topo)
        # custom_cli.run()


if __name__ == "__main__":
    framework = Framework()
    framework.main()

