import time
import logging
import shutil

from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Global states
USER_HOME = Path.home()
ORGANIZER_FOLDER = USER_HOME / "Organizer"
DOWNLOADS_FOLDER = USER_HOME / "Downloads"

ORGANIZER_FOLDER.mkdir(exist_ok=True)

class OrganizerHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.name.endswith(('.crdownload', '.part', '.tmp')):
            return

        extension = file_path.suffix.lower()
        
        categories = {
            "Images": ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'],
            "Videos": ['.mp4', '.avi', '.mov', '.mkv', '.webm'],
            "Audio": ['.mp3', '.wav', '.flac', '.ogg'],
            "Documents": ['.pdf', '.docx', '.txt', '.xlsx', '.pptx', '.csv'],
            "Archives": ['.zip', '.rar', '.7z', '.tar', '.gz']
        }

        target_category = "Others"
        
        for category, ext_list in categories.items():
            if extension in ext_list:
                target_category = category
                break

        dest_folder = ORGANIZER_FOLDER / target_category
        dest_folder.mkdir(exist_ok=True)
        dest_path = dest_folder / file_path.name

        logging.info(f"Detectado: {file_path.name}. Aguardando conclusão...")
        
        if self.wait_for_file_completion(file_path):
            self.move_file(file_path, dest_path)

    def wait_for_file_completion(self, file_path):
        historical_size = -1
        unchanged_count = 0
        max_retries = 30 # 30 seconds timeout

        while unchanged_count < 3: # Recount for security
            try:
                if not file_path.exists():
                    return False
                
                current_size = file_path.stat().st_size
                
                if current_size == historical_size and current_size > 0:
                    unchanged_count += 1
                else:
                    unchanged_count = 0 # reestart count
                    
                historical_size = current_size
                time.sleep(1)
                
                max_retries -= 1
                if max_retries <= 0:
                    logging.warning(f"Timeout aguardando arquivo: {file_path.name}")
                    return False

            except Exception as e:
                logging.error(f"Erro verificando arquivo: {e}")
                time.sleep(1)
        
        return True

    def move_file(self, src, dest):
        # Trata caso o arquivo já exista no destino (renomeia para evitar sobrescrita)
        if dest.exists():
            timestamp = int(time.time())
            dest = dest.parent / f"{dest.stem}_{timestamp}{dest.suffix}"

        try:
            shutil.move(str(src), str(dest))
            logging.info(f"Sucesso: {src.name} → {dest.parent.name}")
        except Exception as e:
            logging.error(f"Falha ao mover {src.name}: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(message)s', 
        datefmt='%H:%M:%S'
    )

    event_handler = OrganizerHandler()
    observer = Observer()
    observer.schedule(event_handler, path=DOWNLOADS_FOLDER, recursive=False)

    logging.info(f"Monitorando: {DOWNLOADS_FOLDER}")
    logging.info("Pressione Ctrl+C para parar.")

    try:
        observer.start()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Encerrando monitoramento.")

    observer.join()