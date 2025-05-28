"""
Unit tests for the slides_operations module.
"""
import pytest
from unittest.mock import MagicMock, patch, ANY
from google_slides_llm_tools.slides_operations import (
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
    """Fixture for mock slides service.
    Returns a plain MagicMock. Behavior should be configured within each test.
    """
    return MagicMock()
    # Removed pre-configuration of create/get/batchUpdate execute results

@pytest.fixture
def mock_drive_service():
    """Fixture for mock drive service."""
    return MagicMock()

@patch('google_slides_llm_tools.slides_operations.get_slides_service')
@patch('google_slides_llm_tools.slides_operations.get_drive_service')
@patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
def test_create_presentation(
    mock_export_pdf, mock_get_drive, mock_get_slides, 
    mock_credentials, mock_slides_service, mock_drive_service
):
    """Test creating a new presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_get_drive.return_value = mock_drive_service
    mock_export_pdf.return_value = (None, '/tmp/test_presentation.pdf')
    
    # Configure mock behavior INSIDE the test
    mock_slides_service.presentations().create().execute.return_value = {
        'presentationId': 'test_presentation_id'
    }
    
    # Execute
    result = create_presentation(mock_credentials, "Test Presentation")
    
    # Assert
    assert mock_get_slides.called
    assert mock_get_drive.called
    # Now assert_called_once should pass as setup calls don't interfere
    mock_slides_service.presentations().create.assert_called_once_with(body={'title': 'Test Presentation'})
    mock_export_pdf.assert_called_once_with(ANY, "test_presentation_id")
    assert result['presentationId'] == 'test_presentation_id'
    assert result['pdfPath'] == '/tmp/test_presentation.pdf'

@patch('google_slides_llm_tools.slides_operations.get_slides_service')
def test_get_presentation(
    mock_get_slides, mock_credentials, mock_slides_service
):
    """Test getting presentation information."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    
    # Configure mock behavior INSIDE the test
    mock_slides_service.presentations().get().execute.return_value = {
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

    # Execute
    result = get_presentation(mock_credentials, "test_presentation_id")
    
    # Assert
    mock_get_slides.assert_called_once_with(mock_credentials)
    # Now assert_called_once should pass
    mock_slides_service.presentations().get.assert_called_once_with(
        presentationId="test_presentation_id"
    )
    assert result['presentationId'] == 'test_presentation_id'
    assert result['title'] == 'Test Presentation'

@patch('google_slides_llm_tools.slides_operations.get_slides_service')
@patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
@patch('google_slides_llm_tools.slides_operations.export_slide_as_pdf')
def test_add_slide(
    mock_export_slide, mock_export_presentation, mock_get_slides,
    mock_credentials, mock_slides_service
):
    """Test adding a slide to a presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_export_presentation.return_value = (None, '/tmp/test_presentation.pdf')
    mock_export_slide.return_value = (None, '/tmp/test_slide.pdf')
    
    # Configure mock behavior INSIDE the test
    # Mock presentations().get() for layout and final state
    mock_slides_service.presentations().get.side_effect = [
        MagicMock(execute=MagicMock(return_value={
            'masters': [
                {'layouts': [
                    {'objectId': 'layout_id_1', 'layoutProperties': {'displayName': 'TITLE'}},
                    {'objectId': 'layout_id_2', 'layoutProperties': {'displayName': 'BLANK'}}
                ]}
            ]
        })), 
        MagicMock(execute=MagicMock(return_value={})) # Call after batchUpdate (may not be strictly necessary depending on exact logic)
    ]
    
    # Mock batchUpdate response
    mock_slides_service.presentations().batchUpdate().execute.return_value = {
        'replies': [{'createSlide': {'objectId': 'new_slide_id'}}]
    }

    # Execute
    result = add_slide(mock_credentials, "test_presentation_id", "BLANK")
    
    # Assert
    mock_get_slides.assert_called_once_with(mock_credentials)
    # Check get() calls 
    assert mock_slides_service.presentations().get.call_count >= 1 # Called at least once for layout
    mock_slides_service.presentations().get.assert_any_call(presentationId="test_presentation_id")
    mock_slides_service.presentations().batchUpdate.assert_called_once() # Check batchUpdate call
    # Check export calls
    mock_export_presentation.assert_called_once_with(ANY, "test_presentation_id")
    mock_export_slide.assert_called_once_with(ANY, "test_presentation_id", 1) # New slide is at index 1
    assert result['slideId'] == 'new_slide_id'
    assert result['presentationPdfPath'] == '/tmp/test_presentation.pdf'
    assert result['slidePdfPath'] == '/tmp/test_slide.pdf'

@patch('google_slides_llm_tools.slides_operations.get_slides_service')
@patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
def test_delete_slide(
    mock_export_pdf, mock_get_slides,
    mock_credentials, mock_slides_service
):
    """Test deleting a slide from a presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_export_pdf.return_value = (None, '/tmp/test_presentation.pdf')
    # Configure mock behavior INSIDE the test
    mock_slides_service.presentations().batchUpdate().execute.return_value = {} # Delete returns empty

    # Execute
    result = delete_slide(mock_credentials, "test_presentation_id", "slide1")
    
    # Assert
    mock_get_slides.assert_called_once_with(mock_credentials)
    mock_slides_service.presentations().batchUpdate.assert_called_once() # Check call count
    batch_update_args, batch_update_kwargs = mock_slides_service.presentations().batchUpdate.call_args
    assert batch_update_kwargs['presentationId'] == 'test_presentation_id'
    assert 'requests' in batch_update_kwargs['body']
    assert batch_update_kwargs['body']['requests'][0]['deleteObject']['objectId'] == 'slide1'
    assert result['success'] is True
    assert result['pdfPath'] == '/tmp/test_presentation.pdf'

@patch('google_slides_llm_tools.slides_operations.get_slides_service')
@patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
def test_reorder_slides(
    mock_export_pdf, mock_get_slides,
    mock_credentials, mock_slides_service
):
    """Test reordering slides in a presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_export_pdf.return_value = (None, '/tmp/test_presentation.pdf')
    slide_ids = ['slide1', 'slide2']
    insertion_index = 1

    # Configure mock behavior INSIDE the test
    mock_slides_service.presentations().batchUpdate().execute.return_value = {} # Reorder returns empty
    mock_slides_service.presentations().get().execute.return_value = {
        'slides': [ # Simulate state *after* reorder
            {'objectId': 'slide_other'},
            {'objectId': 'slide1'}, 
            {'objectId': 'slide2'}
        ]
    }

    # Execute
    result = reorder_slides(mock_credentials, "test_presentation_id", slide_ids, insertion_index)
    
    # Assert
    mock_get_slides.assert_called_once_with(mock_credentials)
    mock_slides_service.presentations().batchUpdate.assert_called_once() # Check call count
    batch_update_args, batch_update_kwargs = mock_slides_service.presentations().batchUpdate.call_args
    assert batch_update_kwargs['presentationId'] == 'test_presentation_id'
    assert batch_update_kwargs['body']['requests'][0]['updateSlidesPosition']['slideObjectIds'] == slide_ids
    mock_slides_service.presentations().get.assert_called_once_with(presentationId='test_presentation_id') # Called after reorder
    assert result['slideIds'] == ['slide_other', 'slide1', 'slide2']
    assert 'pdfPath' in result
    assert result['pdfPath'] == '/tmp/test_presentation.pdf'

@patch('google_slides_llm_tools.slides_operations.get_slides_service')
@patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf')
@patch('google_slides_llm_tools.slides_operations.export_slide_as_pdf')
def test_duplicate_slide(
    mock_export_slide, mock_export_presentation, mock_get_slides,
    mock_credentials, mock_slides_service
):
    """Test duplicating a slide in a presentation."""
    # Setup
    mock_get_slides.return_value = mock_slides_service
    mock_export_presentation.return_value = (None, '/tmp/test_presentation.pdf')
    mock_export_slide.return_value = (None, '/tmp/test_slide.pdf')
    
    # Configure mock behavior INSIDE the test
    # Mock batchUpdate response for duplicateObject
    mock_slides_service.presentations().batchUpdate().execute.return_value = {
        'replies': [{'duplicateObject': {'objectId': 'duplicated_slide_id'}}]
    }
    
    # Mock presentations().get() for original and final state
    mock_slides_service.presentations().get.side_effect = [
        MagicMock(execute=MagicMock(return_value={
            'slides': [
                {'objectId': 'slide1'}, # Original slide at index 0
                {'objectId': 'slide2'}
            ]
        })), # First call for original index
        MagicMock(execute=MagicMock(return_value={
            'slides': [
                {'objectId': 'slide1'},
                {'objectId': 'slide2'},
                {'objectId': 'duplicated_slide_id'} # New slide after duplication (index 2)
            ]
        })) # Second call for new index
    ]

    # Execute
    result = duplicate_slide(mock_credentials, "test_presentation_id", "slide1")
    
    # Assert
    mock_get_slides.assert_called_with(mock_credentials)
    # Check get() calls
    assert mock_slides_service.presentations().get.call_count == 2
    mock_slides_service.presentations().get.assert_any_call(presentationId="test_presentation_id")
    # Check batchUpdate call
    mock_slides_service.presentations().batchUpdate.assert_called_once()
    batch_update_args, batch_update_kwargs = mock_slides_service.presentations().batchUpdate.call_args
    assert batch_update_kwargs['presentationId'] == 'test_presentation_id'
    assert batch_update_kwargs['body']['requests'][0]['duplicateObject']['objectId'] == 'slide1'
    # Assert export calls
    mock_export_presentation.assert_called_once_with(ANY, "test_presentation_id")
    # New slide 'duplicated_slide_id' is at index 2
    mock_export_slide.assert_called_once_with(ANY, "test_presentation_id", 2)
    # Check results
    assert result['slideId'] == 'duplicated_slide_id'
    assert result['presentationPdfPath'] == '/tmp/test_presentation.pdf'
    assert result['slidePdfPath'] == '/tmp/test_slide.pdf'