"""
Tests for the formatting module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

from google_slides_llm_tools import (
    add_text_to_slide,
    update_text_style,
    update_paragraph_style
)


class TestFormatting(unittest.TestCase):
    """Test cases for the formatting module."""

    @patch('google_slides_llm_tools.formatting.export_slide_as_pdf')
    @patch('google_slides_llm_tools.formatting.export_presentation_as_pdf')
    def test_add_text_to_slide(self, mock_export_presentation, mock_export_slide):
        """Test adding text to a slide."""
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
            ]
        }
        mock_get.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_presentation_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_presentation_id_1.pdf")
        mock_export_presentation.return_value = temp_pdf
        mock_export_slide.return_value = temp_slide_pdf
        
        # Execute
        with patch('google_slides_llm_tools.formatting.get_slides_service', return_value=mock_service):
            result = add_text_to_slide(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123",
                "Test Text",
                {'x': 100, 'y': 100, 'width': 300, 'height': 200}
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)
    
    @patch('google_slides_llm_tools.formatting.export_slide_as_pdf')
    @patch('google_slides_llm_tools.formatting.export_presentation_as_pdf')
    def test_update_text_style(self, mock_export_presentation, mock_export_slide):
        """Test updating text style in a slide."""
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
                {
                    'objectId': 'slide1',
                    'pageElements': [
                        {'objectId': 'text_box_123'}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_presentation_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_presentation_id_0.pdf")
        mock_export_presentation.return_value = temp_pdf
        mock_export_slide.return_value = temp_slide_pdf
        
        # Execute
        with patch('google_slides_llm_tools.formatting.get_slides_service', return_value=mock_service):
            result = update_text_style(
                MagicMock(),
                "test_presentation_id",
                "text_box_123",
                {
                    'fontFamily': 'Arial',
                    'fontSize': 18,
                    'bold': True,
                    'italic': False,
                    'foregroundColor': {'red': 0, 'green': 0, 'blue': 0}
                }
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)
    
    @patch('google_slides_llm_tools.formatting.export_slide_as_pdf')
    @patch('google_slides_llm_tools.formatting.export_presentation_as_pdf')
    def test_update_paragraph_style(self, mock_export_presentation, mock_export_slide):
        """Test updating paragraph style in a slide."""
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
                {
                    'objectId': 'slide1',
                    'pageElements': [
                        {'objectId': 'text_box_123'}
                    ]
                }
            ]
        }
        mock_get.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_presentation_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_presentation_id_0.pdf")
        mock_export_presentation.return_value = temp_pdf
        mock_export_slide.return_value = temp_slide_pdf
        
        # Execute
        with patch('google_slides_llm_tools.formatting.get_slides_service', return_value=mock_service):
            result = update_paragraph_style(
                MagicMock(),
                "test_presentation_id",
                "text_box_123",
                {
                    'alignment': 'CENTER',
                    'lineSpacing': 150,
                    'spaceAbove': 10,
                    'spaceBelow': 10,
                    'indentFirstLine': 20,
                    'indentStart': 10,
                    'indentEnd': 10,
                    'direction': 'LEFT_TO_RIGHT',
                    'spacingMode': 'NEVER_COLLAPSE'
                }
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)


if __name__ == '__main__':
    unittest.main() 