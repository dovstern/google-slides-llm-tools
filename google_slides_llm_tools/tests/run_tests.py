"""
Test runner for Google Slides LLM Tools package.
"""
import unittest
import sys
import os

# Add the parent directory to path so that we can import the package
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Import all test modules
from google_slides_llm_tools.tests.test_animations import TestAnimations
from google_slides_llm_tools.tests.test_auth import TestAuthentication
from google_slides_llm_tools.tests.test_collaboration import TestCollaboration
from google_slides_llm_tools.tests.test_data import TestData
from google_slides_llm_tools.tests.test_export import TestExport
from google_slides_llm_tools.tests.test_formatting import TestFormatting
from google_slides_llm_tools.tests.test_multimedia import TestMultimedia
from google_slides_llm_tools.tests.test_slides import TestSlides
from google_slides_llm_tools.tests.test_templates import TestTemplates
from google_slides_llm_tools.tests.test_utils import TestUtils


def create_test_suite():
    """Create a test suite containing all tests."""
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestAnimations,
        TestAuthentication,
        TestCollaboration,
        TestData,
        TestExport,
        TestFormatting,
        TestMultimedia,
        TestSlides,
        TestTemplates,
        TestUtils
    ]
    
    for test_class in test_classes:
        tests = unittest.defaultTestLoader.loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    return test_suite


if __name__ == '__main__':
    # Create the test suite
    suite = create_test_suite()
    
    # Run the tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return non-zero exit code if there were failures
    sys.exit(not result.wasSuccessful()) 