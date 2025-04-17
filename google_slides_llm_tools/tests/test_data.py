"""
Tests for the data module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

from google_slides_llm_tools import (
    create_sheets_chart,
    create_table_from_sheets
)


class TestData(unittest.TestCase):
    """Test cases for the data module."""

    @patch('google_slides_llm_tools.data.export_slide_as_pdf')
    @patch('google_slides_llm_tools.data.export_presentation_as_pdf')
    def test_create_sheets_chart(self, mock_export_presentation, mock_export_slide):
        """Test creating a chart from Google Sheets data."""
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
        with patch('google_slides_llm_tools.data.get_slides_service', return_value=mock_service):
            result = create_sheets_chart(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123",
                "test_spreadsheet_id",
                "test_sheet_id",
                "test_chart_id",
                100, 100, 300, 200
            )
        
        # Assert
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.data.export_slide_as_pdf')
    @patch('google_slides_llm_tools.data.export_presentation_as_pdf')
    def test_create_table_from_sheets(self, mock_export_presentation, mock_export_slide):
        """Test creating a table from Google Sheets data."""
        # Setup
        mock_service = MagicMock()
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_batch_update = MagicMock()
        mock_slides.batchUpdate = mock_batch_update
        
        mock_get = MagicMock()
        mock_slides.get = mock_get
        
        mock_sheets_service = MagicMock()
        mock_sheets = MagicMock()
        mock_sheets_service.spreadsheets.return_value = mock_sheets
        
        mock_values = MagicMock()
        mock_sheets.values = mock_values
        
        mock_get_values = MagicMock()
        mock_values.get = mock_get_values
        
        mock_sheets_response = MagicMock()
        mock_sheets_response.execute.return_value = {
            'values': [
                ['Header 1', 'Header 2', 'Header 3'],
                ['Value 1', 'Value 2', 'Value 3'],
                ['Value 4', 'Value 5', 'Value 6']
            ]
        }
        mock_get_values.return_value = mock_sheets_response
        
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
        with patch('google_slides_llm_tools.data.get_slides_service', return_value=mock_service), \
             patch('google_slides_llm_tools.data.get_sheets_service', return_value=mock_sheets_service):
            result = create_table_from_sheets(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123",
                "test_spreadsheet_id",
                "test_sheet_id",
                "A1:C3",
                100, 100, 300, 200
            )
        
        # Assert
        mock_get_values.assert_called_once_with(
            spreadsheetId="test_spreadsheet_id",
            range="test_sheet_id!A1:C3"
        )
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once()
        mock_export_slide.assert_called_once()
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)


if __name__ == '__main__':
    unittest.main() 