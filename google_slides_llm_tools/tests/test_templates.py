"""
Tests for the templates module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

from google_slides_llm_tools import (
    apply_predefined_layout,
    duplicate_presentation,
    list_available_layouts,
    create_custom_template
)


class TestTemplates(unittest.TestCase):
    """Test cases for the templates module."""

    @patch('google_slides_llm_tools.templates.export_slide_as_pdf')
    @patch('google_slides_llm_tools.templates.export_presentation_as_pdf')
    def test_apply_predefined_layout(self, mock_export_presentation, mock_export_slide):
        """Test applying a predefined layout to a slide."""
        # Setup
        mock_service = MagicMock()
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_batch_update = MagicMock()
        mock_slides.batchUpdate = mock_batch_update
        
        mock_get = MagicMock()
        mock_slides.get = mock_get
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {}
        mock_batch_update.return_value = mock_response
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'slide1'},
                {'objectId': 'slide_id_123'}
            ],
            'layouts': [
                {'objectId': 'layout1', 'layoutProperties': {'displayName': 'Layout 1'}},
                {'objectId': 'layout_id_456', 'layoutProperties': {'displayName': 'TITLE_AND_BODY'}}
            ]
        }
        mock_get.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_presentation_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_presentation_id_1.pdf")
        mock_export_presentation.return_value = temp_pdf
        mock_export_slide.return_value = temp_slide_pdf
        
        # Execute
        with patch('google_slides_llm_tools.templates.get_slides_service', return_value=mock_service):
            result = apply_predefined_layout(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123",
                "layout_id_456"
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.templates.export_presentation_as_pdf')
    def test_duplicate_presentation(self, mock_export_presentation):
        """Test duplicating a presentation."""
        # Setup
        mock_drive_service = MagicMock()
        mock_files = MagicMock()
        mock_drive_service.files.return_value = mock_files
        
        mock_copy = MagicMock()
        mock_files.copy = mock_copy
        
        mock_get = MagicMock()
        mock_files.get = mock_get
        
        mock_update = MagicMock()
        mock_files.update = mock_update
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {'id': 'new_presentation_id'}
        mock_copy.return_value = mock_response
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {'name': 'Original Presentation'}
        mock_get.return_value = mock_presentation
        
        mock_update_response = MagicMock()
        mock_update_response.execute.return_value = {}
        mock_update.return_value = mock_update_response
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_new_presentation_id.pdf")
        mock_export_presentation.return_value = temp_pdf
        
        # Execute
        with patch('google_slides_llm_tools.templates.get_drive_service', return_value=mock_drive_service):
            result = duplicate_presentation(
                MagicMock(),
                "test_presentation_id",
                "New Presentation Title"
            )
        
        # Assert
        mock_copy.assert_called_once_with(
            fileId="test_presentation_id",
            body={}
        )
        mock_update.assert_called_once()
        mock_export_presentation.assert_called_once()
        self.assertEqual(result["presentationId"], "new_presentation_id")
        self.assertEqual(result["presentationPdfPath"], temp_pdf)

    def test_list_available_layouts(self):
        """Test listing all available layouts in a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_get = MagicMock()
        mock_slides.get = mock_get
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'layouts': [
                {'objectId': 'layout1', 'layoutProperties': {'displayName': 'TITLE'}},
                {'objectId': 'layout2', 'layoutProperties': {'displayName': 'TITLE_AND_BODY'}},
                {'objectId': 'layout3', 'layoutProperties': {'displayName': 'BLANK'}}
            ]
        }
        mock_get.return_value = mock_presentation
        
        # Execute
        with patch('google_slides_llm_tools.templates.get_slides_service', return_value=mock_service):
            result = list_available_layouts(
                MagicMock(),
                "test_presentation_id"
            )
        
        # Assert
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]['layoutId'], 'layout1')
        self.assertEqual(result[0]['displayName'], 'TITLE')
        self.assertEqual(result[1]['layoutId'], 'layout2')
        self.assertEqual(result[1]['displayName'], 'TITLE_AND_BODY')
        self.assertEqual(result[2]['layoutId'], 'layout3')
        self.assertEqual(result[2]['displayName'], 'BLANK')

    @patch('google_slides_llm_tools.templates.export_presentation_as_pdf')
    def test_create_custom_template(self, mock_export_presentation):
        """Test creating a custom template."""
        # Setup
        mock_service = MagicMock()
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_create = MagicMock()
        mock_slides.create = mock_create
        
        mock_batch_update = MagicMock()
        mock_slides.batchUpdate = mock_batch_update
        
        mock_drive_service = MagicMock()
        mock_files = MagicMock()
        mock_drive_service.files.return_value = mock_files
        
        mock_update = MagicMock()
        mock_files.update = mock_update
        
        mock_create_response = MagicMock()
        mock_create_response.execute.return_value = {'presentationId': 'new_template_id'}
        mock_create.return_value = mock_create_response
        
        mock_batch_response = MagicMock()
        mock_batch_response.execute.return_value = {}
        mock_batch_update.return_value = mock_batch_response
        
        mock_update_response = MagicMock()
        mock_update_response.execute.return_value = {}
        mock_update.return_value = mock_update_response
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_new_template_id.pdf")
        mock_export_presentation.return_value = temp_pdf
        
        # Execute
        with patch('google_slides_llm_tools.templates.get_slides_service', return_value=mock_service), \
             patch('google_slides_llm_tools.templates.get_drive_service', return_value=mock_drive_service):
            result = create_custom_template(
                MagicMock(),
                "Custom Template",
                [
                    {
                        "name": "Title Slide",
                        "type": "TITLE",
                        "elements": [
                            {
                                "type": "TITLE",
                                "text": "Sample Title",
                                "position": {"x": 100, "y": 100, "width": 400, "height": 100}
                            }
                        ]
                    }
                ]
            )
        
        # Assert
        mock_create.assert_called_once_with(body={'title': 'Custom Template'})
        mock_batch_update.assert_called_once()
        mock_update.assert_called_once()
        mock_export_presentation.assert_called_once()
        self.assertEqual(result["presentationId"], "new_template_id")
        self.assertEqual(result["presentationPdfPath"], temp_pdf)


if __name__ == '__main__':
    unittest.main() 