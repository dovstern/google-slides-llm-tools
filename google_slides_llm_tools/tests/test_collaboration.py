"""
Tests for the collaboration module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY

# Import the functions from the module to test
from google_slides_llm_tools.collaboration import (
    add_editor_permission,
    add_viewer_permission,
    add_commenter_permission,
    remove_permission,
    list_permissions,
    make_public
)

# Import auth functions
from google_slides_llm_tools.auth import get_drive_service


class TestCollaboration(unittest.TestCase):
    """Test cases for the collaboration module."""

    @patch('google_slides_llm_tools.collaboration.get_drive_service')
    def test_add_editor_permission(self, mock_get_drive):
        """Test adding editor permission for a specific user."""
        # Setup mocks
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        
        mock_permissions = MagicMock()
        mock_drive_service.permissions.return_value = mock_permissions
        
        mock_create = MagicMock()
        mock_permissions.create = mock_create
        mock_create.return_value.execute.return_value = {'id': 'test_permission_id', 'role': 'writer'}
        
        # Set up mock credentials
        mock_credentials = MagicMock()
        
        # Execute - access wrapped function
        result = add_editor_permission.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            email="test_user@example.com"
        )
        
        # Assert
        mock_get_drive.assert_called_once_with(mock_credentials)
        
        # Check create was called with the right parameters
        mock_create.assert_called_once()
        call_args = mock_create.call_args.kwargs
        self.assertEqual(call_args['fileId'], 'test_presentation_id')
        
        # Check that body contains expected values
        self.assertEqual(call_args['body']['role'], 'writer')
        self.assertEqual(call_args['body']['type'], 'user')
        self.assertEqual(call_args['body']['emailAddress'], 'test_user@example.com')
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['permission_id'], 'test_permission_id')

    @patch('google_slides_llm_tools.collaboration.get_drive_service')
    def test_add_viewer_permission(self, mock_get_drive):
        """Test adding viewer permission for a specific user."""
        # Setup mocks
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        
        mock_permissions = MagicMock()
        mock_drive_service.permissions.return_value = mock_permissions
        
        mock_create = MagicMock()
        mock_permissions.create = mock_create
        mock_create.return_value.execute.return_value = {'id': 'test_permission_id', 'role': 'reader'}
        
        # Set up mock credentials
        mock_credentials = MagicMock()
        
        # Execute - access wrapped function
        result = add_viewer_permission.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            email="test_user@example.com"
        )
        
        # Assert
        mock_get_drive.assert_called_once_with(mock_credentials)
        
        # Check create was called with the right parameters
        mock_create.assert_called_once()
        call_args = mock_create.call_args.kwargs
        self.assertEqual(call_args['fileId'], 'test_presentation_id')
        
        # Check that body contains expected values
        self.assertEqual(call_args['body']['role'], 'reader')
        self.assertEqual(call_args['body']['type'], 'user')
        self.assertEqual(call_args['body']['emailAddress'], 'test_user@example.com')
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['permission_id'], 'test_permission_id')

    @patch('google_slides_llm_tools.collaboration.get_drive_service')
    def test_add_commenter_permission(self, mock_get_drive):
        """Test adding commenter permission for a specific user."""
        # Setup mocks
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        
        mock_permissions = MagicMock()
        mock_drive_service.permissions.return_value = mock_permissions
        
        mock_create = MagicMock()
        mock_permissions.create = mock_create
        mock_create.return_value.execute.return_value = {'id': 'test_permission_id', 'role': 'commenter'}
        
        # Set up mock credentials
        mock_credentials = MagicMock()
        
        # Execute - access wrapped function
        result = add_commenter_permission.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            email="test_user@example.com"
        )
        
        # Assert
        mock_get_drive.assert_called_once_with(mock_credentials)
        
        # Check create was called with the right parameters
        mock_create.assert_called_once()
        call_args = mock_create.call_args.kwargs
        self.assertEqual(call_args['fileId'], 'test_presentation_id')
        
        # Check that body contains expected values
        self.assertEqual(call_args['body']['role'], 'commenter')
        self.assertEqual(call_args['body']['type'], 'user')
        self.assertEqual(call_args['body']['emailAddress'], 'test_user@example.com')
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['permission_id'], 'test_permission_id')

    @patch('google_slides_llm_tools.collaboration.get_drive_service')
    def test_remove_permission(self, mock_get_drive):
        """Test removing permission for a user."""
        # Setup mocks
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        
        mock_permissions = MagicMock()
        mock_drive_service.permissions.return_value = mock_permissions
        
        mock_delete = MagicMock()
        mock_permissions.delete = mock_delete
        mock_delete.return_value.execute.return_value = None  # Delete usually returns empty
        
        # Set up mock credentials
        mock_credentials = MagicMock()
        
        # Execute - access wrapped function
        result = remove_permission.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            permission_id="test_permission_id"
        )
        
        # Assert
        mock_get_drive.assert_called_once_with(mock_credentials)
        
        # Check delete was called with the right parameters
        mock_delete.assert_called_once()
        call_args = mock_delete.call_args.kwargs
        self.assertEqual(call_args['fileId'], 'test_presentation_id')
        self.assertEqual(call_args['permissionId'], 'test_permission_id')
        
        # Check result
        self.assertTrue(result['success'])

    @patch('google_slides_llm_tools.collaboration.get_drive_service')
    def test_list_permissions(self, mock_get_drive):
        """Test listing permissions for a presentation."""
        # Setup mocks
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        
        mock_permissions = MagicMock()
        mock_drive_service.permissions.return_value = mock_permissions
        
        mock_list = MagicMock()
        mock_permissions.list = mock_list
        
        # Sample permissions list response
        mock_permissions_response = {
            'permissions': [
                {
                    'id': 'permission1',
                    'type': 'user',
                    'role': 'writer',
                    'emailAddress': 'user1@example.com'
                },
                {
                    'id': 'permission2',
                    'type': 'user',
                    'role': 'reader',
                    'emailAddress': 'user2@example.com'
                }
            ]
        }
        mock_list.return_value.execute.return_value = mock_permissions_response
        
        # Set up mock credentials
        mock_credentials = MagicMock()
        
        # Execute - access wrapped function
        result = list_permissions.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id"
        )
        
        # Assert
        mock_get_drive.assert_called_once_with(mock_credentials)
        
        # Check list was called with the right parameters
        mock_list.assert_called_once()
        call_args = mock_list.call_args.kwargs
        self.assertEqual(call_args['fileId'], 'test_presentation_id')
        
        # Check result contains the permissions list
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], 'permission1')
        self.assertEqual(result[0]['emailAddress'], 'user1@example.com')
        self.assertEqual(result[1]['id'], 'permission2')
        self.assertEqual(result[1]['role'], 'reader')

    @patch('google_slides_llm_tools.collaboration.get_drive_service')
    def test_make_public(self, mock_get_drive):
        """Test making a presentation publicly accessible."""
        # Setup mocks
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        
        mock_permissions = MagicMock()
        mock_drive_service.permissions.return_value = mock_permissions
        
        mock_create = MagicMock()
        mock_permissions.create = mock_create
        mock_create.return_value.execute.return_value = {'id': 'public_permission_id', 'role': 'reader', 'type': 'anyone'}
        
        # Set up mock credentials
        mock_credentials = MagicMock()
        
        # Execute - access wrapped function
        result = make_public.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            role="reader"  # Can be reader, commenter, etc
        )
        
        # Assert
        mock_get_drive.assert_called_once_with(mock_credentials)
        
        # Check create was called with the right parameters
        mock_create.assert_called_once()
        call_args = mock_create.call_args.kwargs
        self.assertEqual(call_args['fileId'], 'test_presentation_id')
        
        # Check that body contains expected values
        self.assertEqual(call_args['body']['role'], 'reader')
        self.assertEqual(call_args['body']['type'], 'anyone')
        
        # Check result
        self.assertTrue(result['success'])
        self.assertEqual(result['permission_id'], 'public_permission_id')


if __name__ == '__main__':
    unittest.main() 