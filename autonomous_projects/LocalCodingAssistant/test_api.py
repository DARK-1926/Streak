```python
import pytest
import requests
from unittest.mock import Mock, patch, MagicMock
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api import app, db, User, Task


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def test_user():
    """Create a test user for authentication tests."""
    user = User(username='testuser', email='test@example.com')
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def auth_header(test_user):
    """Create an authorization header with a valid token."""
    token = test_user.generate_token()
    return {'Authorization': f'Bearer {token}'}


class TestUserRegistration:
    """Test cases for user registration endpoint."""
    
    def test_register_user_success(self, client):
        """Test successful user registration."""
        response = client.post('/api/register', 
            data=json.dumps({
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'securepassword123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'id' in data
        assert data['username'] == 'newuser'
        assert data['email'] == 'newuser@example.com'
    
    def test_register_user_missing_fields(self, client):
        """Test registration with missing required fields."""
        response = client.post('/api/register',
            data=json.dumps({
                'username': 'newuser'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_register_user_duplicate_email(self, client, test_user):
        """Test registration with duplicate email."""
        response = client.post('/api/register',
            data=json.dumps({
                'username': 'anotheruser',
                'email': 'test@example.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 409
        data = json.loads(response.data)
        assert 'error' in data


class TestUserLogin:
    """Test cases for user login endpoint."""
    
    def test_login_success(self, client, test_user):
        """Test successful login."""
        response = client.post('/api/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert 'user' in data
    
    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password."""
        response = client.post('/api/login',
            data=json.dumps({
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user."""
        response = client.post('/api/login',
            data=json.dumps({
                'email': 'nonexistent@example.com',
                'password': 'password123'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data


class TestTaskManagement:
    """Test cases for task management endpoints."""
    
    def test_create_task_success(self, client, auth_header):
        """Test successful task creation."""
        response = client.post('/api/tasks',
            data=json.dumps({
                'title': 'Test Task',
                'description': 'This is a test task',
                'completed': False
            }),
            content_type='application/json',
            headers=auth_header
        )
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['title'] == 'Test Task'
        assert data['description'] == 'This is a test task'
        assert data['completed'] is False
    
    def test_create_task_unauthorized(self, client):
        """Test task creation without authentication."""
        response = client.post('/api/tasks',
            data=json.dumps({
                'title': 'Test Task',
                'description': 'This is a test task'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_get_tasks_success(self, client, auth_header, test_user):
        """Test retrieving all tasks."""
        # Create a task first
        task = Task(title='Test Task', user_id=test_user.id)
        db.session.add(task)
        db.session.commit()
        
        response = client.get('/api/tasks', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) > 0
    
    def test_get_task_by_id_success(self, client, auth_header, test_user):
        """Test retrieving a specific task by ID."""
        task = Task(title='Test Task', user_id=test_user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
        response = client.get(f'/api/tasks/{task_id}', headers=auth_header)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == task_id
        assert data['title'] == 'Test Task'
    
    def test_get_task_not_found(self, client, auth_header):
        """Test retrieving a non-existent task."""
        response = client.get('/api/tasks/99999', headers=auth_header)
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_task_success(self, client, auth_header, test_user):
        """Test updating a task."""
        task = Task(title='Original Title', user_id=test_user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
        response = client.put(f'/api/tasks/{task_id}',
            data=json.dumps({
                'title': 'Updated Title',
                'completed': True
            }),
            content_type='application/json',
            headers=auth_header
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['title'] == 'Updated Title'
        assert data['completed'] is True
    
    def test_delete_task_success(self, client, auth_header, test_user):
        """Test deleting a task."""
        task = Task(title='Task to Delete', user_id=test_user.id)
        db.session.add(task)
        db.session.commit()
        task_id = task.id
        
        response = client.delete(f'/api/tasks/{task_id}', headers=auth_header)
        
        assert response.status_code == 204
        
        # Verify task is deleted
        deleted_task = Task.query.get(task_id)
        assert deleted_task is None


class TestErrorHandling:
    """Test cases for error handling."""
    
    def test_404_error(self, client):
        """Test 404 error response."""
        response = client.get('/api/nonexistent')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_400_bad_request(self, client):
        """Test 400 bad request response."""
        response = client.post('/api/login',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_method_not_allowed(self, client):
        """Test method not allowed response."""
        response = client.delete('/api/register')
        
        assert response.status_code == 405


class TestInputValidation:
    """Test cases for input validation."""
    
    def test_invalid_json(self, client):
        """Test handling of invalid JSON."""
        response = client.post('/api/register',
            data='not valid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_empty_request_body(self, client):
        """Test handling of empty request body."""
        response = client.post('/api/register',
            data=None,
            content_type='application/json'
        )
        
        assert response.status_code == 400


class TestAuthentication:
    """Test cases for authentication and authorization."""
    
    def test_protected_endpoint_without_token(self, client):
        """Test accessing protected endpoint without token."""
        response = client.get('/api/tasks')
        
        assert response.status_code == 401
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test accessing protected endpoint with invalid token."""
        headers = {'Authorization': 'Bearer invalid_token'}
        response = client.get('/api/tasks', headers=headers)
        
        assert response.status_code == 401
    
    def test_user_can_only_access_own_tasks(self, client, test_user):
        """Test that users can only access their own tasks."""
        # Create another user and their task
        other_user = User(username='otheruser', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
        db.session.commit()
        
        other_task = Task(title='Other User Task', user_id=other_user.id)
        db.session.add(other_task)
        db.session.commit()
        
        # Try to access other user's task with test_user's token
        token = test_user.generate_token()
        headers = {'Authorization': f'Bearer {token}'}
        
        response = client.get(f'/api/tasks/{other_task.id}', headers=headers)
        
        assert response.status_code == 403


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
```