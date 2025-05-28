"""
Collaboration module for Google Slides LLM Tools.
Provides functionality to manage permissions and sharing for presentations.
"""

from typing import Annotated, Any, Dict, List, Optional, Union
from google_slides_llm_tools.utils import get_drive_service
from langchain.tools import tool
from langchain_core.tools import InjectedToolArg

@tool
def add_editor_permission(
    credentials: Annotated[str, "Authorized Google credentials"], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    email: Annotated[str, "Email address of the user to grant access"]
) -> Annotated[dict, "Response from the API"]:
    """
    Gives editor permission to a user for a presentation.
    """
    drive_service = get_drive_service(credentials)
    
    user_permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': email
    }
    
    response = drive_service.permissions().create(
        fileId=presentation_id,
        body=user_permission,
        sendNotificationEmail=True
    ).execute()
    
    return {
        "permissionId": response['id'],
        "message": f"Editor permission granted to {email}"
    }

@tool
def add_viewer_permission(
    credentials: Annotated[str, "Authorized Google credentials"], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    email: Annotated[str, "Email address of the user to grant access"]
) -> Annotated[dict, "Response from the API"]:
    """
    Gives viewer permission to a user for a presentation.
    """
    drive_service = get_drive_service(credentials)
    
    user_permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': email
    }
    
    response = drive_service.permissions().create(
        fileId=presentation_id,
        body=user_permission,
        sendNotificationEmail=True
    ).execute()
    
    return {
        "permissionId": response['id'],
        "message": f"Viewer permission granted to {email}"
    }

@tool
def add_commenter_permission(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    email: Annotated[str, "Email address of the user to grant comment permission"]
) -> Annotated[Dict[str, str], "Response containing permission details"]:
    """
    Grants comment permission to a user for a presentation.
    """
    drive_service = get_drive_service(credentials)
    
    permission = {
        'type': 'user',
        'role': 'commenter',
        'emailAddress': email
    }
    
    response = drive_service.permissions().create(
        fileId=presentation_id,
        body=permission,
        sendNotificationEmail=True
    ).execute()
    
    return {
        "permissionId": response.get('id'),
        "email": email,
        "role": "commenter"
    }

@tool
def remove_permission(
    credentials: Annotated[str, "Authorized Google credentials"], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    permission_id: Annotated[str, "ID of the permission to remove"]
) -> Annotated[dict, "Success message"]:
    """
    Removes access permission for a user from a presentation.
    """
    drive_service = get_drive_service(credentials)
    
    drive_service.permissions().delete(
        fileId=presentation_id,
        permissionId=permission_id
    ).execute()
    
    return {
        "message": f"Permission {permission_id} removed successfully"
    }

@tool
def list_permissions(
    credentials: Annotated[str, "Authorized Google credentials"], 
    presentation_id: Annotated[str, "ID of the presentation"]
) -> Annotated[list, "All permissions for the presentation"]:
    """
    Lists all permissions for a presentation.
    """
    drive_service = get_drive_service(credentials)
    
    response = drive_service.permissions().list(
        fileId=presentation_id,
        fields="permissions(id, emailAddress, role, type)"
    ).execute()
    
    return response.get('permissions', [])

@tool
def make_public(
    credentials: Annotated[Any, InjectedToolArg], 
    presentation_id: Annotated[str, "ID of the presentation"], 
    role: Annotated[str, "Role to grant ('reader', 'commenter', or 'writer')"] = "reader"
) -> Annotated[Dict[str, str], "Response containing permission details"]:
    """
    Makes a presentation publicly accessible with the specified role.
    """
    drive_service = get_drive_service(credentials)
    
    permission = {
        'type': 'anyone',
        'role': role
    }
    
    response = drive_service.permissions().create(
        fileId=presentation_id,
        body=permission
    ).execute()
    
    return {
        "permissionId": response.get('id'),
        "type": "anyone",
        "role": role
    } 