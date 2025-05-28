"""
Formatting module for Google Slides LLM Tools.
Provides functionality for text and paragraph formatting.
"""
import os
import tempfile
import uuid
import time
from typing import Annotated, Any, Dict, List, Optional, Tuple, Literal

from langchain.tools import tool
from langchain_core.tools import InjectedToolArg
from google_slides_llm_tools.utils import get_slides_service
from google_slides_llm_tools.export import export_presentation_as_pdf, export_slide_as_pdf
from google_slides_llm_tools.utils import Position, TextStyle, ParagraphStyle

@tool(response_format="content_and_artifact")
def add_text_to_slide(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_id: Annotated[str, "ID of the slide"], 
    text: Annotated[str, "Text content to add"], 
    position: Annotated[Optional[Position], "Position and size of the text box with keys: x, y, width, height (in points)"] = None
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Adds text to a slide.
    """
    service = get_slides_service(credentials)
    
    # Set default position if none provided
    if position is None:
        position = Position(x=100, y=100, width=400, height=100)
    
    # Generate a unique ID for the text box
    text_box_id = f'TextBox_{int(time.time())}'
    
    # Create requests to add a text box and insert text
    requests = [
        {
            'createShape': {
                'objectId': text_box_id,
                'shapeType': 'TEXT_BOX',
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
        },
        {
            'insertText': {
                'objectId': text_box_id,
                'text': text
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
    
    content = f"Added text '{text}' to slide {slide_id}"
    
    return content, slide_artifacts

@tool(response_format="content_and_artifact")
def update_text_style(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_object_id: Annotated[str, "ID of the text box or shape containing the text"], 
    text_style: Annotated[TextStyle, "Style to apply with keys: fontFamily, fontSize, bold, italic, underline, foregroundColor, backgroundColor"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Updates the style of text in a text box or shape.
    """
    service = get_slides_service(credentials)
    
    # Build style fields to update
    style = {}
    fields = []
    
    if text_style.bold:
        style['bold'] = True
        fields.append('bold')
        
    if text_style.italic:
        style['italic'] = True
        fields.append('italic')
        
    if text_style.fontSize:
        style['fontSize'] = {
            'magnitude': text_style.fontSize,
            'unit': 'PT'
        }
        fields.append('fontSize')
        
    if text_style.fontFamily:
        style['fontFamily'] = text_style.fontFamily
        fields.append('fontFamily')
        
    if text_style.foregroundColor:
        style['foregroundColor'] = {
            'opaqueColor': {
                'rgbColor': {
                    'red': text_style.foregroundColor.red,
                    'green': text_style.foregroundColor.green,
                    'blue': text_style.foregroundColor.blue
                }
            }
        }
        fields.append('foregroundColor')
    
    # Create the update request
    requests = [
        {
            'updateTextStyle': {
                'objectId': slide_object_id,
                'style': style,
                'fields': ','.join(fields)
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Find which slide contains this shape
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        for element in slide.get('pageElements', []):
            if element.get('objectId') == slide_object_id:
                slide_index = i
                break
        if slide_index is not None:
            break
    
    # Export only the specific slide as PDF since this operation affects only one slide
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Updated text style for object {slide_object_id}"
    
    return content, slide_artifacts

@tool(response_format="content_and_artifact")
def update_paragraph_style(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    slide_object_id: Annotated[str, "ID of the text box or shape containing the text"], 
    paragraph_style: Annotated[ParagraphStyle, "Style to apply with keys: alignment, lineSpacing, spaceAbove, spaceBelow, indentFirstLine, indentStart, indentEnd, direction, spacingMode"]
) -> Annotated[Tuple[str, List[Dict[str, Any]]], "Tuple of (content message, artifacts) with response and PDFs"]:
    """
    Updates the paragraph style in a text box or shape.
    """
    service = get_slides_service(credentials)
    
    # Build style fields to update
    style = {}
    fields = []
    
    if paragraph_style.alignment:
        style['alignment'] = paragraph_style.alignment
        fields.append('alignment')
        
    if paragraph_style.lineSpacing:
        style['lineSpacing'] = {
            'magnitude': paragraph_style.lineSpacing,
            'unit': 'PERCENT'
        }
        fields.append('lineSpacing')
        
    if paragraph_style.spaceAbove:
        style['spaceAbove'] = {
            'magnitude': paragraph_style.spaceAbove,
            'unit': 'PT'
        }
        fields.append('spaceAbove')
        
    if paragraph_style.spaceBelow:
        style['spaceBelow'] = {
            'magnitude': paragraph_style.spaceBelow,
            'unit': 'PT'
        }
        fields.append('spaceBelow')
        
    if paragraph_style.indentFirstLine:
        style['indentFirstLine'] = {
            'magnitude': paragraph_style.indentFirstLine,
            'unit': 'PT'
        }
        fields.append('indentFirstLine')
        
    if paragraph_style.indentStart:
        style['indentStart'] = {
            'magnitude': paragraph_style.indentStart,
            'unit': 'PT'
        }
        fields.append('indentStart')
        
    if paragraph_style.indentEnd:
        style['indentEnd'] = {
            'magnitude': paragraph_style.indentEnd,
            'unit': 'PT'
        }
        fields.append('indentEnd')
    
    # Create the update request
    requests = [
        {
            'updateParagraphStyle': {
                'objectId': slide_object_id,
                'style': style,
                'fields': ','.join(fields)
            }
        }
    ]
    
    body = {'requests': requests}
    response = service.presentations().batchUpdate(
        presentationId=presentation_id, body=body).execute()
    
    # Find which slide contains this shape
    presentation = service.presentations().get(
        presentationId=presentation_id).execute()
    
    slide_index = None
    for i, slide in enumerate(presentation.get('slides', [])):
        for element in slide.get('pageElements', []):
            if element.get('objectId') == slide_object_id:
                slide_index = i
                break
        if slide_index is not None:
            break
    
    
    # Export the specific slide as PDF if we found its index
    slide_artifacts = []
    if slide_index is not None:
        _, slide_artifacts = export_slide_as_pdf(credentials, presentation_id, slide_index)
    
    content = f"Updated paragraph style for object {slide_object_id}"
    
    return content, slide_artifacts 