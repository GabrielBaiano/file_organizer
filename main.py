import os
import logging
import time

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

userName = os.path.expanduser("~")
organizerFolder = os.path.join(userName, "Organizer")

os.makedirs(organizerFolder, exist_ok=True)

class OrganizerHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        extension = file_path.suffix.lower()

        if extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            dest_folder = os.path.join(organizerFolder, "Images")
        elif extension in ['.mp4', '.avi', '.mov', '.mkv']:
            dest_folder = os.path.join(organizerFolder, "Videos")
        elif extension in ['.mp3', '.wav', '.flac']:
            dest_folder = os.path.join(organizerFolder, "Audio")
        elif extension in ['.pdf', '.docx', '.txt', '.xlsx']:
            dest_folder = os.path.join(organizerFolder, "Documents")

        os.makedirs(dest_folder, exist_ok=True)

        dest_path = os.path.join(dest_folder, file_path.name)

        try:
            os.rename(event.src_path, dest_path)
            logging.info(f"Moved: {file_path.name} → {dest_folder}")
        except Exception as e:
            logging.error(f"Failed to move {file_path.name}: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    watch_path = os.path.join(userName, "Downloads")

    event_handler = OrganizerHandler()
    observer = Observer()
    observer.schedule(event_handler, path=watch_path, recursive=False)

    try:
        observer.start()
        logging.info(f"Started monitoring: {watch_path}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
