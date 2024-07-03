import os
import time
import boto3
import logging
import random
import string
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

# Logging configurations to add timestamp
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

# Environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_ENDPOINT = os.getenv('S3_ENDPOINT')
S3_BUCKET = os.getenv('S3_BUCKET')
SSL_VERIFY = os.getenv('SSL_VERIFY', 'True').lower() == 'true'
DIRECTORY_TO_WATCH = os.getenv('DIRECTORY_TO_WATCH', '/path/to/directory')

# S3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    endpoint_url=S3_ENDPOINT,
    verify=SSL_VERIFY
)

def generate_random_string(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

class Watcher:
    def __init__(self, directory_to_watch):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def process(event):
        if event.is_directory:
            return None

        if event.event_type == 'created':
            # The file was created
            file_path = event.src_path
            file_name = os.path.basename(file_path)
            now = datetime.now()
            date_time_prefix = now.strftime('%Y-%m-%d_%H-%M-%S')
            random_suffix = generate_random_string()
            s3_key = f'{date_time_prefix}_{random_suffix}/{file_name}'
            logging.info(f'Detected the creation of {file_path}')

            try:
                # Upload the file to S3
                s3_client.upload_file(file_path, S3_BUCKET, s3_key)
                logging.info(f'Successfully uploaded {file_name} to {S3_BUCKET}/{s3_key}')

                # Create a text file with the original directory path
                original_path_info = f"Original path: {file_path}"
                info_file_name = f'{date_time_prefix}_{random_suffix}_info.txt'
                info_file_path = f'/tmp/{info_file_name}'
                with open(info_file_path, 'w') as info_file:
                    info_file.write(original_path_info)

                # Upload the info file to S3
                info_s3_key = f'{date_time_prefix}_{random_suffix}/{info_file_name}'
                s3_client.upload_file(info_file_path, S3_BUCKET, info_s3_key)
                logging.info(f'Successfully uploaded {info_file_name} to {S3_BUCKET}/{info_s3_key}')
            except Exception as e:
                logging.error(f'Error uploading file: {e}')

    def on_created(self, event):
        self.process(event)

if __name__ == '__main__':
    watcher = Watcher(DIRECTORY_TO_WATCH)
    logging.info(f"Watching path {DIRECTORY_TO_WATCH}")
    logging.info(f"Uploading to s3://{S3_BUCKET}")
    watcher.run()

