from typing import Dict, Optional

class TaskManager:
    def __init__(self):
        self.tasks: Dict[int, Dict[str, str]] = {}

    def add_task(self, task_id: int, title: str, description: str, status: str) -> bool:
        """
        Add a new task to the task manager.
        
        :param task_id: The ID of the task.
        :param title: The title of the task.
        :param description: The description of the task.
        :param status: The initial status of the task.
        :return: True if the task was added successfully, False otherwise.
        """
        if task_id in self.tasks:
            return False
        self.tasks[task_id] = {
            'id': task_id,
            'title': title,
            'description': description,
            'status': status
        }
        return True

    def remove_task(self, task_id: int) -> bool:
        """
        Remove a task from the task manager.
        
        :param task_id: The ID of the task to remove.
        :return: True if the task was removed successfully, False otherwise.
        """
        if task_id not in self.tasks:
            return False
        del self.tasks[task_id]
        return True

    def update_task(self, task_id: int, title: Optional[str] = None, description: Optional[str] = None, status: Optional[str] = None) -> bool:
        """
        Update the details of a task.
        
        :param task_id: The ID of the task to update.
        :param title: The new title of the task (optional).
        :param description: The new description of the task (optional).
        :param status: The new status of the task (optional).
        :return: True if the task was updated successfully, False otherwise.
        """
        if task_id not in self.tasks:
            return False
        if title is not None:
            self.tasks[task_id]['title'] = title
        if description is not None:
            self.tasks[task_id]['description'] = description
        if status is not None:
            self.tasks[task_id]['status'] = status
        return True

    def get_task(self, task_id: int) -> Optional[Dict[str, str]]:
        """
        Retrieve a task by its ID.
        
        :param task_id: The ID of the task to retrieve.
        :return: The task details as a dictionary, or None if the task does not exist.
        """
        return self.tasks.get(task_id)