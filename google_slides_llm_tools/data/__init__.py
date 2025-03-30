from ..auth import get_slides_service, get_sheets_service
from langchain.tools import tool
import time
import os
import tempfile

@tool
def create_sheets_chart(credentials, presentation_id, slide_id, spreadsheet_id, chart_id, x, y, width, height):
    """
    Adds a chart from Google Sheets to a slide.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        spreadsheet_id (str): ID of the Google Sheets spreadsheet
        chart_id (int): ID of the chart in the spreadsheet
        x (float): X coordinate (in points) of the chart's top-left corner
        y (float): Y coordinate (in points) of the chart's top-left corner
        width (float): Width of the chart (in points)
        height (float): Height of the chart (in points)
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    service = get_slides_service(credentials)
    
    # Convert points to EMUs (1 point = 12700 EMUs)
    emu_factor = 12700
    
    # Generate a unique ID for the chart
    chart_object_id = f'Chart_{int(time.time())}'
    
    # Create the request to add a Sheets chart
    requests = [
        {
            'createSheetsChart': {
                'objectId': chart_object_id,
                'spreadsheetId': spreadsheet_id,
                'chartId': chart_id,
                'linkingMode': 'LINKED',
                'elementProperties': {
                    'pageObjectId': slide_id,
                    'size': {
                        'height': {'magnitude': height * emu_factor, 'unit': 'EMU'},
                        'width': {'magnitude': width * emu_factor, 'unit': 'EMU'}
                    },
                    'transform': {
                        'scaleX': 1,
                        'scaleY': 1,
                        'translateX': x * emu_factor,
                        'translateY': y * emu_factor,
                        'unit': 'EMU'
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
    from ..export import export_presentation_as_pdf, export_slide_as_pdf
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
def create_table_from_sheets(credentials, presentation_id, slide_id, spreadsheet_id, sheet_name, 
                            range_start, range_end, x, y, width, height):
    """
    Creates a table in a slide with data from Google Sheets.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        slide_id (str): ID of the slide
        spreadsheet_id (str): ID of the Google Sheets spreadsheet
        sheet_name (str): Name of the sheet within the spreadsheet
        range_start (str): Start cell of the range (e.g., 'A1')
        range_end (str): End cell of the range (e.g., 'C5')
        x (float): X coordinate (in points) of the table's top-left corner
        y (float): Y coordinate (in points) of the table's top-left corner
        width (float): Width of the table (in points)
        height (float): Height of the table (in points)
        
    Returns:
        dict: Response from the API with paths to PDFs of the presentation and the slide
    """
    slides_service = get_slides_service(credentials)
    sheets_service = get_sheets_service(credentials)
    
    # Get data from Google Sheets
    range_name = f'{sheet_name}!{range_start}:{range_end}'
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id, range=range_name).execute()
    
    rows = result.get('values', [])
    if not rows:
        return {'error': 'No data found in the specified range'}
    
    # Determine table dimensions
    num_rows = len(rows)
    num_columns = max(len(row) for row in rows)
    
    # Generate a unique ID for the table
    table_id = f'Table_{int(time.time())}'
    
    # Create a table in the slide
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
    
    # Create the table first
    body = {'requests': requests}
    response = slides_service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Now populate the table with data
    text_requests = []
    for i, row in enumerate(rows):
        for j, cell_value in enumerate(row):
            if j < num_columns:  # Ensure we don't exceed the number of columns
                text_requests.append({
                    'insertText': {
                        'objectId': table_id,
                        'cellLocation': {
                            'rowIndex': i,
                            'columnIndex': j
                        },
                        'text': str(cell_value)
                    }
                })
    
    # Update the table with the data
    if text_requests:
        body = {'requests': text_requests}
        response = slides_service.presentations().batchUpdate(
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
    from ..export import export_presentation_as_pdf, export_slide_as_pdf
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
