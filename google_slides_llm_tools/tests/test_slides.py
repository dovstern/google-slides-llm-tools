"""
Tests for the slides operations module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY, call
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
        mock_export_pdf.return_value = ("content", temp_pdf)
        
        # Execute
        with patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=mock_service):
            result = create_presentation(
                MagicMock(),
                "Test Presentation"
            )
        
        # Assert
        mock_create.assert_called_once_with(body={"title": "Test Presentation"})
        mock_export_pdf.assert_called_once_with(ANY, "test_presentation_id")
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
        mock_export_presentation.return_value = ("content_pres", temp_pdf)
        mock_export_slide.return_value = ("content_slide", temp_slide_pdf)
        
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
        mock_export_pdf.return_value = ("content", temp_pdf)
        
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
        mock_export_pdf.assert_called_once_with(ANY, "test_presentation_id")
        self.assertEqual(result["success"], True)
        self.assertEqual(result["pdfPath"], temp_pdf)

    @patch('google_slides_llm_tools.slides.get_slides_service')
    def test_reorder_slides(self, mock_get_slides):
        """Test reordering slides in a presentation."""
        # Setup
        mock_slides_service = MagicMock()
        mock_get_slides.return_value = mock_slides_service

        # Mock the 'presentations' resource
        mock_presentations = MagicMock()
        mock_slides_service.presentations.return_value = mock_presentations

        # Mock the 'get' method for checking slides before reordering
        mock_get = MagicMock()
        mock_presentations.get = mock_get
        
        # Set up initial presentation response
        mock_presentation_initial = MagicMock()
        mock_presentation_initial.execute.return_value = {
            'slides': [
                {'objectId': 'slide2'},
                {'objectId': 'slide1'}
            ]
        }
        mock_get.return_value = mock_presentation_initial
        
        # Mock the 'batchUpdate' method
        mock_batch_update = MagicMock()
        mock_presentations.batchUpdate = mock_batch_update
        mock_batch_update.return_value.execute.return_value = {}
        
        # Mock the 'get' method for checking slides after reordering
        # We need to change the mock to return the updated order after the batchUpdate
        def get_side_effect(presentationId):
            if mock_batch_update.call_count > 0:
                # After reordering, return slides in the requested order
                mock_presentation_final = MagicMock()
                mock_presentation_final.execute.return_value = {
                    'slides': [
                        {'objectId': 'slide1'},
                        {'objectId': 'slide2'}
                    ]
                }
                return mock_presentation_final
            else:
                # Before reordering, return slides in the initial order
                return mock_presentation_initial
        
        mock_get.side_effect = get_side_effect
        
        # Mock the export to PDF function
        with patch('google_slides_llm_tools.slides.export_presentation_to_pdf') as mock_export:
            mock_export.return_value = "/tmp/test_presentation.pdf"
            
            # Execute - access wrapped function
            result = reorder_slides.func(
                credentials=MagicMock(),
                presentation_id="test_presentation_id",
                slide_ids=['slide1', 'slide2']
            )
            
            # Assert
            mock_get_slides.assert_called_once()
            
            # Verify first get call (before reordering)
            self.assertIn(call("test_presentation_id"), mock_get.call_args_list)
            
            # Verify batchUpdate call
            mock_batch_update.assert_called_once()
            call_args = mock_batch_update.call_args.kwargs
            self.assertEqual(call_args['presentationId'], "test_presentation_id")
            self.assertEqual(len(call_args['body']['requests']), 1)
            
            # Verify second get call (after reordering)
            self.assertEqual(mock_get.call_count, 2)
            
            # Verify PDF export was called
            mock_export.assert_called_once_with(MagicMock(), "test_presentation_id")
            
            # Verify the result format
            self.assertIn('slideIds', result)
            self.assertIn('pdfPath', result)
            self.assertEqual(result['slideIds'], ['slide1', 'slide2'])
            self.assertEqual(result['pdfPath'], "/tmp/test_presentation.pdf")

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
        
        mock_get.side_effect = [
            MagicMock(execute=MagicMock(return_value={
                'slides': [
                    {'objectId': 'slide1'},
                    {'objectId': 'slide2'}
                ]
            })),
            MagicMock(execute=MagicMock(return_value={
                'slides': [
                    {'objectId': 'slide1'},
                    {'objectId': 'slide2'},
                    {'objectId': 'new_slide_id'}
                ]
            }))
        ]

        temp_pdf = os.path.join(tempfile.gettempdir(), "test_presentation.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "test_slide.pdf")
        mock_export_presentation.return_value = ("content_pres", temp_pdf)
        mock_export_slide.return_value = ("content_slide", temp_slide_pdf)
        
        # Execute
        with patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=mock_service):
            result = duplicate_slide(
                MagicMock(),
                "test_presentation_id",
                "slide1"
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        self.assertEqual(mock_get.call_count, 2)
        mock_get.assert_any_call(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once_with(ANY, "test_presentation_id")
        mock_export_slide.assert_called_once_with(ANY, "test_presentation_id", 2)
        self.assertEqual(result["slideId"], "new_slide_id")
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)


if __name__ == '__main__':
    unittest.main() 