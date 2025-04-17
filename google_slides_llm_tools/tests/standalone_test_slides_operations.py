"""
Unit tests for the slides_operations module.
This is a standalone test file that avoids package imports to prevent
issues with dependencies like mcp_server.py.
"""
import sys
import os
from unittest.mock import MagicMock, patch
import pytest

# Adjust sys.path to import the module directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Direct import from the module file instead of the package
from slides_operations import (
    create_presentation,
    get_presentation,
    add_slide,
    delete_slide,
    reorder_slides,
    duplicate_slide
)

@pytest.fixture
def mock_credentials():
    """Fixture for mock credentials."""
    return MagicMock()

@pytest.fixture
def mock_slides_service():
    """Fixture for mock slides service."""
    mock = MagicMock()
    
    # Setup for presentations().create()
    mock.presentations().create().execute.return_value = {
        'presentationId': 'test_presentation_id'
    }
    
    # Setup for presentations().get()
    mock.presentations().get().execute.return_value = {
        'presentationId': 'test_presentation_id',
        'title': 'Test Presentation',
        'slides': [
            {'objectId': 'slide1'},
            {'objectId': 'slide2'}
        ],
        'masters': [
            {
                'layouts': [
                    {
                        'objectId': 'layout1',
                        'layoutProperties': {'displayName': 'BLANK'}
                    }
                ]
            }
        ]
    }
    
    # Setup for presentations().batchUpdate()
    mock.presentations().batchUpdate().execute.return_value = {
        'replies': [
            {
                'createSlide': {'objectId': 'new_slide_id'}
            },
            {
                'duplicateObject': {'objectId': 'duplicated_slide_id'}
            }
        ]
    }
    
    return mock

@pytest.fixture
def mock_drive_service():
    """Fixture for mock drive service."""
    return MagicMock()

@patch('slides_operations.get_slides_service')
@patch('slides_operations.get_drive_service')
@patch('slides_operations.export_presentation_as_pdf')
def test_create_presentation(
    mock_export_pdf, mock_get_drive, mock_get_slides, 
    mock_credentials, mock_slides_service, mock_drive_service
):
    """Test creating a new presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_get_drive.return_value = mock_drive_service
    mock_export_pdf.return_value = '/tmp/test_presentation.pdf'
    
    # Execute
    result = create_presentation(mock_credentials, "Test Presentation")
    
    # Assert
    assert mock_get_slides.called
    assert mock_get_drive.called
    mock_slides_service.presentations().create.assert_called_once()
    assert result['presentationId'] == 'test_presentation_id'
    assert result['pdfPath'] == '/tmp/test_presentation.pdf'

@patch('slides_operations.get_slides_service')
def test_get_presentation(
    mock_get_slides, mock_credentials, mock_slides_service
):
    """Test getting presentation information."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    
    # Execute
    result = get_presentation(mock_credentials, "test_presentation_id")
    
    # Assert
    mock_get_slides.assert_called_once_with(mock_credentials)
    mock_slides_service.presentations().get.assert_called_once_with(
        presentationId="test_presentation_id"
    )
    assert result['presentationId'] == 'test_presentation_id'
    assert result['title'] == 'Test Presentation'

@patch('slides_operations.get_slides_service')
@patch('slides_operations.export_presentation_as_pdf')
@patch('slides_operations.export_slide_as_pdf')
def test_add_slide(
    mock_export_slide, mock_export_presentation, mock_get_slides,
    mock_credentials, mock_slides_service
):
    """Test adding a slide to a presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_export_presentation.return_value = '/tmp/test_presentation.pdf'
    mock_export_slide.return_value = '/tmp/test_slide.pdf'
    
    # Execute
    result = add_slide(mock_credentials, "test_presentation_id", "BLANK")
    
    # Assert
    mock_get_slides.assert_called_once_with(mock_credentials)
    mock_slides_service.presentations().get.assert_called_once_with(
        presentationId="test_presentation_id"
    )
    assert mock_slides_service.presentations().batchUpdate.called
    batch_update_args = mock_slides_service.presentations().batchUpdate.call_args[1]
    assert batch_update_args['presentationId'] == 'test_presentation_id'
    assert 'requests' in batch_update_args['body']
    assert result['slideId'] == 'new_slide_id'
    assert result['presentationPdfPath'] == '/tmp/test_presentation.pdf'
    assert result['slidePdfPath'] == '/tmp/test_slide.pdf'

@patch('slides_operations.get_slides_service')
@patch('slides_operations.export_presentation_as_pdf')
def test_delete_slide(
    mock_export_pdf, mock_get_slides,
    mock_credentials, mock_slides_service
):
    """Test deleting a slide from a presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_export_pdf.return_value = '/tmp/test_presentation.pdf'
    
    # Execute
    result = delete_slide(mock_credentials, "test_presentation_id", "slide1")
    
    # Assert
    mock_get_slides.assert_called_once_with(mock_credentials)
    assert mock_slides_service.presentations().batchUpdate.called
    batch_update_args = mock_slides_service.presentations().batchUpdate.call_args[1]
    assert batch_update_args['presentationId'] == 'test_presentation_id'
    assert 'requests' in batch_update_args['body']
    assert result['success'] is True
    assert result['pdfPath'] == '/tmp/test_presentation.pdf'

@patch('slides_operations.get_slides_service')
@patch('slides_operations.export_presentation_as_pdf')
def test_reorder_slides(
    mock_export_pdf, mock_get_slides,
    mock_credentials, mock_slides_service
):
    """Test reordering slides in a presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_export_pdf.return_value = '/tmp/test_presentation.pdf'
    slide_ids = ['slide1', 'slide2']
    insertion_index = 1
    
    # Execute
    result = reorder_slides(mock_credentials, "test_presentation_id", slide_ids, insertion_index)
    
    # Assert
    mock_get_slides.assert_called_once_with(mock_credentials)
    assert mock_slides_service.presentations().batchUpdate.called
    batch_update_args = mock_slides_service.presentations().batchUpdate.call_args[1]
    assert batch_update_args['presentationId'] == 'test_presentation_id'
    assert 'requests' in batch_update_args['body']
    assert result['success'] is True
    assert result['slideIds'] == slide_ids
    assert result['pdfPath'] == '/tmp/test_presentation.pdf'

@patch('slides_operations.get_slides_service')
@patch('slides_operations.export_presentation_as_pdf')
@patch('slides_operations.export_slide_as_pdf')
def test_duplicate_slide(
    mock_export_slide, mock_export_presentation, mock_get_slides,
    mock_credentials, mock_slides_service
):
    """Test duplicating a slide in a presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_export_presentation.return_value = '/tmp/test_presentation.pdf'
    mock_export_slide.return_value = '/tmp/test_slide.pdf'
    
    # Execute
    result = duplicate_slide(mock_credentials, "test_presentation_id", "slide1")
    
    # Assert
    mock_get_slides.assert_called_with(mock_credentials)
    assert mock_slides_service.presentations().get.called
    assert mock_slides_service.presentations().batchUpdate.called
    batch_update_args = mock_slides_service.presentations().batchUpdate.call_args[1]
    assert batch_update_args['presentationId'] == 'test_presentation_id'
    assert 'requests' in batch_update_args['body']
    assert result['slideId'] == 'duplicated_slide_id'
    assert result['presentationPdfPath'] == '/tmp/test_presentation.pdf'
    assert result['slidePdfPath'] == '/tmp/test_slide.pdf' 