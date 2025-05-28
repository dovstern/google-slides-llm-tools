"""
Tests for the data module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

# Check if the data module exists in the correct location
from google_slides_llm_tools import data as data_module

# Import functions directly to check they exist
try:
    # Import functions from the data module
    from google_slides_llm_tools.data import (
        create_sheets_chart,
        create_table_from_sheets,
        get_slide_data,
        get_presentation_data,
        find_element_ids
    )
except ImportError as e:
    # Print helpful debug information about where the module is actually located
    import sys
    import google_slides_llm_tools
    print(f"Python path: {sys.path}")
    print(f"google_slides_llm_tools module path: {google_slides_llm_tools.__file__}")
    print(f"google_slides_llm_tools contents: {dir(google_slides_llm_tools)}")
    # Re-raise the error to fail the test and get the stack trace
    raise

# Import auth functions for patching
from google_slides_llm_tools.auth import get_slides_service, get_sheets_service
# Import export functions for patching
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf


class TestData(unittest.TestCase):
    """Test cases for the data module."""

    @patch('google_slides_llm_tools.data.export_slide_as_pdf')
    @patch('google_slides_llm_tools.data.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.data.get_slides_service')
    def test_create_sheets_chart(self, mock_get_slides, mock_export_presentation, mock_export_slide):
        """Test inserting a chart from Google Sheets into a slide."""
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
            "replies": [{"createSheetsChart": {"objectId": "new_chart_id"}}]
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
        
        # Create a specific mock for credentials
        mock_credentials = MagicMock()
        
        # Execute - Access the wrapped function's underlying function
        result = create_sheets_chart.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            slide_id="slide_id_123",
            spreadsheet_id="test_spreadsheet_id",
            sheet_id=1, chart_id=1, 
            x=100, y=100, width=300, height=200
        )
        
        # Assert
        mock_get_slides.assert_called_once_with(mock_credentials)
        mock_batch_update.assert_called_once()
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once_with(ANY, "test_presentation_id", temp_pdf)
        mock_export_slide.assert_called_once_with(ANY, "test_presentation_id", 1, temp_slide_pdf) # Slide index is 1
        self.assertIn("presentationPdfPath", result)
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertIn("slidePdfPath", result)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.data.export_slide_as_pdf')
    @patch('google_slides_llm_tools.data.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.data.get_sheets_service')
    @patch('google_slides_llm_tools.data.get_slides_service')
    def test_create_table_from_sheets(self, mock_get_slides, mock_get_sheets, mock_export_presentation, mock_export_slide):
        """Test creating a table from Google Sheets data."""
        # Setup
        mock_slides_service = MagicMock()
        mock_get_slides.return_value = mock_slides_service
        mock_sheets_service = MagicMock()
        mock_get_sheets.return_value = mock_sheets_service
        
        mock_slides_ops = MagicMock()
        mock_slides_service.presentations.return_value = mock_slides_ops
        mock_sheets_ops = MagicMock()
        mock_sheets_service.spreadsheets.return_value = mock_sheets_ops
        
        mock_batch_update = MagicMock()
        mock_slides_ops.batchUpdate = mock_batch_update
        
        mock_get_slides_pres = MagicMock()
        mock_slides_ops.get = mock_get_slides_pres
        
        mock_get_sheets_values = MagicMock()
        mock_sheets_ops.values = MagicMock(return_value=MagicMock(get=mock_get_sheets_values))
        
        # Mock Sheets data fetch
        mock_sheets_response = MagicMock()
        mock_sheets_response.execute.return_value = {
            'values': [['Header 1', 'Header 2'], ['Data A', 'Data B']]
        }
        mock_get_sheets_values.return_value = mock_sheets_response
        
        # Mock Slides batch updates (table creation + text insertion)
        mock_batch_update.side_effect = [
            MagicMock(execute=MagicMock(return_value={})), # Table creation
            MagicMock(execute=MagicMock(return_value={}))  # Text insertion
        ]
        
        # Mock Slides presentation get for index
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'other_slide'}, 
                {'objectId': 'slide_id_123'} # Target slide at index 1
            ]
        }
        mock_get_slides_pres.return_value = mock_presentation
        
        temp_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_presentation_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_presentation_id_1.pdf")
        mock_export_presentation.return_value = (None, temp_pdf)
        mock_export_slide.return_value = (None, temp_slide_pdf)
        
        # Create a specific mock for credentials
        mock_credentials = MagicMock()
        
        # Execute - Access the wrapped function's underlying function
        result = create_table_from_sheets.func(
            credentials=mock_credentials,
            presentation_id="test_presentation_id",
            slide_id="slide_id_123",
            spreadsheet_id="test_spreadsheet_id",
            sheet_name="Sheet1", range_name="A1:B2",
            x=50, y=50, width=200, height=100
        )
        
        # Assert
        mock_get_slides.assert_called_once_with(mock_credentials)
        mock_get_sheets.assert_called_once_with(mock_credentials)
        mock_get_sheets_values.assert_called_once_with(spreadsheetId="test_spreadsheet_id", range="Sheet1!A1:B2")
        self.assertEqual(mock_batch_update.call_count, 2) # Create table + Insert text
        mock_get_slides_pres.assert_called_once_with(presentationId="test_presentation_id")
        mock_export_presentation.assert_called_once_with(ANY, "test_presentation_id", temp_pdf)
        mock_export_slide.assert_called_once_with(ANY, "test_presentation_id", 1, temp_slide_pdf)
        self.assertIn("presentationPdfPath", result)
        self.assertEqual(result["presentationPdfPath"], temp_pdf)
        self.assertIn("slidePdfPath", result)
        self.assertEqual(result["slidePdfPath"], temp_slide_pdf)

    @patch('google_slides_llm_tools.data.get_slides_service')
    def test_get_slide_data(self, mock_get_slides):
        """Test retrieving data for a specific slide."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_presentation = MagicMock()
        mock_service.presentations.return_value = mock_presentation
        mock_get = MagicMock()
        mock_presentation.get.return_value = mock_get

        expected_slide_data = {
            'objectId': 'slide_01',
            'pageElements': [
                {'objectId': 'element_01', 'shape': {'text': {'textRuns': [{'content': 'Title'}]}}},
                {'objectId': 'element_02', 'shape': {'text': {'textRuns': [{'content': 'Body'}]}}}
            ]
        }
        mock_get.execute.return_value = {
            'slides': [expected_slide_data]
        }

        # Create a specific mock for credentials
        mock_credentials = MagicMock()

        # Execute - Access the wrapped function's underlying function
        result = get_slide_data.func(
            credentials=mock_credentials,
            presentation_id="test_pres_id",
            slide_id="slide_01"
        )

        # Assert
        mock_get_slides.assert_called_once_with(mock_credentials)
        mock_presentation.get.assert_called_once_with(
            presentationId="test_pres_id",
            fields="slides(objectId,pageElements)"
        )
        mock_get.execute.assert_called_once()
        self.assertEqual(result, expected_slide_data)

    @patch('google_slides_llm_tools.data.get_slides_service')
    def test_get_presentation_data(self, mock_get_slides):
        """Test retrieving data for the entire presentation."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_presentation = MagicMock()
        mock_service.presentations.return_value = mock_presentation
        mock_get = MagicMock()
        mock_presentation.get.return_value = mock_get

        expected_presentation_data = {
            'presentationId': 'test_pres_id',
            'slides': [
                {'objectId': 'slide_01'}, {'objectId': 'slide_02'}
            ],
            'title': 'Test Presentation'
        }
        mock_get.execute.return_value = expected_presentation_data

        # Create a specific mock for credentials
        mock_credentials = MagicMock()

        # Execute - Access the wrapped function's underlying function
        result = get_presentation_data.func(
            credentials=mock_credentials, 
            presentation_id="test_pres_id"
        )

        # Assert
        mock_get_slides.assert_called_once_with(mock_credentials)
        mock_presentation.get.assert_called_once_with(
            presentationId="test_pres_id"
            # No specific fields requested, so get all
        )
        mock_get.execute.assert_called_once()
        self.assertEqual(result, expected_presentation_data)

    @patch('google_slides_llm_tools.data.get_slides_service')
    def test_find_element_ids(self, mock_get_slides):
        """Test finding element IDs by text."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_presentation = MagicMock()
        mock_service.presentations.return_value = mock_presentation
        mock_get = MagicMock()
        mock_presentation.get.return_value = mock_get

        # Create sample presentation with text elements
        mock_get.execute.return_value = {
            'slides': [
                {
                    'objectId': 'slide_01',
                    'pageElements': [
                        {
                            'objectId': 'text_box_1',
                            'shape': {
                                'shapeType': 'TEXT_BOX',
                                'text': {
                                    'textElements': [
                                        {
                                            'textRun': {
                                                'content': 'Find this text'
                                            }
                                        }
                                    ]
                                }
                            }
                        },
                        {
                            'objectId': 'text_box_2',
                            'shape': {
                                'shapeType': 'TEXT_BOX',
                                'text': {
                                    'textElements': [
                                        {
                                            'textRun': {
                                                'content': 'Other text'
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    ]
                }
            ]
        }

        # Create a specific mock for credentials
        mock_credentials = MagicMock()

        # Execute - Access the wrapped function's underlying function
        result = find_element_ids.func(
            credentials=mock_credentials,
            presentation_id="test_pres_id",
            search_string="Find this"
        )

        # Assert
        mock_get_slides.assert_called_once_with(mock_credentials)
        mock_presentation.get.assert_called_once()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], {'element_id': 'text_box_1', 'slide_id': 'slide_01'})


if __name__ == '__main__':
    unittest.main() 