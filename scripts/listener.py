'''
Watchdog listener demo adapted for explainer dashboard.

## How it works

The script is supposed to be in an S3 bucket which our SageMaker has access to.
The script is fetched by a SageMaker lifecycle script and started as an asynchronous process with `nohup`. The lifecycle script is not included in this PR.

### Listening Directory

Once started, the script listens to changes in:
`DIRECTORY_TO_WATCH = "/home/sagemaker-user/dashboard-definitions"`

### Explainer Dashboard

If the following event conditions are observed, the script will start an explainer dashboard in a separate thread:
* file added
* file is a yaml file
* file has a corresponding joblib file

The thread runs until it crashes or is shut down (i.e. explainer dashboard interface)

### Log file

The script outputs logs in:
`logfile = "/tmp/dashboard-explainer-watchdog-listener-python-logging.log"`

The nohup process may also pipe output to a logfile.

### Trello Task

**[implement-explainer-dashboard-watchdog](https://trello.com/c/wls37ubu/79-implement-explainer-dashboard-watchdog)**
'''

import time
import os
import sys
import logging
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
from explainerdashboard import ExplainerDashboard
import threading
from pathlib import Path

# constants
DIRECTORY_TO_WATCH = "/home/sagemaker-user/dashboard-definitions"
logfile = "/tmp/dashboard-explainer-watchdog-listener-python-logging.log"

def get_logger(logger_name: str = "script_logger") -> logging.Logger:
    """Returns the configured logger for the pipeline script"""
    file_handler = logging.FileHandler(filename=logfile)
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=handlers,
    )

    logger = logging.getLogger(logger_name)
    return logger


class Watcher:

    def __init__(self):
        # self.observer = Observer()
        self.observer = PollingObserver()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(1)
        except:
            self.observer.stop()
            logger.info("Exiting - stopping threads")
            for thread in threading.enumerate(): 
                logger.info(f'{thread.name = }')
                thread.join()

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        logger.info(f"{event.event_type} on: [{event.src_path}]")

        # ignore directory events
        if event.is_directory:
            return
        
        # ignore events that are not new files
        if event.event_type != 'created':
            return
        
        # ignore non yaml changes
        if not is_yml(event.src_path):
            return

        # it may take a second for the joblib (below) to be added
        time.sleep(1)

        # ignore yaml additions without joblib
        if not has_corresponding_joblib(event.src_path):
            return

        # start dashboard
        file = extract_file(event.src_path)
        logger.info(f"Starting explainer dashboard thread for {file}")
        threading.Thread(
            target=lambda: ExplainerDashboard.from_config(file).run(),
            name=file
        ).start()

def is_yml(file):
    '''check if a file extension is .yml'''
    return file.lower().endswith(".yaml")

def extract_file(file):
    '''extract file from a file path'''
    return file.split("/")[-1]

def has_corresponding_joblib(file_path):
    '''check if a file with the same name but with the extension .joblib exists'''
    return Path(file_path.replace('.yaml', '.joblib')).exists()


if __name__ == '__main__':
    logger = get_logger()

    if not Path(DIRECTORY_TO_WATCH).exists():
        logger.info('making directory:', DIRECTORY_TO_WATCH)
        Path(DIRECTORY_TO_WATCH).mkdir()

    logger.info(f'changing into: {DIRECTORY_TO_WATCH}')
    os.chdir(DIRECTORY_TO_WATCH)

    # start watcher
    logger.info('starting watcher')
    w = Watcher()
    w.run()
