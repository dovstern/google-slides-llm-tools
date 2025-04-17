"""
Tests for the export module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY, mock_open
import tempfile
import os
import io

from google_slides_llm_tools import (
    export_presentation_as_pdf,
    export_slide_as_pdf,
    get_presentation_thumbnail
)


class TestExport(unittest.TestCase):
    """Test cases for the export module."""

    @patch('google_slides_llm_tools.export.MediaIoBaseDownload')
    def test_export_presentation_as_pdf(self, mock_media_download):
        """Test exporting a presentation as PDF."""
        # Setup
        mock_drive_service = MagicMock()
        mock_files = MagicMock()
        mock_drive_service.files.return_value = mock_files
        
        mock_export = MagicMock()
        mock_files.export = mock_export
        
        mock_export_response = MagicMock()
        mock_export.return_value = mock_export_response
        
        mock_downloader = MagicMock()
        mock_media_download.return_value = mock_downloader
        
        # Mock the download process
        mock_downloader.next_chunk.side_effect = [(None, True)]
        
        temp_file = os.path.join(tempfile.gettempdir(), "presentation_test_id.pdf")
        
        # Execute
        with patch('google_slides_llm_tools.export.get_drive_service', return_value=mock_drive_service), \
             patch('builtins.open', mock_open()) as mock_file:
            result = export_presentation_as_pdf(
                MagicMock(),
                "test_id",
                temp_file
            )
        
        # Assert
        mock_export.assert_called_once_with(
            fileId="test_id",
            mimeType="application/pdf"
        )
        mock_media_download.assert_called_once()
        mock_downloader.next_chunk.assert_called_once()
        mock_file.assert_called_once_with(temp_file, 'wb')
        self.assertEqual(result, temp_file)

    @patch('google_slides_llm_tools.export.export_presentation_as_pdf')
    @patch('PyPDF2.PdfReader')
    @patch('PyPDF2.PdfWriter')
    def test_export_slide_as_pdf(self, mock_pdf_writer, mock_pdf_reader, mock_export_presentation):
        """Test exporting a specific slide as PDF."""
        # Setup
        temp_full_pdf = os.path.join(tempfile.gettempdir(), "presentation_test_id.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_id_2.pdf")
        mock_export_presentation.return_value = temp_full_pdf
        
        # Mock PDF reader and writer
        mock_reader = MagicMock()
        mock_pdf_reader.return_value = mock_reader
        mock_reader.__len__.return_value = 5
        
        mock_page = MagicMock()
        mock_reader.pages = [MagicMock(), MagicMock(), mock_page, MagicMock(), MagicMock()]
        
        mock_writer = MagicMock()
        mock_pdf_writer.return_value = mock_writer
        
        # Execute
        with patch('builtins.open', mock_open()):
            result = export_slide_as_pdf(
                MagicMock(),
                "test_id",
                2,  # 0-indexed, so this is the third slide
                temp_slide_pdf
            )
        
        # Assert
        mock_export_presentation.assert_called_once_with(MagicMock(), "test_id", temp_full_pdf)
        mock_pdf_reader.assert_called_once_with(temp_full_pdf)
        mock_writer.add_page.assert_called_once_with(mock_page)
        mock_writer.write.assert_called_once()
        self.assertEqual(result, temp_slide_pdf)

    @patch('google_slides_llm_tools.export.MediaIoBaseDownload')
    def test_get_presentation_thumbnail(self, mock_media_download):
        """Test getting a presentation thumbnail."""
        # Setup
        mock_slides_service = MagicMock()
        mock_presentations = MagicMock()
        mock_slides_service.presentations.return_value = mock_presentations
        
        mock_get_thumbnail = MagicMock()
        mock_presentations.getThumbnail = mock_get_thumbnail
        
        mock_thumbnail_response = MagicMock()
        mock_get_thumbnail.return_value = mock_thumbnail_response
        
        mock_thumbnail_result = MagicMock()
        mock_thumbnail_result.execute.return_value = {
            'contentUrl': 'https://example.com/thumbnail.jpg'
        }
        mock_thumbnail_response.execute.return_value = mock_thumbnail_result
        
        # Mock the download process
        mock_downloader = MagicMock()
        mock_media_download.return_value = mock_downloader
        mock_downloader.next_chunk.side_effect = [(None, True)]
        
        temp_file = os.path.join(tempfile.gettempdir(), "thumbnail_test_id.jpg")
        
        # Execute
        with patch('google_slides_llm_tools.export.get_slides_service', return_value=mock_slides_service), \
             patch('google_slides_llm_tools.export.requests.get') as mock_get, \
             patch('builtins.open', mock_open()) as mock_file:
            # Mock the HTTP response
            mock_response = MagicMock()
            mock_response.content = b'image_data'
            mock_get.return_value = mock_response
            
            result = get_presentation_thumbnail(
                MagicMock(),
                "test_id",
                temp_file,
                1  # Scale factor
            )
        
        # Assert
        mock_get_thumbnail.assert_called_once_with(
            presentationId="test_id",
            thumbnailProperties_thumbnailSize="MEDIUM",
            thumbnailProperties_scaleFactor=1
        )
        mock_get.assert_called_once_with('https://example.com/thumbnail.jpg')
        mock_file.assert_called_once_with(temp_file, 'wb')
        mock_file().write.assert_called_once_with(b'image_data')
        self.assertEqual(result, temp_file)


if __name__ == '__main__':
    unittest.main() 