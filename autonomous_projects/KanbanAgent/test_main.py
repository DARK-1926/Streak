import unittest
from kanban_board import KanbanBoard
from task_manager import TaskManager


class TestKanbanBoard(unittest.TestCase):
    def setUp(self):
        self.board = KanbanBoard()

    def test_create_task(self):
        task_id = self.board.create_task("Test Task", "Test Description")
        self.assertEqual(task_id, 1)
        self.assertIn(1, self.board.board['To Do'])
        self.assertEqual(self.board.tasks[1]['title'], "Test Task")
        self.assertEqual(self.board.tasks[1]['description'], "Test Description")
        self.assertEqual(self.board.tasks[1]['status'], "To Do")

    def test_move_task_valid(self):
        task_id = self.board.create_task("Move Test", "Moving task")
        self.board.move_task(task_id, "In Progress")
        self.assertNotIn(task_id, self.board.board['To Do'])
        self.assertIn(task_id, self.board.board['In Progress'])
        self.assertEqual(self.board.tasks[task_id]['status'], "In Progress")

    def test_move_task_invalid_task_id(self):
        with self.assertRaises(ValueError) as context:
            self.board.move_task(999, "Done")
        self.assertIn("Task with ID 999 does not exist.", str(context.exception))

    def test_move_task_same_status(self):
        task_id = self.board.create_task("No-op Move", "No change")
        old_to_do = self.board.board['To Do'][:]
        self.board.move_task(task_id, "To Do")
        self.assertEqual(self.board.board['To Do'], old_to_do)
        self.assertEqual(self.board.tasks[task_id]['status'], "To Do")

    def test_update_task(self):
        task_id = self.board.create_task("Update Me", "Old desc")
        self.board.update_task(task_id, title="Updated Title", description="New desc")
        task = self.board.get_task(task_id)
        self.assertEqual(task['title'], "Updated Title")
        self.assertEqual(task['description'], "New desc")

    def test_update_task_partial(self):
        task_id = self.board.create_task("Partial Update", "Initial desc")
        self.board.update_task(task_id, title="Renamed")
        task = self.board.get_task(task_id)
        self.assertEqual(task['title'], "Renamed")
        self.assertEqual(task['description'], "Initial desc")

    def test_get_task(self):
        task_id = self.board.create_task("Fetch Me", "For retrieval")
        task = self.board.get_task(task_id)
        self.assertEqual(task['id'], task_id)
        self.assertEqual(task['title'], "Fetch Me")
        self.assertEqual(task['description'], "For retrieval")
        self.assertEqual(task['status'], "To Do")

    def test_get_task_not_found(self):
        with self.assertRaises(ValueError) as context:
            self.board.get_task(999)
        self.assertIn("Task with ID 999 does not exist.", str(context.exception))

    def test_get_board(self):
        task1 = self.board.create_task("Task 1", "First")
        task2 = self.board.create_task("Task 2", "Second")
        board_state = self.board.get_board()
        self.assertEqual(len(board_state['To Do']), 2)
        self.assertIn(task1, board_state['To Do'])
        self.assertIn(task2, board_state['To Do'])
        self.assertEqual(board_state['In Progress'], [])
        self.assertEqual(board_state['Done'], [])


class TestTaskManager(unittest.TestCase):
    def setUp(self):
        self.tm = TaskManager()

    def test_add_task_success(self):
        result = self.tm.add_task(1, "Add Test", "Added task", "To Do")
        self.assertTrue(result)
        self.assertIn(1, self.tm.tasks)
        self.assertEqual(self.tm.tasks[1]['title'], "Add Test")
        self.assertEqual(self.tm.tasks[1]['status'], "To Do")

    def test_add_task_duplicate_id(self):
        self.tm.add_task(1, "First", "Desc", "To Do")
        result = self.tm.add_task(1, "Duplicate", "Ignored", "In Progress")
        self.assertFalse(result)
        self.assertEqual(self.tm.tasks[1]['title'], "First")

    def test_remove_task_success(self):
        self.tm.add_task(1, "To Remove", "Gone soon", "Done")
        result = self.tm.remove_task(1)
        self.assertTrue(result)
        self.assertNotIn(1, self.tm.tasks)

    def test_remove_task_not_found(self):
        result = self.tm.remove_task(999)
        self.assertFalse(result)

    def test_update_task_success(self):
        self.tm.add_task(1, "Orig", "Original", "To Do")
        result = self.tm.update_task(1, title="Updated", description="New desc", status="Done")
        self.assertTrue(result)
        task = self.tm.get_task(1)
        self.assertEqual(task['title'], "Updated")
        self.assertEqual(task['description'], "New desc")
        self.assertEqual(task['status'], "Done")

    def test_update_task_partial(self):
        self.tm.add_task(1, "Partial", "Desc", "To Do")
        result = self.tm.update_task(1, title="Renamed")
        self.assertTrue(result)
        task = self.tm.get_task(1)
        self.assertEqual(task['title'], "Renamed")
        self.assertEqual(task['description'], "Desc")

    def test_update_task_not_found(self):
        result = self.tm.update_task(999, title="Nope")
        self.assertFalse(result)

    def test_get_task_found(self):
        self.tm.add_task(1, "Get Me", "Retrievable", "In Progress")
        task = self.tm.get_task(1)
        self.assertIsNotNone(task)
        self.assertEqual(task['title'], "Get Me")

    def test_get_task_not_found(self):
        task = self.tm.get_task(999)
        self.assertIsNone(task)


if __name__ == '__main__':
    unittest.main()