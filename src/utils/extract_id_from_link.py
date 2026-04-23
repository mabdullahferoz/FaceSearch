import re

def extract_folder_id(link_or_id):
    """
    Extracts the Google Drive folder ID from a full URL or returns 
     the string if it's already an ID.
    """
    # Pattern for drive.google.com/drive/folders/ID or drive.google.com/open?id=ID
    pattern = r'(?:folders\/|id=)([a-zA-Z0-9-_]{25,})'
    match = re.search(pattern, link_or_id)
    return match.group(1) if match else link_or_id