def convert_drive_link(original_url):
    if "drive.google.com" in original_url and "/file/d/" in original_url:
        file_id = original_url.split("/file/d/")[1].split("/")[0]
        return f"https://drive.google.com/uc?export=view&id={file_id}"
    return original_url