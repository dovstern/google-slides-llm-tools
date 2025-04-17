"""
Tests for the utils module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY
import tempfile
import os

from google_slides_llm_tools import (
    slide_id_to_index,
    index_to_slide_id,
    get_element_id_by_name,
    rgb_to_hex,
    hex_to_rgb,
    points_to_emu,
    emu_to_points,
    get_page_size
)


class TestUtils(unittest.TestCase):
    """Test cases for the utils module."""

    def test_slide_id_to_index(self):
        """Test converting a slide ID to its index."""
        # Setup
        mock_service = MagicMock()
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_get = MagicMock()
        mock_slides.get = mock_get
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'slide1'},
                {'objectId': 'slide2'},
                {'objectId': 'slide_id_123'},
                {'objectId': 'slide4'}
            ]
        }
        mock_get.return_value = mock_presentation
        
        # Execute
        with patch('google_slides_llm_tools.utils.get_slides_service', return_value=mock_service):
            result = slide_id_to_index(
                MagicMock(),
                "test_presentation_id",
                "slide_id_123"
            )
        
        # Assert
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        self.assertEqual(result, 2)  # 0-indexed, so the third slide is index 2

    def test_index_to_slide_id(self):
        """Test converting an index to a slide ID."""
        # Setup
        mock_service = MagicMock()
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_get = MagicMock()
        mock_slides.get = mock_get
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'slide1'},
                {'objectId': 'slide2'},
                {'objectId': 'slide_id_123'},
                {'objectId': 'slide4'}
            ]
        }
        mock_get.return_value = mock_presentation
        
        # Execute
        with patch('google_slides_llm_tools.utils.get_slides_service', return_value=mock_service):
            result = index_to_slide_id(
                MagicMock(),
                "test_presentation_id",
                2  # 0-indexed, so the third slide
            )
        
        # Assert
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        self.assertEqual(result, "slide_id_123")

    def test_get_element_id_by_name(self):
        """Test getting an element ID by its name."""
        # Setup
        mock_service = MagicMock()
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_get = MagicMock()
        mock_slides.get = mock_get
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {
                    'objectId': 'slide1',
                    'pageElements': [
                        {
                            'objectId': 'element1',
                            'title': 'Title Element'
                        },
                        {
                            'objectId': 'element_id_456',
                            'title': 'Target Element'
                        }
                    ]
                }
            ]
        }
        mock_get.return_value = mock_presentation
        
        # Execute
        with patch('google_slides_llm_tools.utils.get_slides_service', return_value=mock_service):
            result = get_element_id_by_name(
                MagicMock(),
                "test_presentation_id",
                "Target Element"
            )
        
        # Assert
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        self.assertEqual(result, "element_id_456")

    def test_rgb_to_hex(self):
        """Test converting RGB to hex."""
        # Test cases
        test_cases = [
            # (r, g, b) -> expected hex
            ((255, 255, 255), "#ffffff"),
            ((0, 0, 0), "#000000"),
            ((255, 0, 0), "#ff0000"),
            ((0, 255, 0), "#00ff00"),
            ((0, 0, 255), "#0000ff"),
            ((128, 128, 128), "#808080")
        ]
        
        for rgb, expected_hex in test_cases:
            result = rgb_to_hex(*rgb)
            self.assertEqual(result, expected_hex)

    def test_hex_to_rgb(self):
        """Test converting hex to RGB."""
        # Test cases
        test_cases = [
            # hex -> expected (r, g, b)
            ("#ffffff", (1.0, 1.0, 1.0)),
            ("#000000", (0.0, 0.0, 0.0)),
            ("#ff0000", (1.0, 0.0, 0.0)),
            ("#00ff00", (0.0, 1.0, 0.0)),
            ("#0000ff", (0.0, 0.0, 1.0)),
            ("#808080", (0.5019607843137255, 0.5019607843137255, 0.5019607843137255))
        ]
        
        for hex_color, expected_rgb in test_cases:
            result = hex_to_rgb(hex_color)
            
            # Compare with some tolerance due to floating point precision
            self.assertAlmostEqual(result['red'], expected_rgb[0], places=6)
            self.assertAlmostEqual(result['green'], expected_rgb[1], places=6)
            self.assertAlmostEqual(result['blue'], expected_rgb[2], places=6)

    def test_points_to_emu(self):
        """Test converting points to EMU."""
        # Test cases
        test_cases = [
            # points -> expected EMU
            (1, 12700),
            (10, 127000),
            (72, 914400)  # 1 inch = 72 points = 914400 EMU
        ]
        
        for points, expected_emu in test_cases:
            result = points_to_emu(points)
            self.assertEqual(result, expected_emu)

    def test_emu_to_points(self):
        """Test converting EMU to points."""
        # Test cases
        test_cases = [
            # EMU -> expected points
            (12700, 1),
            (127000, 10),
            (914400, 72)  # 914400 EMU = 72 points = 1 inch
        ]
        
        for emu, expected_points in test_cases:
            result = emu_to_points(emu)
            self.assertEqual(result, expected_points)

    def test_get_page_size(self):
        """Test getting a presentation's page size."""
        # Setup
        mock_service = MagicMock()
        mock_slides = MagicMock()
        mock_service.presentations.return_value = mock_slides
        
        mock_get = MagicMock()
        mock_slides.get = mock_get
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'pageSize': {
                'width': {'magnitude': 9144000, 'unit': 'EMU'},  # 720 points
                'height': {'magnitude': 5143500, 'unit': 'EMU'}  # 405 points
            }
        }
        mock_get.return_value = mock_presentation
        
        # Execute
        with patch('google_slides_llm_tools.utils.get_slides_service', return_value=mock_service):
            result = get_page_size(
                MagicMock(),
                "test_presentation_id"
            )
        
        # Assert
        mock_get.assert_called_once_with(presentationId="test_presentation_id")
        self.assertEqual(result, {'width': 720, 'height': 405})


if __name__ == '__main__':
    unittest.main() 