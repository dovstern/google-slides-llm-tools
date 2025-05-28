"""
Data module for Google Slides LLM Tools.
Provides functionality to create charts and tables from Google Sheets data.
"""

import os
import tempfile
import time
from typing import Annotated, Any, Dict, List, Optional, Tuple, Union

from langchain.tools import tool
from langchain_core.tools import InjectedToolArg
from google_slides_llm_tools.utils import get_slides_service, get_sheets_service
from google_slides_llm_tools.utils import Position
from google_slides_llm_tools.export import export_slide_as_pdf

@tool(response_format="content_and_artifact")
def create_sheets_chart(
    credentials: Annotated[Any, InjectedToolArg],
    presentation_id: Annotated[str, "ID of the presentation"],
    slide_id: Annotated[str, "ID of the slide"],
    spreadsheet_id: Annotated[str, "ID of the spreadsheet containing the chart"],
    sheet_id: Annotated[int, "ID of the sheet containing the chart"],
    chart_id: Annotated[int, "ID of the chart to insert"],
    position: Annotated[Position, "Position and size of the chart with x, y coordinates and width, height"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """Inserts a chart from Google Sheets into a slide."""
    service = get_slides_service(credentials)
    
    # Generate a unique ID for the chart
    chart_element_id = f'Chart_{int(time.time())}'
    
    # Create request to add a chart from Sheets
    requests = [
        {
            'createSheetsChart': {
                'objectId': chart_element_id,
                'spreadsheetId': spreadsheet_id,
                'chartId': chart_id,
                'linkingMode': 'LINKED',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': position.height, 'unit': 'PT'},
                        'width': {'magnitude': position.width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': position.x,
                        'translateY': position.y,
                        'unit': 'PT'
                    }
                }
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Get the slide index
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == slide_id:
            slide_index = i
            break
    
    # Export only the specific slide as PDF since this operation affects only one slide
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Added chart from spreadsheet {spreadsheet_id} to slide {slide_id}"
    
    return content, slide_artifacts

@tool(response_format="content_and_artifact")
def create_table_from_sheets(
    credentials: Annotated[Any, InjectedToolArg],
    presentation_id: Annotated[str, "ID of the presentation"],
    slide_id: Annotated[str, "ID of the slide"],
    spreadsheet_id: Annotated[str, "ID of the spreadsheet"],
    sheet_name: Annotated[str, "Name of the sheet"],
    range_name: Annotated[str, "Range of cells to import (e.g., 'A1:D10')"],
    position: Annotated[Position, "Position and size of the table with x, y coordinates and width, height"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """Creates a table in a slide using data from Google Sheets."""
    slides_service = get_slides_service(credentials)
    sheets_service = get_sheets_service(credentials)
    
    # Get data from the spreadsheet
    full_range = f"{sheet_name}!{range_name}"
    sheet_data = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=full_range
    ).execute()
    
    values = sheet_data.get('values', [])
    if not values:
        return "No data found in the specified range", []
    
    # Generate a unique ID for the table
    table_id = f'Table_{int(time.time())}'
    
    # Determine table dimensions
    num_rows = len(values)
    num_columns = max(len(row) for row in values) if values else 0
    
    # Create request to add a table
    requests = [
        {
            'createTable': {
                'objectId': table_id,
                'rows': num_rows,
                'columns': num_columns,
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': position.height, 'unit': 'PT'},
                        'width': {'magnitude': position.width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': position.x,
                        'translateY': position.y,
                        'unit': 'PT'
                    }
                }
            }
        }
    ]
    
    # Create the empty table
    body = {'requests': requests}
    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Now populate the table with data
    text_requests = []
    for row_index, row in enumerate(values):
        for col_index, cell_value in enumerate(row):
            if col_index < num_columns:  # Ensure we don't exceed table dimensions
                text_requests.append({
                    'insertText': {
                        'objectId': table_id,
                        'cellLocation': {
                            'rowIndex': row_index,
                            'columnIndex': col_index
                        },
                        'text': str(cell_value)
                    }
                })
    
    if text_requests:
        body = {'requests': text_requests}
        slides_service.presentations().batchUpdate(
            presentationId=presentation_id, body=body).execute()
    
    # Get the slide index
    presentation = slides_service.presentations().get(
        presentationId=presentation_id).execute()
    
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        if slide.get('objectId') == slide_id:
            slide_index = i
            break
    
    # Export only the specific slide as PDF since this operation affects only one slide
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Created table from {sheet_name}!{range_name} on slide {slide_id}"
    
    return content, slide_artifacts

@tool
def get_slide_data(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide to get data for"]
) -> Annotated[dict, "Slide data including object ID and page elements"]:
    """
    Retrieves detailed data for a specific slide in a presentation.
    """
    service = get_slides_service(credentials)
    
    # Get the presentation but only fetch the slides data we need
    presentation = service.presentations().get(
        presentationId=presentation_id,
        fields="slides(objectId,pageElements)"
    ).execute()
    
    # Find the slide with the matching ID
    for slide in presentation.get('slides', []):
        if slide.get('objectId') == slide_id:
            return slide
    
    # If no matching slide is found, return an empty dict
    return {}

@tool
def get_presentation_data(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"]
) -> Annotated[dict, "Full presentation data"]:
    """
    Retrieves detailed data for an entire presentation.
    """
    service = get_slides_service(credentials)
    
    # Get the complete presentation data
    presentation = service.presentations().get(
        presentationId=presentation_id
    ).execute()
    
    return presentation

@tool
def find_element_ids(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    search_string: Annotated[str, "Text to search for in elements"]
) -> Annotated[list, "IDs of elements containing the search string"]:
    """
    Finds IDs of elements containing specific text across all slides.
    """
    service = get_slides_service(credentials)
    
    # Get the presentation with specific fields to optimize the API request
    presentation = service.presentations().get(
        presentationId=presentation_id,
        fields="slides(objectId,pageElements(objectId,shape(text)))"
    ).execute()
    
    matching_element_ids = []
    
    # Search through all slides and their elements
    for slide in presentation.get('slides', []):
        for element in slide.get('pageElements', []):
            # Check if the element is a shape with text
            if 'shape' in element and 'text' in element['shape']:
                # Extract all text from textRuns
                text_content = ""
                for text_element in element['shape']['text'].get('textElements', []):
                    if 'textRun' in text_element:
                        text_content += text_element['textRun'].get('content', '')
                
                # If the search string is in the text content, add the element ID to results
                if search_string.lower() in text_content.lower():
                    matching_element_ids.append(element.get('objectId'))
    
    return matching_element_ids 