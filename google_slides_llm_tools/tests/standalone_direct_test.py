"""
Simple direct test for slides_operations.py
This script uses direct imports and unittest to avoid the package import issues.
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from google_slides_llm_tools.auth import authenticate
from google_slides_llm_tools.slides_operations import (
    create_presentation,
    add_slide,
    duplicate_slide,
    reorder_slides,
    delete_slide
)
from googleapiclient.discovery import build

class TestSlidesOperations(unittest.TestCase):
    """Test case for slides operations functions"""
    
    @classmethod
    def setUpClass(cls):
        """Authenticate once for all tests in this class."""
        # Ensure environment variable is set or replace with your path
        credentials_path = os.environ.get('TEST_CREDENTIALS_PATH')
        if not credentials_path:
            raise unittest.SkipTest("TEST_CREDENTIALS_PATH environment variable not set.")
        cls.credentials = authenticate(credentials_path=credentials_path)
        cls.presentation_id = None
        cls.slide_id = None
        cls.new_slide_id = None

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
        """Test creating a presentation."""
        # Execute
        result = create_presentation(self.credentials, "Test Presentation Standalone")
        TestSlidesOperations.presentation_id = result['presentationId']
        print(f"Created presentation: {self.presentation_id}")
        # Assert: Check if pdfPath exists and is a string
        self.assertIn('pdfPath', result)
        self.assertIsInstance(result['pdfPath'], str)
        self.assertIsNotNone(self.presentation_id)

    def test_add_slide(self):
        """Test adding a slide."""
        self.assertIsNotNone(self.presentation_id, "Presentation must be created first")
        # Execute
        result = add_slide(self.credentials, self.presentation_id, "BLANK")
        TestSlidesOperations.slide_id = result['slideId']
        print(f"Added slide: {self.slide_id}")
        # Assert: Check PDF paths
        self.assertIn('presentationPdfPath', result)
        self.assertIsInstance(result['presentationPdfPath'], str)
        self.assertIn('slidePdfPath', result)
        self.assertIsInstance(result['slidePdfPath'], str)
        self.assertIsNotNone(self.slide_id)

    def test_duplicate_slide(self):
        """Test duplicating a slide."""
        self.assertIsNotNone(self.presentation_id, "Presentation must be created first")
        self.assertIsNotNone(self.slide_id, "Slide must be added first")
        # Execute
        result = duplicate_slide(self.credentials, self.presentation_id, self.slide_id)
        TestSlidesOperations.new_slide_id = result['slideId']
        print(f"Duplicated slide {self.slide_id} to {self.new_slide_id}")
        # Assert: Check PDF paths
        self.assertIn('presentationPdfPath', result)
        self.assertIsInstance(result['presentationPdfPath'], str)
        self.assertIn('slidePdfPath', result)
        self.assertIsInstance(result['slidePdfPath'], str)
        self.assertIsNotNone(self.new_slide_id)
        self.assertNotEqual(self.new_slide_id, self.slide_id)

    def test_reorder_slides(self):
        """Test reordering slides."""
        self.assertIsNotNone(self.presentation_id, "Presentation must be created first")
        self.assertIsNotNone(self.slide_id, "Slide must be added first")
        self.assertIsNotNone(self.new_slide_id, "Slide must be duplicated first")
        # Execute
        result = reorder_slides(self.credentials, self.presentation_id, [self.new_slide_id, self.slide_id], 0)
        print(f"Reordered slides")
        # Assert: Check PDF path and slide order
        self.assertIn('pdfPath', result)
        self.assertIsInstance(result['pdfPath'], str)
        self.assertIn('slideIds', result)
        self.assertIsInstance(result['slideIds'], list)
        # Check if the order is updated (assuming more than 2 slides initially)
        if len(result['slideIds']) > 1:
            self.assertEqual(result['slideIds'][0], self.new_slide_id)
            self.assertEqual(result['slideIds'][1], self.slide_id)

    def test_delete_slide(self):
        """Test deleting a slide."""
        self.assertIsNotNone(self.presentation_id, "Presentation must be created first")
        self.assertIsNotNone(self.new_slide_id, "Duplicated slide must exist first")
        # Execute
        result = delete_slide(self.credentials, self.presentation_id, self.new_slide_id)
        print(f"Deleted slide: {self.new_slide_id}")
        # Assert: Check PDF path and success
        self.assertIn('pdfPath', result)
        self.assertIsInstance(result['pdfPath'], str)
        self.assertTrue(result['success'])

    @classmethod
    def tearDownClass(cls):
        """Clean up by deleting the test presentation if created."""
        if cls.presentation_id:
            try:
                # Use Drive API v3 to delete the file
                drive_service = cls.credentials.authorize(build('drive', 'v3')) # Needs build import
                drive_service.files().delete(fileId=cls.presentation_id).execute()
                print(f"Deleted test presentation: {cls.presentation_id}")
            except Exception as e:
                print(f"Error deleting presentation {cls.presentation_id}: {e}")

# This conditional is only triggered when running this script directly
if __name__ == '__main__':
    # Run tests sequentially
    suite = unittest.TestSuite()
    suite.addTest(TestSlidesOperations('test_create_presentation'))
    suite.addTest(TestSlidesOperations('test_add_slide'))
    suite.addTest(TestSlidesOperations('test_duplicate_slide'))
    suite.addTest(TestSlidesOperations('test_reorder_slides'))
    suite.addTest(TestSlidesOperations('test_delete_slide'))
    
    runner = unittest.TextTestRunner(verbosity=2)
    # Run the test suite
    runner.run(suite) 