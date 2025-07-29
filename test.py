from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os

SCOPES = ['https://www.googleapis.com/auth/drive']

def upload_and_share(file_path, share_email):
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('drive', 'v3', credentials=creds)

    # Upload the file
    file_metadata = {'name': os.path.basename(file_path)}
    media = MediaFileUpload(file_path, resumable=True)
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    file_id = file.get('id')

    print(f"Uploaded file ID: {file_id}")

    # Share the file with the given email
    permission = {
        'type': 'user',
        'role': 'reader',  # Use 'writer' if you want to allow editing
        'emailAddress': share_email
    }

    service.permissions().create(
        fileId=file_id,
        body=permission,
        sendNotificationEmail=True,  # Optional: notify the user by email
        fields='id'
    ).execute()

    print(f"Shared file with {share_email}")



