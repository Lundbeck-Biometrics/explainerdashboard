# needs watchdog and explainer dashboard
import time
import os
import sys
import logging
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler
from explainerdashboard import ExplainerDashboard
import threading
from pathlib import Path

def get_logger(logger_name: str = "script_logger") -> logging.Logger:
    """Returns the configured logger for the pipeline script"""
    file_handler = logging.FileHandler(filename="pipeline.log")
    
    stdout_handler = logging.StreamHandler(stream=sys.stdout)
    handlers = [file_handler, stdout_handler]

    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=handlers,
    )

    logger = logging.getLogger(logger_name)
    return logger

logger = get_logger()

logger.info('starting dashboard listener')

DIRECTORY_TO_WATCH = "/home/sagemaker-user/dashboard-definitions"
logger.info('hello')

if not Path(DIRECTORY_TO_WATCH).exists():
    logger.info('making directory:', DIRECTORY_TO_WATCH)
    Path(DIRECTORY_TO_WATCH).mkdir()

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
                time.sleep(5)
        except:
            self.observer.stop()
            logger.info("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        logger.info(
            f"[{time.asctime()}] noticed {event.event_type} on: [{event.src_path}]"
        )
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            time.sleep(5)
            logger.info("Error")
            # Take any action here when a file is first created.
            logger.info("Received created event - %s." % event.src_path)

            file = extract_file(event.src_path)

            if is_yml(file):
                logger.info("Starting explainer dashboard")
                threading.Thread(target=lambda: ExplainerDashboard.from_config(file).run()).start()

            # TODO Treat edge case race condition when model file is read before yaml file

        elif event.event_type == 'modified':
            # TODO reload explainerdashboard at port in config
            logger.info("Received modified event - %s." % event.src_path)

        elif event.event_type == 'deleted':
            # TODO stop explainerdashboard at port in config; might need to map yaml config to port
            logger.info("Received deleted event - %s." % event.src_path)

#function to check if a file extension is .yml
def is_yml(file):
    return file.endswith(".yml") or file.endswith(".yaml")

#function to extract file from a file path
def extract_file(file):
    return file.split("/")[-1]       

if __name__ == '__main__':
    os.chdir(DIRECTORY_TO_WATCH)
    logger.info('starting watcher')
    w = Watcher()
    w.run()
