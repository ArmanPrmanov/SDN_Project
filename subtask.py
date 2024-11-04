import random

class Subtask:
    def __init__(self, subtask_id):
        self.subtask_id = subtask_id
        self.cpu_cycles = random.randint(50, 1000)

    def __repr__(self):
        return f"Subtask(id={self.subtask_id}, cpu_cycles={self.cpu_cycles})"
