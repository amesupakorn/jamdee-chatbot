import re

def convert_drive_link(drive_link):
    match = re.search(r'/d/([a-zA-Z0-9_-]+)', drive_link)
    if match:
        file_id = match.group(1)
        return f"https://lh3.googleusercontent.com/d/{file_id}"
    return drive_link 