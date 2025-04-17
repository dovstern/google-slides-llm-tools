"""
Simple direct test for slides_operations.py
This script uses direct imports and unittest to avoid the package import issues.
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch

class TestSlidesOperations(unittest.TestCase):
    """Test case for slides operations functions"""
    
    def setUp(self):
        """Set up mocks before each test"""
        # Create mocks for slides service
        self.mock_slides_service = MagicMock()
        self.mock_slides_service.presentations().create().execute.return_value = {
            'presentationId': 'test_presentation_id'
        }
        self.mock_slides_service.presentations().get().execute.return_value = {
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
        self.mock_slides_service.presentations().batchUpdate().execute.return_value = {
            'replies': [
                {
                    'createSlide': {'objectId': 'new_slide_id'}
                },
                {
                    'duplicateObject': {'objectId': 'duplicated_slide_id'}
                }
            ]
        }
        
        # Create mock for drive service
        self.mock_drive_service = MagicMock()
        
        # Create mock for credentials
        self.mock_credentials = MagicMock()
        
        # Create patches
        self.patches = [
            patch('google_slides_llm_tools.slides_operations.get_slides_service', return_value=self.mock_slides_service),
            patch('google_slides_llm_tools.slides_operations.get_drive_service', return_value=self.mock_drive_service),
            patch('google_slides_llm_tools.slides_operations.export_presentation_as_pdf', return_value='/tmp/test_presentation.pdf'),
            patch('google_slides_llm_tools.slides_operations.export_slide_as_pdf', return_value='/tmp/test_slide.pdf')
        ]
        
        # Start all patches
        for p in self.patches:
            p.start()
        
        # Import the functions after patching
        from google_slides_llm_tools.slides_operations import (
            create_presentation,
            get_presentation,
            add_slide,
            delete_slide,
            reorder_slides,
            duplicate_slide
        )
        
        self.create_presentation = create_presentation
        self.get_presentation = get_presentation
        self.add_slide = add_slide
        self.delete_slide = delete_slide
        self.reorder_slides = reorder_slides
        self.duplicate_slide = duplicate_slide
    
    def tearDown(self):
        """Stop patches after each test"""
        for p in self.patches:
            p.stop()
    
    def test_create_presentation(self):
        """Test creating a new presentation."""
        result = self.create_presentation(self.mock_credentials, "Test Presentation")
        self.assertEqual(result['presentationId'], 'test_presentation_id')
        self.assertEqual(result['pdfPath'], '/tmp/test_presentation.pdf')
    
    def test_get_presentation(self):
        """Test getting presentation information."""
        result = self.get_presentation(self.mock_credentials, "test_presentation_id")
        self.assertEqual(result['presentationId'], 'test_presentation_id')
        self.assertEqual(result['title'], 'Test Presentation')
    
    def test_add_slide(self):
        """Test adding a slide to a presentation."""
        result = self.add_slide(self.mock_credentials, "test_presentation_id", "BLANK")
        self.assertEqual(result['slideId'], 'new_slide_id')
        self.assertEqual(result['presentationPdfPath'], '/tmp/test_presentation.pdf')
        self.assertEqual(result['slidePdfPath'], '/tmp/test_slide.pdf')
    
    def test_delete_slide(self):
        """Test deleting a slide from a presentation."""
        result = self.delete_slide(self.mock_credentials, "test_presentation_id", "slide1")
        self.assertTrue(result['success'])
        self.assertEqual(result['pdfPath'], '/tmp/test_presentation.pdf')
    
    def test_reorder_slides(self):
        """Test reordering slides in a presentation."""
        slide_ids = ['slide1', 'slide2']
        insertion_index = 1
        result = self.reorder_slides(self.mock_credentials, "test_presentation_id", slide_ids, insertion_index)
        self.assertTrue(result['success'])
        self.assertEqual(result['slideIds'], slide_ids)
        self.assertEqual(result['pdfPath'], '/tmp/test_presentation.pdf')
    
    def test_duplicate_slide(self):
        """Test duplicating a slide in a presentation."""
        result = self.duplicate_slide(self.mock_credentials, "test_presentation_id", "slide1")
        self.assertEqual(result['slideId'], 'duplicated_slide_id')
        self.assertEqual(result['presentationPdfPath'], '/tmp/test_presentation.pdf')
        self.assertEqual(result['slidePdfPath'], '/tmp/test_slide.pdf')

# This conditional is only triggered when running this script directly
if __name__ == '__main__':
    # Create a new test loader
    loader = unittest.TestLoader()
    # Create a test suite containing tests from TestSlidesOperations
    suite = loader.loadTestsFromTestCase(TestSlidesOperations)
    # Create a test runner
    runner = unittest.TextTestRunner(verbosity=2)
    # Run the test suite
    result = runner.run(suite) 