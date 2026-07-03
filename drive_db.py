import json
import io
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

class DriveDatabase:
    def __init__(self, credentials):
        """Builds the Drive service using user's authenticated OAuth2 credentials."""
        self.service = build('drive', 'v3', credentials=credentials)
        self.folder_id = self._get_or_create_app_folder()

    def _get_or_create_app_folder(self):
        """Creates a hidden specific folder inside the user's Drive for app files."""
        query = "name = 'FairStudyAI_Data' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
        results = self.service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        
        if files:
            return files[0]['id']
        
        # Create folder if it doesn't exist
        file_metadata = {
            'name': 'FairStudyAI_Data',
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = self.service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')

    def save_state(self, session_id: str, state_data: dict):
        """Saves or updates state data inside a JSON file named after the session ID."""
        file_name = f"{session_id}.json"
        query = f"name = '{file_name}' and '{self.folder_id}' in parents and trashed = false"
        results = self.service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])

        json_bytes = json.dumps(state_data).encode('utf-8')
        media = MediaIoBaseUpload(io.BytesIO(json_bytes), mimeType='application/json', resumable=True)

        if files:
            # Update existing file
            file_id = files[0]['id']
            self.service.files().update(fileId=file_id, media_body=media).execute()
        else:
            # Create new file
            file_metadata = {'name': file_name, 'parents': [self.folder_id]}
            self.service.files().create(body=file_metadata, media_body=media).execute()

    def load_state(self, session_id: str) -> dict:
        """Loads state data from the user's Drive session JSON file."""
        file_name = f"{session_id}.json"
        query = f"name = '{file_name}' and '{self.folder_id}' in parents and trashed = false"
        results = self.service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])

        if not files:
            return {}

        file_id = files[0]['id']
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()

        return json.loads(fh.getvalue().decode('utf-8'))
