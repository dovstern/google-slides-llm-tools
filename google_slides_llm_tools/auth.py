"""
Authentication module for Google Slides LLM Tools.
Provides functionality to authenticate with Google services and create service clients.
"""

from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.oauth2 import credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth import default

def authenticate(credentials_path=None, use_oauth=False, scopes=None, use_adc=False, project_id=None):
    """
    Authenticate with Google using either a service account, OAuth, or application default credentials.
    
    Args:
        credentials_path (str, optional): Path to the credentials file. Not required if use_adc is True.
        use_oauth (bool): Whether to use OAuth (True) or service account (False).
        scopes (list): List of scopes to request access to.
        use_adc (bool): Whether to use Application Default Credentials via gcloud CLI.
        project_id (str, optional): Google Cloud project ID to use for ADC.
    Returns:
        credentials: Google credentials object.
    """
    if scopes is None:
        scopes = [
            'https://www.googleapis.com/auth/presentations',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/spreadsheets'
        ]
    
    if use_adc:
        # Use Application Default Credentials (e.g., set via gcloud auth application-default login)
        credentials, project = default(scopes=scopes, quota_project_id=project_id)
        return credentials
    elif use_oauth:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, scopes)
        return flow.run_local_server(port=0)
    else:
        return service_account.Credentials.from_service_account_file(
            credentials_path, scopes=scopes
        )

def get_slides_service(credentials):
    """
    Get a Google Slides service instance.
    
    Args:
        credentials: Google credentials object.
        
    Returns:
        service: Google Slides service instance.
    """
    return build('slides', 'v1', credentials=credentials)

def get_drive_service(credentials):
    """
    Get a Google Drive service instance.
    
    Args:
        credentials: Google credentials object.
        
    Returns:
        service: Google Drive service instance.
    """
    return build('drive', 'v3', credentials=credentials)

def get_sheets_service(credentials):
    """
    Get a Google Sheets service instance.
    
    Args:
        credentials: Google credentials object.
        
    Returns:
        service: Google Sheets service instance.
    """
    return build('sheets', 'v4', credentials=credentials) 