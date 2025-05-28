import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

# Import from specific submodule
from google_slides_llm_tools.formatting import (
    add_text_to_slide      # Corrected import location
)
from google_slides_llm_tools.multimedia import (
    add_image_to_slide     # Keep this one
)

# Import necessary functions from other modules if needed for patching
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
from google_slides_llm_tools.auth import get_slides_service

class TestContent(unittest.TestCase):
    """Test cases for the content/multimedia functions."""

    @patch('google_slides_llm_tools.formatting.export_slide_as_pdf') # Patch export within formatting module
    @patch('google_slides_llm_tools.formatting.export_presentation_as_pdf') # Patch export within formatting module
    @patch('google_slides_llm_tools.formatting.get_slides_service') # Patch get_slides_service within formatting module
    def test_add_text_to_slide(self, mock_get_slides, mock_export_presentation, mock_export_slide):
        """Test adding text to a slide."""
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
        mock_response.execute.return_value = {
            "replies": [{"createShape": {"objectId": "new_textbox_id"}}]
        }
        mock_batch_update.return_value = mock_response
        
        mock_presentation = MagicMock()
        # Mock the return value for the get call within add_text_to_slide
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'other_slide'}, 
                {'objectId': 'slide_id_123'} # Target slide at index 1
            ]
        }
        mock_get.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_presentation_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_presentation_id_1.pdf")
        mock_export_presentation.return_value = (None, temp_pdf)
        mock_export_slide.return_value = (None, temp_slide_pdf)
        
        # Execute
        # Call the raw function directly (removed .__wrapped__)
        result = add_text_to_slide(
            credentials=MagicMock(),
            presentation_id="test_presentation_id",
            slide_id="slide_id_123",
            text="Hello, World!",
            position={'x': 100, 'y': 50, 'width': 200, 'height': 30} 
        )
        
        # Assert
        mock_get_slides.assert_called_once_with(MagicMock())
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once_with(ANY, "test_presentation_id", temp_pdf)
        mock_export_slide.assert_called_once_with(ANY, "test_presentation_id", 1, temp_slide_pdf)
        self.assertEqual(result["replies"][0]["createShape"]["objectId"], "new_textbox_id") # Check actual response structure
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.multimedia.export_slide_as_pdf') 
    @patch('google_slides_llm_tools.multimedia.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.multimedia.get_slides_service') 
    def test_add_image_to_slide(self, mock_get_slides, mock_export_presentation, mock_export_slide):
        """Test adding an image to a slide."""
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
        mock_response.execute.return_value = {
            "replies": [{"createImage": {"objectId": "new_image_id"}}]
        }
        mock_batch_update.return_value = mock_response
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'other_slide'}, 
                {'objectId': 'slide_id_123'} # Target slide at index 1
            ]
        }
        mock_get.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_presentation_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_presentation_id_1.pdf")
        mock_export_presentation.return_value = (None, temp_pdf)
        mock_export_slide.return_value = (None, temp_slide_pdf)
        
        # Execute
        # Call the raw function directly (removed .__wrapped__)
        result = add_image_to_slide(
            credentials=MagicMock(),
            presentation_id="test_presentation_id",
            slide_id="slide_id_123",
            image_url="https://example.com/image.jpg",
            x=150, y=150, width=100, height=100 
        )
        
        # Assert
        mock_get_slides.assert_called_once_with(MagicMock())
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once_with(ANY, "test_presentation_id", temp_pdf)
        mock_export_slide.assert_called_once_with(ANY, "test_presentation_id", 1, temp_slide_pdf)
        self.assertEqual(result["replies"][0]["createImage"]["objectId"], "new_image_id") # Check actual response structure
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

if __name__ == '__main__':
    unittest.main() 