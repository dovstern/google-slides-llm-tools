"""
Tests for the authentication module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock

from google_slides_llm_tools import authenticate


class TestAuthentication(unittest.TestCase):
    """Test cases for the authentication module."""

    @patch('google_slides_llm_tools.auth.build')
    @patch('google_slides_llm_tools.auth.service_account.Credentials.from_service_account_file')
    def test_authenticate_with_service_account(self, mock_credentials, mock_build):
        """Test authentication with a service account file."""
        # Setup
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Execute
        result = authenticate(credentials_path="fake_service_account.json")
        
        # Assert
        mock_credentials.assert_called_once_with("fake_service_account.json")
        mock_build.assert_called_once()
        self.assertEqual(result, mock_service)
    
    @patch('google_slides_llm_tools.auth.build')
    @patch('google_slides_llm_tools.auth.InstalledAppFlow.from_client_secrets_file')
    def test_authenticate_with_oauth(self, mock_flow, mock_build):
        """Test authentication with OAuth."""
        # Setup
        mock_credentials = MagicMock()
        mock_flow.return_value.run_local_server.return_value = mock_credentials
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        # Execute
        result = authenticate(credentials_path="fake_oauth_credentials.json", use_oauth=True)
        
        # Assert
        mock_flow.assert_called_once_with("fake_oauth_credentials.json", scopes=['https://www.googleapis.com/auth/presentations', 'https://www.googleapis.com/auth/drive'])
        mock_build.assert_called_once()
        self.assertEqual(result, mock_service)


if __name__ == '__main__':
    unittest.main() 