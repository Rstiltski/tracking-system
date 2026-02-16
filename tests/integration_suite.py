"""
Integration Tests for Unified Connection Layer

Tests the integration between frontend, brain, and database modules
through the UnifiedConnectionLayer.
"""

import unittest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from brain.core.integration import UnifiedConnectionLayer, get_unified_connector, reset_unified_connector
from brain.core.command_event import CommandEvent
from brain.core.result import BrainResult


class TestUnifiedConnectionLayer(unittest.TestCase):
    """Test cases for the UnifiedConnectionLayer class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Reset the global connector to ensure clean state
        reset_unified_connector()
        
        # Create a temporary database for testing
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix='.db')
        os.environ['TEST_DB_PATH'] = self.temp_db_path
        
    def tearDown(self):
        """Clean up after each test method."""
        # Close and remove the temporary database
        os.close(self.temp_db_fd)
        os.unlink(self.temp_db_path)
        if hasattr(self, 'connector') and self.connector.database:
            # Close any open connections
            pass
        reset_unified_connector()
    
    @patch('tracking_app.database.Database.get_connection')
    def test_initialize_connections_success(self, mock_get_connection):
        """Test successful initialization of all connections."""
        # Mock the database connection
        mock_conn = Mock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = (1,)
        
        # Create the connector
        self.connector = UnifiedConnectionLayer()
        result = self.connector.initialize_connections()
        
        # Assertions
        self.assertTrue(result)
        self.assertTrue(self.connector.is_connected)
        self.assertIsNotNone(self.connector.database)
        self.assertIsNotNone(self.connector.brain)
        self.assertIsNotNone(self.connector.cerebellum)
    
    @patch('tracking_app.database.Database.get_connection')
    def test_initialize_connections_failure(self, mock_get_connection):
        """Test failure during connection initialization."""
        # Mock the database connection to raise an exception
        mock_get_connection.side_effect = Exception("Connection failed")
        
        # Create the connector
        self.connector = UnifiedConnectionLayer()
        result = self.connector.initialize_connections()
        
        # Assertions
        self.assertFalse(result)
        self.assertFalse(self.connector.is_connected)
    
    def test_validate_connection_success(self):
        """Test successful connection validation."""
        # Create and initialize the connector
        self.connector = UnifiedConnectionLayer()
        self.connector.database = Mock()
        self.connector.is_connected = True
        
        # Mock the database connection context manager with proper context methods
        mock_conn = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        self.connector.database.get_connection = Mock(return_value=mock_context)
        mock_conn.execute.return_value.fetchone.return_value = (1,)
        
        result = self.connector.validate_connection()
        
        # Assertions
        self.assertTrue(result)
    
    @patch('tracking_app.database.Database.get_connection')
    def test_validate_connection_not_initialized(self, mock_get_connection):
        """Test connection validation when not properly initialized."""
        # Create the connector without initializing
        self.connector = UnifiedConnectionLayer()
        self.connector.is_connected = False
        
        result = self.connector.validate_connection()
        
        # Assertions
        self.assertFalse(result)
    
    @patch.object(UnifiedConnectionLayer, 'validate_connection')
    def test_execute_brain_command_success(self, mock_validate_connection):
        """Test successful execution of a brain command."""
        # Mock the validation to return True
        mock_validate_connection.return_value = True
        
        # Create the connector and mock the brain
        self.connector = UnifiedConnectionLayer()
        self.connector.brain = Mock()
        self.connector.is_connected = True
        
        # Mock the brain's run method
        mock_result = BrainResult(success=True, status="SUCCESS", data={'result': 'success'}, command_id=1)
        self.connector.brain.run.return_value = mock_result
        
        # Test command data
        command_data = {
            'command_type': 'TestCommand',
            'params': {'test_param': 'test_value'},
            'user_id': 1,
            'company_id': 1
        }
        
        result = self.connector.execute_brain_command(command_data)
        
        # Assertions
        self.connector.brain.run.assert_called_once()
        self.assertTrue(result['success'])
        self.assertEqual(result['data'], {'result': 'success'})
    
    @patch('tracking_app.database.Database.get_connection')
    def test_execute_brain_command_not_connected(self, mock_get_connection):
        """Test brain command execution when not connected."""
        # Create the connector without connecting
        self.connector = UnifiedConnectionLayer()
        self.connector.is_connected = False
        
        command_data = {
            'command_type': 'TestCommand',
            'params': {'test_param': 'test_value'},
            'user_id': 1,
            'company_id': 1
        }
        
        # Should raise ConnectionError
        with self.assertRaises(ConnectionError):
            self.connector.execute_brain_command(command_data)
    
    @patch.object(UnifiedConnectionLayer, 'validate_connection')
    def test_sync_frontend_data_success(self, mock_validate_connection):
        """Test successful synchronization of frontend data."""
        # Mock the validation to return True
        mock_validate_connection.return_value = True
        
        # Create the connector and mock dependencies
        self.connector = UnifiedConnectionLayer()
        self.connector.brain = Mock()
        self.connector.database = Mock()
        self.connector.is_connected = True
        
        # Mock the brain's run method
        mock_result = BrainResult(success=True, status="SUCCESS", data={'result': 'success'}, command_id=1)
        self.connector.brain.run.return_value = mock_result
        
        # Test frontend data
        frontend_data = {
            'habits': [{'id': 1, 'name': 'Test Habit', 'created_at': '2023-01-01'}],
            'tasks': [{'id': 1, 'name': 'Test Task', 'completed': False}]
        }
        
        result = self.connector.sync_frontend_data(frontend_data)
        
        # Assertions
        self.assertTrue(result['success'])
        self.assertEqual(result['processed_items'], 2)  # 1 habit + 1 task
        # The execute_brain_command should be called for each item
        self.assertEqual(self.connector.brain.run.call_count, 2)  # 1 for habit, 1 for task
    
    @patch.object(UnifiedConnectionLayer, 'validate_connection')
    def test_get_backend_data_success(self, mock_validate_connection):
        """Test successful retrieval of backend data."""
        # Mock the validation to return True
        mock_validate_connection.return_value = True
        
        # Mock the database connection with proper context methods
        mock_conn = Mock()
        
        # Mock the execute method to return test data
        def mock_execute(query):
            mock_cursor = Mock()
            if 'habits' in query:
                mock_cursor.fetchall.return_value = [
                    {'id': 1, 'name': 'Test Habit', 'created_at': '2023-01-01'}
                ]
            elif 'tasks' in query:
                mock_cursor.fetchall.return_value = [
                    {'id': 1, 'name': 'Test Task', 'completed': False, 'created_at': '2023-01-01'}
                ]
            elif 'transactions' in query:
                mock_cursor.fetchall.return_value = [
                    {'id': 1, 'amount': 100.0, 'created_at': '2023-01-01'}
                ]
            elif 'health_entries' in query:
                mock_cursor.fetchall.return_value = [
                    {'id': 1, 'metric': 'weight', 'value': 70.0, 'created_at': '2023-01-01'}
                ]
            elif 'goals' in query:
                mock_cursor.fetchall.return_value = [
                    {'id': 1, 'title': 'Test Goal', 'target': 100, 'created_at': '2023-01-01'}
                ]
            return mock_cursor
        
        mock_conn.execute.side_effect = mock_execute
        
        # Create the connector
        self.connector = UnifiedConnectionLayer()
        self.connector.database = Mock()
        self.connector.is_connected = True
        
        # Mock the database connection context manager with proper context methods
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        self.connector.database.get_connection = Mock(return_value=mock_context)
        
        result = self.connector.get_backend_data()
        
        # Assertions
        self.assertIn('habits', result)
        self.assertIn('tasks', result)
        self.assertIn('transactions', result)
        self.assertIn('health', result)
        self.assertIn('goals', result)
        self.assertEqual(len(result['habits']), 1)
        self.assertEqual(len(result['tasks']), 1)
    
    @patch.object(UnifiedConnectionLayer, 'validate_connection')
    def test_get_backend_data_error(self, mock_validate_connection):
        """Test error handling when retrieving backend data."""
        # Mock the validation to return True
        mock_validate_connection.return_value = True
        
        # Create the connector
        self.connector = UnifiedConnectionLayer()
        self.connector.database = Mock()
        self.connector.is_connected = True
        
        # Mock the database connection to raise an exception
        mock_conn = Mock()
        mock_context = Mock()
        mock_context.__enter__ = Mock(return_value=mock_conn)
        mock_context.__exit__ = Mock(return_value=None)
        self.connector.database.get_connection = Mock(return_value=mock_context)
        mock_conn.execute.side_effect = Exception("Database error")
        
        result = self.connector.get_backend_data()
        
        # Assertions
        self.assertIn('error', result)
        self.assertEqual(result['error'], "Database error")


class TestUnifiedAPI(unittest.TestCase):
    """Test cases for the UnifiedAPI class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        reset_unified_connector()
    
    def tearDown(self):
        """Clean up after each test method."""
        reset_unified_connector()
    
    @patch.object(UnifiedConnectionLayer, 'sync_frontend_data')
    def test_sync_data_with_backend(self, mock_sync):
        """Test the sync_data_with_backend API endpoint."""
        # Mock the sync method
        mock_sync.return_value = {'success': True, 'processed_items': 5}
        
        # Call the API method
        from brain.core.integration import UnifiedAPI
        result = UnifiedAPI.sync_data_with_backend({'test': 'data'})
        
        # Assertions
        mock_sync.assert_called_once_with({'test': 'data'})
        self.assertEqual(result, {'success': True, 'processed_items': 5})
    
    @patch.object(UnifiedConnectionLayer, 'get_backend_data')
    def test_get_backend_sync_data(self, mock_get_data):
        """Test the get_backend_sync_data API endpoint."""
        # Mock the get data method
        mock_get_data.return_value = {'habits': [], 'tasks': []}
        
        # Call the API method
        from brain.core.integration import UnifiedAPI
        result = UnifiedAPI.get_backend_sync_data()
        
        # Assertions
        mock_get_data.assert_called_once()
        self.assertEqual(result, {'habits': [], 'tasks': []})
    
    @patch.object(UnifiedConnectionLayer, 'execute_brain_command')
    def test_execute_backend_command(self, mock_execute):
        """Test the execute_backend_command API endpoint."""
        # Mock the execute method
        mock_execute.return_value = {'success': True, 'data': 'result'}
        
        # Call the API method
        from brain.core.integration import UnifiedAPI
        result = UnifiedAPI.execute_backend_command({'command': 'test'})
        
        # Assertions
        mock_execute.assert_called_once_with({'command': 'test'})
        self.assertEqual(result, {'success': True, 'data': 'result'})


class TestGlobalConnector(unittest.TestCase):
    """Test cases for the global connector functions."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        reset_unified_connector()
    
    def tearDown(self):
        """Clean up after each test method."""
        reset_unified_connector()
    
    @patch('tracking_app.database.Database.get_connection')
    def test_get_unified_connector_singleton(self, mock_get_connection):
        """Test that get_unified_connector returns a singleton instance."""
        # Mock the database connection
        mock_conn = Mock()
        mock_get_connection.return_value.__enter__.return_value = mock_conn
        mock_conn.execute.return_value.fetchone.return_value = (1,)
        
        # Get the connector twice
        connector1 = get_unified_connector()
        connector2 = get_unified_connector()
        
        # They should be the same instance
        self.assertIs(connector1, connector2)
        
        # Both should have been initialized
        self.assertTrue(connector1.is_connected)
        self.assertTrue(connector2.is_connected)


if __name__ == '__main__':
    unittest.main()