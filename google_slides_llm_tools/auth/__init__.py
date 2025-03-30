from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle

# Define scopes needed for Google Slides API
SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets.readonly'
]

def authenticate(credentials_path='credentials.json', token_path='token.pickle'):
    """
    Authenticates with Google APIs and returns the credentials.
    
    Args:
        credentials_path (str): Path to the credentials.json file
        token_path (str): Path to save the token.pickle file
        
    Returns:
        Credentials: Google OAuth2 credentials
    """
    creds = None
    
    # Load the token file if it exists
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                raise FileNotFoundError(
                    f"Credentials file not found at {credentials_path}. "
                    "Please download credentials.json from the Google Cloud Console "
                    "and save it to this location."
                )
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for next run
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def get_slides_service(credentials):
    """
    Get an authorized Google Slides API service instance.
    
    Args:
        credentials: Authorized credentials
        
    Returns:
        Resource: Google Slides API service
    """
    return build('slides', 'v1', credentials=credentials)

def get_drive_service(credentials):
    """
    Get an authorized Google Drive API service instance.
    
    Args:
        credentials: Authorized credentials
        
    Returns:
        Resource: Google Drive API service
    """
    return build('drive', 'v3', credentials=credentials)

def get_sheets_service(credentials):
    """
    Get an authorized Google Sheets API service instance.
    
    Args:
        credentials: Authorized credentials
        
    Returns:
        Resource: Google Sheets API service
    """
    return build('sheets', 'v4', credentials=credentials)
