"""
Tests for the multimedia module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

from google_slides_llm_tools import (
    add_image_to_slide,
    add_video_to_slide,
    insert_audio_link,
    add_shape_to_slide
)


class TestMultimedia(unittest.TestCase):
    """Test cases for the multimedia module."""

    @patch('google_slides_llm_tools.multimedia.export_slide_as_pdf')
    @patch('google_slides_llm_tools.multimedia.export_presentation_as_pdf')
    def test_add_image_to_slide(self, mock_export_presentation, mock_export_slide):
        """Test adding an image to a slide."""
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
        with patch('google_slides_llm_tools.multimedia.get_slides_service', return_value=mock_service):
            result = add_image_to_slide(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123",
                "https://example.com/image.jpg",
                100, 100, 300, 200
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.multimedia.export_slide_as_pdf')
    @patch('google_slides_llm_tools.multimedia.export_presentation_as_pdf')
    def test_add_video_to_slide(self, mock_export_presentation, mock_export_slide):
        """Test adding a video to a slide."""
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
        with patch('google_slides_llm_tools.multimedia.get_slides_service', return_value=mock_service):
            result = add_video_to_slide(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123",
                "https://www.youtube.com/watch?v=test_video",
                100, 100, 300, 200,
                auto_play=True,
                start_time=10,
                end_time=60,
                mute=False
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.multimedia.export_slide_as_pdf')
    @patch('google_slides_llm_tools.multimedia.export_presentation_as_pdf')
    def test_insert_audio_link(self, mock_export_presentation, mock_export_slide):
        """Test inserting an audio link in a slide."""
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
        with patch('google_slides_llm_tools.multimedia.get_slides_service', return_value=mock_service):
            result = insert_audio_link(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123",
                "https://example.com/audio.mp3",
                100, 100, 300, 200,
                link_text="Listen to Audio"
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.multimedia.export_slide_as_pdf')
    @patch('google_slides_llm_tools.multimedia.export_presentation_as_pdf')
    def test_add_shape_to_slide(self, mock_export_presentation, mock_export_slide):
        """Test adding a shape to a slide."""
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
        with patch('google_slides_llm_tools.multimedia.get_slides_service', return_value=mock_service):
            result = add_shape_to_slide(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123",
                "RECTANGLE",
                100, 100, 300, 200,
                {"red": 0.5, "green": 0.5, "blue": 0.5}
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