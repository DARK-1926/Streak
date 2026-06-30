from typing import Dict, List, Optional

class KanbanBoard:
    def __init__(self):
        self.board: Dict[str, List[int]] = {
            'To Do': [],
            'In Progress': [],
            'Done': []
        }
        self.tasks: Dict[int, Dict[str, str]] = {}

    def create_task(self, title: str, description: str) -> int:
        """
        Create a new task and add it to the 'To Do' column.
        
        :param title: The title of the task.
        :param description: The description of the task.
        :return: The ID of the created task.
        """
        task_id = len(self.tasks) + 1
        self.tasks[task_id] = {
            'id': task_id,
            'title': title,
            'description': description,
            'status': 'To Do'
        }
        self.board['To Do'].append(task_id)
        return task_id

    def move_task(self, task_id: int, new_status: str) -> None:
        """
        Move a task from its current status to a new status.
        
        :param task_id: The ID of the task to move.
        :param new_status: The new status for the task.
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} does not exist.")
        
        old_status = self.tasks[task_id]['status']
        if old_status == new_status:
            return
        
        self.board[old_status].remove(task_id)
        self.board[new_status].append(task_id)
        self.tasks[task_id]['status'] = new_status

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None) -> None:
        """
        Update the title or description of a task.
        
        :param task_id: The ID of the task to update.
        :param title: The new title of the task (optional).
        :param description: The new description of the task (optional).
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} does not exist.")
        
        if title is not None:
            self.tasks[task_id]['title'] = title
        if description is not None:
            self.tasks[task_id]['description'] = description

    def get_task(self, task_id: int) -> Dict[str, str]:
        """
        Retrieve a task by its ID.
        
        :param task_id: The ID of the task to retrieve.
        :return: The task details.
        """
        if task_id not in self.tasks:
            raise ValueError(f"Task with ID {task_id} does not exist.")
        
        return self.tasks[task_id]

    def get_board(self) -> Dict[str, List[int]]:
        """
        Retrieve the current state of the board.
        
        :return: A dictionary representing the board.
        """
        return self.board