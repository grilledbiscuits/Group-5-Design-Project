import os
import platform
from datetime import datetime


def creation_date(file_path):
    """
    Try to get the date that a file was created, falling back to when it was last modified if creation date isn't available.
    This works on Windows, Unix/Linux.
    """
    if platform.system() == 'Windows':
        return datetime.fromtimestamp(os.path.getctime(file_path))
    else:
        stat = os.stat(file_path)
        try:
            return datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            # For Unix/Linux fallback to last modified time if birthtime is not available
            return datetime.fromtimestamp(stat.st_mtime)


def main():
    directory = input("Enter directory path: ")
    if not os.path.isdir(directory):
        print("Invalid directory path.")
        return

    files = os.listdir(directory)
    for file in files:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            print(f"{file}: {creation_date(file_path)}")


if __name__ == "__main__":
    main()
