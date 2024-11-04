import networkx as nx
import matplotlib.pyplot as plt
import random

def generate_dag(num_nodes):
    if num_nodes < 2:
        raise ValueError("The number of nodes should be at least 2 to form a meaningful DAG.")

    # Create a directed graph
    dag = nx.DiGraph()

    # Add nodes to the graph
    for i in range(1, num_nodes + 1):
        dag.add_node(i)

    # Add edges to ensure it's a DAG with strict ID ordering
    for i in range(2, num_nodes):

        if random.random() < 0.5:
            one_children = []
            for j in range(1, i):
                out_degree = dag.out_degree(j)
                if out_degree == 1:
                    one_children.append(j)
            if len(one_children) > 0:
                parent_node_idx = random.randint(0, len(one_children) - 1)
                dag.add_edge(one_children[parent_node_idx], i)

        no_children = []
        for j in range(1, i):
            out_degree = dag.out_degree(j)
            if out_degree == 0:
                no_children.append(j)
        if len(no_children) > 0:
            parent_node_idx = random.randint(0, len(no_children) - 1)
            dag.add_edge(no_children[parent_node_idx], i)

    # Connect all leave nodes to the end node
    last_node_idx = num_nodes
    for j in range(1, num_nodes):
        out_degree = dag.out_degree(j)
        if out_degree == 0:
            dag.add_edge(j, last_node_idx)

    return dag

# Parameters for DAG generation
num_nodes = 10
dag = generate_dag(num_nodes)

# Draw the DAG
pos = nx.spring_layout(dag)
nx.draw(dag, pos, with_labels=True, node_size=700, node_color='lightblue', arrowsize=20)
plt.title("Generated Directed Acyclic Graph")
plt.show()
