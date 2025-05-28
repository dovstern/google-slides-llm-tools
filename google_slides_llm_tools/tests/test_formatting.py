"""
Tests for the formatting module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

# Import from specific submodule
from google_slides_llm_tools.formatting import (
    add_text_to_slide,
    update_text_style,
    update_paragraph_style
)

# Import necessary functions from other modules if needed for patching
from google_slides_llm_tools.auth import get_slides_service
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf


class TestFormatting(unittest.TestCase):
    """Test cases for the formatting module."""

    @patch('google_slides_llm_tools.formatting.export_slide_as_pdf')
    @patch('google_slides_llm_tools.formatting.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.formatting.get_slides_service')
    def test_update_text_style(self, mock_get_slides, mock_export_pres, mock_export_slide_pdf):
        """Test updating text style in a shape."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_presentation_data = {
            'slides': [
                {'objectId': 's1', 'pageElements': []},
                {'objectId': 's2', 'pageElements': [{'objectId': 'text_box_id'}]}
            ]
        }
        mock_service.presentations().get().execute.return_value = mock_presentation_data
        
        mock_batch_update = MagicMock()
        mock_service.presentations().batchUpdate = mock_batch_update
        mock_batch_update.return_value.execute.return_value = {}

        temp_pdf = "/tmp/pres.pdf"
        temp_slide_pdf = "/tmp/slide.pdf"
        mock_export_pres.return_value = (None, temp_pdf)
        mock_export_slide_pdf.return_value = (None, temp_slide_pdf)
        
        text_style_dict = {
            'fontFamily': 'Arial',
            'fontSize': 14,
            'bold': True,
            'italic': False,
            'underline': False,
            'strikethrough': False,
            'foregroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2}
        }
        
        # Execute
        result = update_text_style(
            credentials=MagicMock(),
            presentation_id="test_presentation_id",
            slide_object_id="text_box_id",
            text_style=text_style_dict
        )
        
        # Assert
        mock_get_slides.assert_called_once()
        mock_service.presentations().get.assert_called_once_with(presentationId='test_presentation_id')
        mock_batch_update.assert_called_once()
        mock_export_pres.assert_called_once_with(ANY, "test_presentation_id", ANY)
        mock_export_slide_pdf.assert_called_once_with(ANY, "test_presentation_id", 1, ANY)
        self.assertIn("presentationPdfPath", result)
        self.assertIn("slidePdfPath", result)
    
    @patch('google_slides_llm_tools.formatting.export_slide_as_pdf')
    @patch('google_slides_llm_tools.formatting.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.formatting.get_slides_service')
    def test_update_paragraph_style(self, mock_get_slides, mock_export_pres, mock_export_slide_pdf):
        """Test updating paragraph style in a shape."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_presentation_data = {
            'slides': [
                {'objectId': 's1', 'pageElements': [{'objectId': 'text_box_id'}]},
                {'objectId': 's2', 'pageElements': []}
            ]
        }
        mock_service.presentations().get().execute.return_value = mock_presentation_data

        mock_batch_update = MagicMock()
        mock_service.presentations().batchUpdate = mock_batch_update
        mock_batch_update.return_value.execute.return_value = {}

        temp_pdf = "/tmp/pres.pdf"
        temp_slide_pdf = "/tmp/slide.pdf"
        mock_export_pres.return_value = (None, temp_pdf)
        mock_export_slide_pdf.return_value = (None, temp_slide_pdf)

        paragraph_style_dict = {
            'alignment': 'CENTER',
            'lineSpacing': 150,
            'spaceAbove': 10,
            'spaceBelow': 5,
            'indentFirstLine': None,
            'indentStart': None,
            'indentEnd': None,
            'direction': 'LEFT_TO_RIGHT',
            'spacingMode': None
        }
        
        # Execute
        result = update_paragraph_style(
            credentials=MagicMock(),
            presentation_id="test_presentation_id",
            slide_object_id="text_box_id",
            paragraph_style=paragraph_style_dict
        )
        
        # Assert
        mock_get_slides.assert_called_once()
        mock_service.presentations().get.assert_called_once_with(presentationId='test_presentation_id')
        mock_batch_update.assert_called_once()
        mock_export_pres.assert_called_once_with(ANY, "test_presentation_id", ANY)
        mock_export_slide_pdf.assert_called_once_with(ANY, "test_presentation_id", 0, ANY)
        self.assertIn("presentationPdfPath", result)
        self.assertIn("slidePdfPath", result)


if __name__ == '__main__':
    unittest.main() 