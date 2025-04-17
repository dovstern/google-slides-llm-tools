"""
Tests for the slides operations module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

from google_slides_llm_tools import (
    create_presentation,
    get_presentation,
    add_slide,
    delete_slide,
    reorder_slides,
    duplicate_slide
)


class TestSlides(unittest.TestCase):
    """Test cases for the slides operations module."""

    @patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
    def test_create_presentation(self, mock_export_pdf):
        """Test creating a new presentation."""
        # Setup
        mock_service = MagicMock()
        mock_presentations = MagicMock()
        mock_service.presentations.return_value = mock_presentations
        
        mock_create = MagicMock()
        mock_presentations.create = mock_create
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {"presentationId": "test_presentation_id"}
        mock_create.return_value = mock_response
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "test_presentation.pdf")
        mock_export_pdf.return_value = temp_pdf
        
        # Execute
        with patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=mock_service):
            result = create_presentation(
                MagicMock(),
                "Test Presentation"
            )
        
        # Assert
        mock_create.assert_called_once_with(body={"title": "Test Presentation"})
        mock_export_pdf.assert_called_once_with(ANY, "test_presentation_id", ANY)
        self.assertEqual(result["presentationId"], "test_presentation_id")
        self.assertEqual(result["pdfPath"], temp_pdf)
    
    @patch('google_slides_llm_tools.slides_operations.export_slide_as_pdf')
    @patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
    def test_add_slide(self, mock_export_presentation, mock_export_slide):
        """Test adding a slide to a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_presentations = MagicMock()
        mock_service.presentations.return_value = mock_presentations
        
        mock_batch_update = MagicMock()
        mock_presentations.batchUpdate = mock_batch_update
        
        mock_get = MagicMock()
        mock_presentations.get = mock_get
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            "replies": [{"createSlide": {"objectId": "test_slide_id"}}]
        }
        mock_batch_update.return_value = mock_response
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'slide1'},
                {'objectId': 'test_slide_id'}
            ]
        }
        mock_get.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "test_presentation.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "test_slide.pdf")
        mock_export_presentation.return_value = temp_pdf
        mock_export_slide.return_value = temp_slide_pdf
        
        # Execute
        with patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=mock_service):
            result = add_slide(
                MagicMock(),
                "test_presentation_id",
                "TITLE_AND_BODY"
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["slideId"], "test_slide_id")
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    def test_get_presentation(self):
        """Test getting presentation details."""
        # Setup
        mock_service = MagicMock()
        mock_presentations = MagicMock()
        mock_service.presentations.return_value = mock_presentations
        
        mock_get = MagicMock()
        mock_presentations.get = mock_get
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            "presentationId": "test_presentation_id",
            "title": "Test Presentation",
            "slides": [
                {"objectId": "slide1"},
                {"objectId": "slide2"}
            ]
        }
        mock_get.return_value = mock_response
        
        # Execute
        with patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=mock_service):
            result = get_presentation(
                MagicMock(),
                "test_presentation_id"
            )
        
        # Assert
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        self.assertEqual(result["presentationId"], "test_presentation_id")
        self.assertEqual(result["title"], "Test Presentation")
        self.assertEqual(len(result["slides"]), 2)

    @patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
    def test_delete_slide(self, mock_export_pdf):
        """Test deleting a slide from a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_presentations = MagicMock()
        mock_service.presentations.return_value = mock_presentations
        
        mock_batch_update = MagicMock()
        mock_presentations.batchUpdate = mock_batch_update
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {}
        mock_batch_update.return_value = mock_response
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "test_presentation.pdf")
        mock_export_pdf.return_value = temp_pdf
        
        # Execute
        with patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=mock_service):
            result = delete_slide(
                MagicMock(),
                "test_presentation_id",
                "test_slide_id"
            )
        
        # Assert
        mock_batch_update.assert_called_once_with(
            presentationId="test_presentation_id",
            body={"requests": [{"deleteObject": {"objectId": "test_slide_id"}}]}
        )
        mock_export_pdf.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["success"], True)

    @patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
    def test_reorder_slides(self, mock_export_pdf):
        """Test reordering slides in a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_presentations = MagicMock()
        mock_service.presentations.return_value = mock_presentations
        
        mock_batch_update = MagicMock()
        mock_presentations.batchUpdate = mock_batch_update
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {}
        mock_batch_update.return_value = mock_response
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "test_presentation.pdf")
        mock_export_pdf.return_value = temp_pdf
        
        # Execute
        with patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=mock_service):
            result = reorder_slides(
                MagicMock(),
                "test_presentation_id",
                ["slide1", "slide2"],
                0
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        self.assertEqual(len(result["slideIds"]), 2)
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["success"], True)

    @patch('google_slides_llm_tools.slides_operations.export_slide_as_pdf')
    @patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
    def test_duplicate_slide(self, mock_export_presentation, mock_export_slide):
        """Test duplicating a slide in a presentation."""
        # Setup
        mock_service = MagicMock()
        mock_presentations = MagicMock()
        mock_service.presentations.return_value = mock_presentations
        
        mock_batch_update = MagicMock()
        mock_presentations.batchUpdate = mock_batch_update
        
        mock_get = MagicMock()
        mock_presentations.get = mock_get
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            "replies": [{"duplicateObject": {"objectId": "new_slide_id"}}]
        }
        mock_batch_update.return_value = mock_response
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'slide1'},
                {'objectId': 'slide2'},
                {'objectId': 'new_slide_id'}
            ]
        }
        mock_get.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "test_presentation.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "test_slide.pdf")
        mock_export_presentation.return_value = temp_pdf
        mock_export_slide.return_value = temp_slide_pdf
        
        # Execute
        with patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=mock_service):
            result = duplicate_slide(
                MagicMock(),
                "test_presentation_id",
                "slide1"
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["newSlideId"], "new_slide_id")
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)


if __name__ == '__main__':
    unittest.main() 