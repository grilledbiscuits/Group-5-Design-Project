import os
import platform
import time

def creation_date(file_path):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(file_path)
    else:
        stat = os.stat(file_path)
        try:
            return stat.st_birthtime
        except AttributeError:
            # Some systems (like Linux) don't have st_birthtime, so we use st_mtime instead
            return stat.st_mtime

def main():
    folder_path = "images"
    if os.path.exists(folder_path) and os.path.isdir(folder_path):
        files_info = []  # List to store (filename, creation_date) tuples
        files = os.listdir(folder_path)
        for file in files:
            file_path = os.path.join(folder_path, file)
            if os.path.isfile(file_path):
                created_timestamp = creation_date(file_path)
                files_info.append((file, created_timestamp))
        
        # Sort files_info based on creation dates
        files_info.sort(key=lambda x: x[1])
        
        # Print sorted creation dates
        for file_info in files_info:
            file_name, created_timestamp = file_info
            created_date = time.strftime('%m-%d %H:%M:%S', time.localtime(created_timestamp))
            print(f"The file {file_name} was created on: {created_date}")
    else:
        print("Folder 'images' not found or is not a directory.")

if __name__ == "__main__":
    main()
