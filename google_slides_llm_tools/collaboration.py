from google_slides_llm_tools.auth import get_drive_service
from langchain.tools import tool

@tool
def add_editor_permission(credentials, presentation_id, email):
    """
    Gives editor permission to a user for a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        email (str): Email address of the user to grant access
        
    Returns:
        dict: Response from the API
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
def add_viewer_permission(credentials, presentation_id, email):
    """
    Gives viewer permission to a user for a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        email (str): Email address of the user to grant access
        
    Returns:
        dict: Response from the API
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
def add_commenter_permission(credentials, presentation_id, email):
    """
    Gives commenter permission to a user for a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        email (str): Email address of the user to grant access
        
    Returns:
        dict: Response from the API
    """
    drive_service = get_drive_service(credentials)
    
    user_permission = {
        'type': 'user',
        'role': 'commenter',
        'emailAddress': email
    }
    
    response = drive_service.permissions().create(
        fileId=presentation_id,
        body=user_permission,
        sendNotificationEmail=True
    ).execute()
    
    return {
        "permissionId": response['id'],
        "message": f"Commenter permission granted to {email}"
    }

@tool
def remove_permission(credentials, presentation_id, permission_id):
    """
    Removes access permission for a user from a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        permission_id (str): ID of the permission to remove
        
    Returns:
        dict: Success message
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
def list_permissions(credentials, presentation_id):
    """
    Lists all permissions for a presentation.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        
    Returns:
        list: All permissions for the presentation
    """
    drive_service = get_drive_service(credentials)
    
    response = drive_service.permissions().list(
        fileId=presentation_id,
        fields="permissions(id, emailAddress, role, type)"
    ).execute()
    
    return response.get('permissions', [])

@tool
def make_public(credentials, presentation_id, role='reader'):
    """
    Makes a presentation publicly accessible.
    
    Args:
        credentials: Authorized Google credentials
        presentation_id (str): ID of the presentation
        role (str, optional): Role to assign. Options: 'reader', 'commenter', 'writer'
        
    Returns:
        dict: Response from the API with the public link
    """
    drive_service = get_drive_service(credentials)
    
    # Create public permission
    permission = {
        'type': 'anyone',
        'role': role
    }
    
    result = drive_service.permissions().create(
        fileId=presentation_id,
        body=permission
    ).execute()
    
    # Get the file to obtain the webViewLink
    file = drive_service.files().get(
        fileId=presentation_id,
        fields='webViewLink'
    ).execute()
    
    return {
        "permissionId": result['id'],
        "role": role,
        "link": file['webViewLink'],
        "message": f"Presentation is now public with {role} access"
    } 