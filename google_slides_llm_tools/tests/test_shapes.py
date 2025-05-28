import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

# Import from multimedia module where the functions are implemented
from google_slides_llm_tools.multimedia import (
    create_shape,
    group_elements,
    ungroup_elements    
)

# Import necessary functions from other modules for patching
from google_slides_llm_tools.auth import get_slides_service

class TestShapes(unittest.TestCase):
    """Test cases for the shape manipulation functions.""" 

    @patch('google_slides_llm_tools.multimedia.get_slides_service')
    def test_create_shape(self, mock_get_slides):
        """Test creating a shape on a slide."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_batch_update = MagicMock()
        mock_slides.batchUpdate = mock_batch_update
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            "replies": [{"createShape": {"objectId": "new_shape_id"}}]
        }
        mock_batch_update.return_value = mock_response
        
        # Execute
        result = create_shape(
            credentials=MagicMock(),
            presentation_id="test_presentation_id",
            slide_id="test_slide_id",
            shape_type="RECTANGLE",
            x=200, y=200, width=100, height=100
        )
        
        # Assert
        mock_get_slides.assert_called_once_with(ANY)
        mock_batch_update.assert_called_once()
        self.assertEqual(result["objectId"], "new_shape_id")

    @patch('google_slides_llm_tools.multimedia.get_slides_service')
    def test_group_elements(self, mock_get_slides):
        """Test grouping elements on a slide."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_batch_update = MagicMock()
        mock_slides.batchUpdate = mock_batch_update
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {
            "replies": [{"createGroup": {"objectId": "new_group_id"}}]
        }
        mock_batch_update.return_value = mock_response
        
        # Execute
        result = group_elements(
            credentials=MagicMock(),
            presentation_id="test_presentation_id",
            element_ids=["shape1", "shape2", "text1"]
        )
        
        # Assert
        mock_get_slides.assert_called_once_with(ANY)
        mock_batch_update.assert_called_once()
        self.assertEqual(result["groupId"], "new_group_id")

    @patch('google_slides_llm_tools.multimedia.get_slides_service')
    def test_ungroup_elements(self, mock_get_slides):
        """Test ungrouping elements on a slide."""
        # Setup
        mock_service = MagicMock()
        mock_get_slides.return_value = mock_service
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_batch_update = MagicMock()
        mock_slides.batchUpdate = mock_batch_update
        
        mock_response = MagicMock()
        mock_response.execute.return_value = {}
        mock_batch_update.return_value = mock_response
        
        # Execute
        result = ungroup_elements(
            credentials=MagicMock(),
            presentation_id="test_presentation_id",
            group_id="group_to_ungroup"
        )
        
        # Assert
        mock_get_slides.assert_called_once_with(ANY)
        mock_batch_update.assert_called_once()
        self.assertEqual(result, {}) # Expecting empty dict on success

if __name__ == '__main__':
    unittest.main() 