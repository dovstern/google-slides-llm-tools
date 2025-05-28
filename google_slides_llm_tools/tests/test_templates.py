"""
Tests for the templates module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

# Import the functions from the module
from google_slides_llm_tools.templates import (
    apply_predefined_layout,
    duplicate_presentation,
    list_available_layouts,
    create_custom_template
)
# Import auth functions for patching
from google_slides_llm_tools.auth import get_slides_service, get_drive_service
# Import export functions for patching
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf


class TestTemplates(unittest.TestCase):
    """Test cases for the templates module."""

    @patch('google_slides_llm_tools.templates.export_slide_as_pdf')
    @patch('google_slides_llm_tools.templates.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.templates.get_slides_service')
    def test_apply_predefined_layout(self, mock_get_slides, mock_export_presentation, mock_export_slide):
        """Test applying a predefined layout to a slide."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
    
        mock_batch_update = MagicMock()
        mock_slides.batchUpdate = mock_batch_update
    
        mock_get = MagicMock()
        mock_slides.get = mock_get
    
        mock_response = MagicMock()
        mock_response.execute.return_value = {} # Batch update usually returns empty on success
        mock_batch_update.return_value = mock_response
    
        # Mock presentation get to find slide index and layout ID
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'slide1'},
                {'objectId': 'slide_id_123'} # Target slide at index 1
            ],
            'masters': [{
                'layouts': [
                    {'objectId': 'layout1', 'layoutProperties': {'displayName': 'TITLE'}},
                    {'objectId': 'layout_id_456', 'layoutProperties': {'displayName': 'TITLE_AND_BODY'}}
                ]
            }]
        }
        mock_get.return_value = mock_presentation
    
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_presentation_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_presentation_id_1.pdf")
        mock_export_presentation.return_value = (None, temp_pdf) # Return tuple
        mock_export_slide.return_value = (None, temp_slide_pdf)  # Return tuple
    
        # Create a specific mock for credentials
        mock_credentials = MagicMock()
        
        # Execute - Access the wrapped function's underlying function
        result = apply_predefined_layout.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            slide_id="slide_id_123",
            layout_name="TITLE_AND_BODY" # Use display name as per function logic
        )
    
        # Assert
        mock_get_slides.assert_called_once_with(mock_credentials)
        # We can't use assert_called_once_with here due to the way the mock chain works
        mock_batch_update.assert_called()
        self.assertEqual(
            mock_batch_update.call_args.kwargs['presentationId'], 
            "test_presentation_id"
        )
        # Assert that expected request body is passed (could check more details)
        self.assertIn('body', mock_batch_update.call_args.kwargs)
        
        # Check that export functions are called with the right arguments
        mock_export_presentation.assert_called_once_with(ANY, "test_presentation_id", temp_pdf)
        mock_export_slide.assert_called_once_with(ANY, "test_presentation_id", 1, temp_slide_pdf)
        
        # Check result structure
        self.assertIn("presentationPdfPath", result)
        self.assertIn("slidePdfPath", result)
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.templates.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.templates.get_drive_service')
    def test_duplicate_presentation(self, mock_get_drive, mock_export_presentation):
        """Test duplicating a presentation."""
        # Setup
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        mock_files = MagicMock()
        mock_drive_service.files.return_value = mock_files
    
        mock_copy = MagicMock()
        mock_files.copy = mock_copy
        mock_copy.return_value.execute.return_value = {'id': 'new_presentation_id'} # copy returns the new file info
    
        mock_update = MagicMock()
        mock_files.update = mock_update
        mock_update.return_value.execute.return_value = {'title': 'New Presentation Title'}
    
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_new_presentation_id.pdf")
        mock_export_presentation.return_value = (None, temp_pdf) # Return tuple
    
        # Create a specific mock for credentials
        mock_credentials = MagicMock()
        
        # Execute - Access the wrapped function's underlying function
        result = duplicate_presentation.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            new_title="New Presentation Title"
        )
    
        # Assert
        mock_get_drive.assert_called_once_with(mock_credentials)
        # Check copy was called with right args
        mock_copy.assert_called()
        self.assertEqual(
            mock_copy.call_args.kwargs['fileId'], 
            "test_presentation_id"
        )
        
        # Check update was called
        mock_update.assert_called()
        
        # Check export function was called with the right arguments
        mock_export_presentation.assert_called_once_with(ANY, "new_presentation_id", temp_pdf)
        
        # Check result structure
        self.assertIn("presentationId", result)
        self.assertEqual(result["presentationId"], "new_presentation_id")
        self.assertIn("presentationPdfPath", result)
        self.assertEqual(result["presentationPdfPath"], temp_pdf)

    @patch('google_slides_llm_tools.templates.get_slides_service')
    def test_list_available_layouts(self, mock_get_slides):
        """Test listing all available layouts in a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
    
        mock_get = MagicMock()
        mock_slides.get = mock_get
    
        # Mock presentation data with layouts under masters
        mock_presentation_data = {
            'masters': [
                {
                    'layouts': [
                        {'objectId': 'layout1', 'layoutProperties': {'displayName': 'TITLE'}},
                        {'objectId': 'layout2', 'layoutProperties': {'displayName': 'TITLE_AND_BODY'}}
                    ]
                },
                {
                    'layouts': [
                         {'objectId': 'layout3', 'layoutProperties': {'displayName': 'BLANK'}}
                    ]
                }
            ]
        }
        mock_get.return_value.execute.return_value = mock_presentation_data
    
        # Create a specific mock for credentials
        mock_credentials = MagicMock()
        
        # Execute - Access the wrapped function's underlying function
        result = list_available_layouts.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id"
        )
    
        # Assert
        mock_get_slides.assert_called_once_with(mock_credentials)
        # Check get was called with right args
        mock_get.assert_called()
        self.assertEqual(
            mock_get.call_args.kwargs['presentationId'], 
            "test_presentation_id"
        )
        
        # Check result has all layout names from all masters
        self.assertEqual(len(result), 3)
        self.assertIn({'layoutId': 'layout1', 'name': 'TITLE'}, result)
        self.assertIn({'layoutId': 'layout2', 'name': 'TITLE_AND_BODY'}, result)
        self.assertIn({'layoutId': 'layout3', 'name': 'BLANK'}, result)

    @patch('google_slides_llm_tools.templates.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.templates.get_slides_service')
    def test_create_custom_template(self, mock_get_slides, mock_export_presentation):
        """Test creating a custom template."""
        # Setup
        mock_slides_service = MagicMock()
        mock_get_slides.return_value = mock_slides_service
    
        mock_create = MagicMock()
        mock_slides_service.presentations().create = mock_create
        mock_create.return_value.execute.return_value = {'presentationId': 'new_template_id'}
    
        mock_batch_update = MagicMock()
        mock_slides_service.presentations().batchUpdate = mock_batch_update
        mock_batch_update.return_value.execute.return_value = {}
    
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_new_template_id.pdf")
        mock_export_presentation.return_value = (None, temp_pdf) # Return tuple
    
        # Create a specific mock for credentials
        mock_credentials = MagicMock()
    
        # Simplified slides_config for testing
        test_slides_config = [
            {
                "layout": "TITLE_SLIDE", # Example layout
                "elements": [
                    {
                        "type": "TITLE",
                        "text": "Sample Title"
                    }
                ]
            }
        ]
    
        # Execute - Access the wrapped function's underlying function
        result = create_custom_template.func(
            credentials=mock_credentials,
            template_name="Custom Template",
            slides_config=test_slides_config
        )
    
        # Assert
        mock_get_slides.assert_called_once_with(mock_credentials)
        # Check create was called with right title
        mock_create.assert_called()
        self.assertEqual(
            mock_create.call_args.kwargs['body']['title'], 
            "Custom Template"
        )
        
        # Check batch update was called for slide creation/configuration
        mock_batch_update.assert_called()
        
        # Check export function was called with the right arguments
        mock_export_presentation.assert_called_once_with(ANY, "new_template_id", temp_pdf)
        
        # Check result structure
        self.assertIn("presentationId", result)
        self.assertEqual(result["presentationId"], "new_template_id")
        self.assertIn("presentationPdfPath", result)
        self.assertEqual(result["presentationPdfPath"], temp_pdf)


if __name__ == '__main__':
    unittest.main() 