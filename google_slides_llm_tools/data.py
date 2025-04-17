from google_slides_llm_tools.auth import get_slides_service, get_sheets_service
from langchain.tools import tool
import time
import os
import tempfile

@tool
def create_sheets_chart(credentials, presentation_id, slide_id, spreadsheet_id, sheet_id, chart_id, x, y, width, height):
    """
    Inserts a chart from Google Sheets into a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        spreadsheet_id (str): ID of the spreadsheet containing the chart
        sheet_id (int): ID of the sheet containing the chart
        chart_id (int): ID of the chart to insert
        x (float): X coordinate (in points) of the chart's top-left corner
        y (float): Y coordinate (in points) of the chart's top-left corner
        width (float): Width of the chart (in points)
        height (float): Height of the chart (in points)
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and slide
    """
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
                        'height': {'magnitude': height, 'unit': 'PT'},
                        'width': {'magnitude': width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x,
                        'translateY': y,
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
    
    # Export presentation as PDF
    from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
    presentation_pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, presentation_pdf_path)
    
    # Export the specific slide as PDF if we found its index
    slide_pdf_path = None
    if slide_index is not None:
        slide_pdf_path = os.path.join(tempfile.gettempdir(), f"slide_{presentation_id}_{slide_index}.pdf")
        export_slide_as_pdf(credentials, presentation_id, slide_index, slide_pdf_path)
    
    # Add PDF paths to the response
    response["presentationPdfPath"] = presentation_pdf_path
    if slide_pdf_path:
        response["slidePdfPath"] = slide_pdf_path
    
    return response

@tool
def create_table_from_sheets(credentials, presentation_id, slide_id, spreadsheet_id, sheet_name, range_name, x, y, width, height):
    """
    Creates a table in a slide using data from Google Sheets.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        spreadsheet_id (str): ID of the spreadsheet
        sheet_name (str): Name of the sheet
        range_name (str): Range of cells to import (e.g., 'A1:D10')
        x (float): X coordinate (in points) of the table's top-left corner
        y (float): Y coordinate (in points) of the table's top-left corner
        width (float): Width of the table (in points)
        height (float): Height of the table (in points)
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and slide
    """
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
        return {"error": "No data found in the specified range"}
    
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
                        'height': {'magnitude': height, 'unit': 'PT'},
                        'width': {'magnitude': width, 'unit': 'PT'},
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x,
                        'translateY': y,
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
    
    # Export presentation as PDF
    from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
    presentation_pdf_path = os.path.join(tempfile.gettempdir(), f"presentation_{presentation_id}.pdf")
    export_presentation_as_pdf(credentials, presentation_id, presentation_pdf_path)
    
    # Export the specific slide as PDF if we found its index
    slide_pdf_path = None
    if slide_index is not None:
        slide_pdf_path = os.path.join(tempfile.gettempdir(), f"slide_{presentation_id}_{slide_index}.pdf")
        export_slide_as_pdf(credentials, presentation_id, slide_index, slide_pdf_path)
    
    # Add PDF paths to the response
    response["presentationPdfPath"] = presentation_pdf_path
    if slide_pdf_path:
        response["slidePdfPath"] = slide_pdf_path
    
    return response 