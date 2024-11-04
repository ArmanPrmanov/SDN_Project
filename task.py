from subtask import Subtask

import networkx as nx
import random

class Task:
    def __init__(self, task_id):
        self.task_id = task_id
        self.subtasks = []
        self.dependencies = {}  # Subtask dependencies represented by a DAG

        num_nodes = random.randint(2, 10)
        dag = self._generate_dag(num_nodes)
        self._populate_subtasks_and_dependencies(dag)

    def add_subtask(self, subtask):
        self.subtasks.append(subtask)
        self.dependencies[subtask.subtask_id] = []

    def add_dependency(self, from_subtask, to_subtask):
        self.dependencies[from_subtask.subtask_id].append(to_subtask.subtask_id)

    def _generate_dag(self, num_nodes):
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

        import matplotlib.pyplot as plt
        nx.draw(dag, with_labels=True)
        plt.show()

        return dag

    def _populate_subtasks_and_dependencies(self, dag):
        # Create subtasks corresponding to each node in the DAG
        for node in dag.nodes():
            subtask = Subtask(subtask_id=node)
            self.add_subtask(subtask)

        # Create dependencies based on the edges in the DAG
        for from_node, to_node in dag.edges():
            self.add_dependency(self.subtasks[from_node - 1], self.subtasks[to_node - 1])

    def __repr__(self):
        return (f"Task(id={self.task_id},\n\t subtasks={self.subtasks},\n\t "
                f"dependencies={self.dependencies})")


if __name__ == "__main__":
    task = Task(task_id=1)
    print(task)
