"""
Tests for the collaboration module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY

from google_slides_llm_tools import (
    add_editor_permission,
    add_viewer_permission,
    add_commenter_permission,
    remove_permission,
    list_permissions,
    make_public
)


class TestCollaboration(unittest.TestCase):
    """Test cases for the collaboration module."""

    def test_add_editor_permission(self):
        """Test adding editor permission to a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_permissions = MagicMock()
        mock_service.permissions.return_value = mock_permissions
        
        mock_create = MagicMock()
        mock_permissions.create = mock_create
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {'id': 'permission_id_123', 'role': 'writer', 'type': 'user'}
        mock_create.return_value = mock_response
        
        # Execute
        with patch('google_slides_llm_tools.collaboration.get_drive_service', return_value=mock_service):
            result = add_editor_permission(
                MagicMock(),
                "test_presentation_id",
                "user@example.com",
                "User permission added",
                True
            )
        
        # Assert
        mock_create.assert_called_once_with(
            fileId="test_presentation_id",
            body={
                'type': 'user',
                'role': 'writer',
                'emailAddress': 'user@example.com'
            },
            emailMessage="User permission added",
            sendNotificationEmail=True
        )
        self.assertEqual(result['id'], 'permission_id_123')
        self.assertEqual(result['role'], 'writer')
        self.assertEqual(result['type'], 'user')

    def test_add_viewer_permission(self):
        """Test adding viewer permission to a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_permissions = MagicMock()
        mock_service.permissions.return_value = mock_permissions
        
        mock_create = MagicMock()
        mock_permissions.create = mock_create
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {'id': 'permission_id_123', 'role': 'reader', 'type': 'user'}
        mock_create.return_value = mock_response
        
        # Execute
        with patch('google_slides_llm_tools.collaboration.get_drive_service', return_value=mock_service):
            result = add_viewer_permission(
                MagicMock(),
                "test_presentation_id",
                "user@example.com",
                "User permission added",
                True
            )
        
        # Assert
        mock_create.assert_called_once_with(
            fileId="test_presentation_id",
            body={
                'type': 'user',
                'role': 'reader',
                'emailAddress': 'user@example.com'
            },
            emailMessage="User permission added",
            sendNotificationEmail=True
        )
        self.assertEqual(result['id'], 'permission_id_123')
        self.assertEqual(result['role'], 'reader')
        self.assertEqual(result['type'], 'user')

    def test_add_commenter_permission(self):
        """Test adding commenter permission to a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_permissions = MagicMock()
        mock_service.permissions.return_value = mock_permissions
        
        mock_create = MagicMock()
        mock_permissions.create = mock_create
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {'id': 'permission_id_123', 'role': 'commenter', 'type': 'user'}
        mock_create.return_value = mock_response
        
        # Execute
        with patch('google_slides_llm_tools.collaboration.get_drive_service', return_value=mock_service):
            result = add_commenter_permission(
                MagicMock(),
                "test_presentation_id",
                "user@example.com",
                "User permission added",
                True
            )
        
        # Assert
        mock_create.assert_called_once_with(
            fileId="test_presentation_id",
            body={
                'type': 'user',
                'role': 'commenter',
                'emailAddress': 'user@example.com'
            },
            emailMessage="User permission added",
            sendNotificationEmail=True
        )
        self.assertEqual(result['id'], 'permission_id_123')
        self.assertEqual(result['role'], 'commenter')
        self.assertEqual(result['type'], 'user')

    def test_remove_permission(self):
        """Test removing a permission from a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_permissions = MagicMock()
        mock_service.permissions.return_value = mock_permissions
        
        mock_delete = MagicMock()
        mock_permissions.delete = mock_delete
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {}
        mock_delete.return_value = mock_response
        
        # Execute
        with patch('google_slides_llm_tools.collaboration.get_drive_service', return_value=mock_service):
            result = remove_permission(
                MagicMock(),
                "test_presentation_id",
                "permission_id_123"
            )
        
        # Assert
        mock_delete.assert_called_once_with(
            fileId="test_presentation_id",
            permissionId="permission_id_123"
        )
        self.assertEqual(result, {'success': True})

    def test_list_permissions(self):
        """Test listing permissions for a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_permissions = MagicMock()
        mock_service.permissions.return_value = mock_permissions
        
        mock_list = MagicMock()
        mock_permissions.list = mock_list
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            'permissions': [
                {'id': 'permission_id_1', 'role': 'owner', 'type': 'user', 'emailAddress': 'owner@example.com'},
                {'id': 'permission_id_2', 'role': 'writer', 'type': 'user', 'emailAddress': 'editor@example.com'},
                {'id': 'permission_id_3', 'role': 'reader', 'type': 'user', 'emailAddress': 'viewer@example.com'}
            ]
        }
        mock_list.return_value = mock_response
        
        # Execute
        with patch('google_slides_llm_tools.collaboration.get_drive_service', return_value=mock_service):
            result = list_permissions(
                MagicMock(),
                "test_presentation_id"
            )
        
        # Assert
        mock_list.assert_called_once_with(
            fileId="test_presentation_id",
            fields="permissions(id,type,emailAddress,role,displayName)"
        )
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['id'], 'permission_id_1')
        self.assertEqual(result[0]['role'], 'owner')
        self.assertEqual(result[1]['id'], 'permission_id_2')
        self.assertEqual(result[1]['role'], 'writer')
        self.assertEqual(result[2]['id'], 'permission_id_3')
        self.assertEqual(result[2]['role'], 'reader')

    def test_make_public(self):
        """Test making a presentation public."""
        # Setup
        mock_service = MagicMock()
        mock_permissions = MagicMock()
        mock_service.permissions.return_value = mock_permissions
        
        mock_create = MagicMock()
        mock_permissions.create = mock_create
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {'id': 'permission_id_123', 'role': 'reader', 'type': 'anyone'}
        mock_create.return_value = mock_response
        
        # Execute
        with patch('google_slides_llm_tools.collaboration.get_drive_service', return_value=mock_service):
            result = make_public(
                MagicMock(),
                "test_presentation_id",
                "reader"
            )
        
        # Assert
        mock_create.assert_called_once_with(
            fileId="test_presentation_id",
            body={
                'type': 'anyone',
                'role': 'reader'
            }
        )
        self.assertEqual(result['id'], 'permission_id_123')
        self.assertEqual(result['role'], 'reader')
        self.assertEqual(result['type'], 'anyone')


if __name__ == '__main__':
    unittest.main() 