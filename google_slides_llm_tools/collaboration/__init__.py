from ..auth import get_drive_service
from langchain.tools import tool

@tool
def add_editor_permission(credentials, presentation_id, user_email):
    """
    Grants edit access to a user for a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        user_email (str): Email address of the user to grant access
        
    Returns:
        dict: The permission resource
    """
    drive_service = get_drive_service(credentials)
    
    permission = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': user_email
    }
    
    result = drive_service.permissions().create(
        fileId=presentation_id, 
        body=permission,
        sendNotificationEmail=True
    ).execute()
    
    return result

@tool
def add_viewer_permission(credentials, presentation_id, user_email):
    """
    Grants view access to a user for a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        user_email (str): Email address of the user to grant access
        
    Returns:
        dict: The permission resource
    """
    drive_service = get_drive_service(credentials)
    
    permission = {
        'type': 'user',
        'role': 'reader',
        'emailAddress': user_email
    }
    
    result = drive_service.permissions().create(
        fileId=presentation_id, 
        body=permission,
        sendNotificationEmail=True
    ).execute()
    
    return result

@tool
def add_commenter_permission(credentials, presentation_id, user_email):
    """
    Grants comment access to a user for a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        user_email (str): Email address of the user to grant access
        
    Returns:
        dict: The permission resource
    """
    drive_service = get_drive_service(credentials)
    
    permission = {
        'type': 'user',
        'role': 'commenter',
        'emailAddress': user_email
    }
    
    result = drive_service.permissions().create(
        fileId=presentation_id, 
        body=permission,
        sendNotificationEmail=True
    ).execute()
    
    return result

@tool
def remove_permission(credentials, presentation_id, permission_id):
    """
    Removes a permission from a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        permission_id (str): ID of the permission to remove
        
    Returns:
        dict: Empty dict if successful
    """
    drive_service = get_drive_service(credentials)
    
    result = drive_service.permissions().delete(
        fileId=presentation_id,
        permissionId=permission_id
    ).execute()
    
    return result

@tool
def list_permissions(credentials, presentation_id):
    """
    Lists all permissions for a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        
    Returns:
        list: List of permission resources
    """
    drive_service = get_drive_service(credentials)
    
    permissions = drive_service.permissions().list(
        fileId=presentation_id
    ).execute()
    
    return permissions['permissions']

@tool
def make_public(credentials, presentation_id):
    """
    Makes a presentation public (anyone with the link can view).
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        
    Returns:
        dict: The permission resource
    """
    drive_service = get_drive_service(credentials)
    
    permission = {
        'type': 'anyone',
        'role': 'reader',
        'allowFileDiscovery': False
    }
    
    result = drive_service.permissions().create(
        fileId=presentation_id, 
        body=permission
    ).execute()
    
    return result
