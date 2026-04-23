import io
import os
from googleapiclient.http import MediaIoBaseDownload

class DriveHandler:
    def __init__(self, service):
        self.service = service

    def list_all_images_recursive(self, folder_id):
        """Recursively finds all images in a folder and its subfolders."""
        all_images = []
        
        # 1. Setup API parameters for shared/public drives
        params = {
            "q": f"'{folder_id}' in parents and (mimeType contains 'image/')",
            "fields": "files(id, name)",
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True
        }
        
        # 2. Get images in the current folder
        results = self.service.files().list(**params).execute()
        all_images.extend(results.get('files', []))
        
        # 3. Get all subfolders to dive deeper
        folder_params = {
            "q": f"'{folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'",
            "fields": "files(id, name)",
            "supportsAllDrives": True,
            "includeItemsFromAllDrives": True
        }
        folders = self.service.files().list(**folder_params).execute()
        
        for folder in folders.get('files', []):
            print(f"[*] Entering subfolder: {folder['name']}")
            # Recursive call: adds results from subfolders to the main list
            all_images.extend(self.list_all_images_recursive(folder['id']))
            
        return all_images

    def get_file_bytes(self, file_id):
        """Streams file bytes into memory using a buffer."""
        request = self.service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        return fh.getvalue()