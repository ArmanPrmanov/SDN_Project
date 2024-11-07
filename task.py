import random

class Task:
    def __init__(self, task_id):
        self.task_id = task_id
        self.cpu_cycles = random.randint(50, 1000)
        self.memory = random.randint(10, 1000)

    def __repr__(self):
        return f"Task(id={self.task_id}, cpu_cycles={self.cpu_cycles}, memory={self.memory}"

