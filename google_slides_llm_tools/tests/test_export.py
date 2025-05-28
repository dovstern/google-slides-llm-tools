"""
Tests for the export module in the Google Slides LLM Tools package.
"""
import unittest
from unittest.mock import patch, MagicMock, ANY, mock_open, PropertyMock
import tempfile
import os
import io
import requests
import uuid

from google_slides_llm_tools.export import (
    export_presentation_as_pdf,
    export_slide_as_pdf,
    get_presentation_thumbnail
)
from google_slides_llm_tools.auth import get_drive_service, get_slides_service
from googleapiclient.http import MediaIoBaseDownload


class TestExport(unittest.TestCase):
    """Test cases for the export module."""

    @patch('google_slides_llm_tools.export.MediaIoBaseDownload')
    @patch('google_slides_llm_tools.export.get_drive_service')
    @patch('google_slides_llm_tools.export.io.FileIO')
    def test_export_presentation_as_pdf(self, mock_fileio, mock_get_drive, mock_media_download_init):
        """Test exporting a presentation as PDF."""
        # Setup
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        mock_files = MagicMock()
        mock_drive_service.files.return_value = mock_files
        
        mock_export_media_response = MagicMock()
        mock_files.export_media.return_value = mock_export_media_response
        
        mock_fh = MagicMock()
        mock_fileio.return_value = mock_fh

        mock_downloader = MagicMock()
        mock_downloader.next_chunk.side_effect = [(None, True)]
        mock_media_download_init.return_value = mock_downloader
        
        temp_file_path = os.path.join(tempfile.gettempdir(), "presentation_test_id.pdf")
        
        # Execute
        result = export_presentation_as_pdf(
            MagicMock(),
            "test_id",
            temp_file_path
        )
        
        # Assert
        mock_files.export_media.assert_called_once_with(
            fileId="test_id",
            mimeType="application/pdf"
        )
        mock_fileio.assert_called_once_with(temp_file_path, 'wb')
        mock_media_download_init.assert_called_once_with(mock_fh, mock_export_media_response)
        mock_downloader.next_chunk.assert_called_once()
        self.assertEqual(result[0], f"Presentation exported as PDF to {temp_file_path}")
        self.assertEqual(result[1], temp_file_path)

    @patch('google_slides_llm_tools.export.get_slides_service')
    @patch('google_slides_llm_tools.export.get_drive_service')
    @patch('google_slides_llm_tools.export.export_presentation_as_pdf')
    @patch('google_slides_llm_tools.export.PdfReader')
    @patch('google_slides_llm_tools.export.PdfWriter')
    @patch('builtins.open', new_callable=mock_open)
    @patch('google_slides_llm_tools.export.os.remove')
    def test_export_slide_as_pdf(self, mock_os_remove, mock_builtin_open, mock_pdf_writer, mock_pdf_reader, mock_export_presentation, mock_get_drive, mock_get_slides):
        """Test exporting a specific slide as PDF."""
        # Setup
        mock_drive_service = MagicMock()
        mock_get_drive.return_value = mock_drive_service
        mock_slides_service = MagicMock()
        mock_get_slides.return_value = mock_slides_service
        
        temp_full_pdf = os.path.join(tempfile.gettempdir(), f"temp_full_test_id_{uuid.uuid4()}.pdf")
        temp_slide_pdf = os.path.join(tempfile.gettempdir(), "slide_test_id_2.pdf")
        mock_export_presentation.return_value = ("Full export success", temp_full_pdf)
        
        mock_reader_instance = MagicMock()
        mock_pdf_reader.return_value = mock_reader_instance
        mock_page = MagicMock()
        mock_reader_instance.pages = [MagicMock(), MagicMock(), mock_page, MagicMock(), MagicMock()]
        
        mock_writer_instance = MagicMock()
        mock_pdf_writer.return_value = mock_writer_instance
        
        mock_output_fh = mock_builtin_open.return_value

        # Execute
        result = export_slide_as_pdf(
            MagicMock(),
            "test_id",
            2,
            temp_slide_pdf
        )
        
        # Assert
        mock_export_presentation.assert_called_once_with(ANY, "test_id", temp_full_pdf)
        mock_pdf_reader.assert_called_once_with(temp_full_pdf)
        mock_writer_instance.add_page.assert_called_once_with(mock_page)
        mock_builtin_open.assert_called_once_with(temp_slide_pdf, 'wb')
        mock_writer_instance.write.assert_called_once_with(mock_output_fh)
        mock_os_remove.assert_called_once_with(temp_full_pdf)
        self.assertEqual(result[0], f"Slide 3 exported as PDF to {temp_slide_pdf}")
        self.assertEqual(result[1], temp_slide_pdf)

    @patch('google_slides_llm_tools.export.requests.get')
    @patch('google_slides_llm_tools.export.get_slides_service')
    @patch('builtins.open', new_callable=mock_open)
    @patch('google_slides_llm_tools.export.base64.b64encode')
    def test_get_presentation_thumbnail(self, mock_b64encode, mock_file, mock_get_slides, mock_requests_get):
        """Test getting a presentation thumbnail."""
        # Setup
        mock_slides_service = MagicMock()
        mock_get_slides.return_value = mock_slides_service
        
        mock_presentation = MagicMock()
        mock_presentation.execute.return_value = {
            'slides': [
                {'objectId': 'slide_id_0'},
                {'objectId': 'slide_id_1'},
                {'objectId': 'slide_id_2'}
            ]
        }
        mock_slides_service.presentations().get.return_value = mock_presentation

        mock_pages = MagicMock()
        mock_slides_service.presentations().pages.return_value = mock_pages

        mock_get_thumbnail = MagicMock()
        mock_pages.getThumbnail = mock_get_thumbnail
        
        mock_thumbnail_result = MagicMock()
        mock_thumbnail_result.execute.return_value = {
            'contentUrl': 'https://example.com/thumbnail.jpg'
        }
        mock_get_thumbnail.return_value = mock_thumbnail_result
        
        mock_response = MagicMock()
        mock_response.content = b'image_data'
        mock_requests_get.return_value = mock_response
        
        temp_file = os.path.join(tempfile.gettempdir(), "thumbnail_test_id.jpg")
        mock_fh = mock_file.return_value
        
        # Execute
        result = get_presentation_thumbnail(
            MagicMock(),
            "test_id",
            1,
            temp_file
        )
        
        # Assert
        mock_get_slides.assert_called_once_with(ANY)
        mock_slides_service.presentations().get.assert_called_once_with(presentationId="test_id")
        mock_pages.getThumbnail.assert_called_once_with(
            presentationId="test_id",
            pageObjectId='slide_id_1'
        )
        mock_requests_get.assert_called_once_with('https://example.com/thumbnail.jpg')
        mock_file.assert_called_once_with(temp_file, 'wb')
        mock_fh.write.assert_called_once_with(b'image_data')
        expected_content = f"Thumbnail of slide 2 saved to {temp_file}"
        self.assertEqual(result, (expected_content, temp_file))


if __name__ == '__main__':
    unittest.main() 