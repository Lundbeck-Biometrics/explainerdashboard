#needs watchdog and explainer dashboard
import time
import os
from watchdog.observers import Observer
from watchdog.observers.polling import PollingObserver
from watchdog.events import PatternMatchingEventHandler
from watchdog.events import FileSystemEventHandler
from explainerdashboard import ExplainerDashboard
import threading
from pathlib import Path

DIRECTORY_TO_WATCH = "/home/sagemaker-user/dashboard-definitions"
print('hello')

if not Path(DIRECTORY_TO_WATCH).exists():
    print('making directory:', DIRECTORY_TO_WATCH)
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
            print("Error")

        self.observer.join()


class Handler(FileSystemEventHandler):

    @staticmethod
    def on_any_event(event):
        print(
            f"[{time.asctime()}] noticed {event.event_type} on: [{event.src_path}]"
        )
        if event.is_directory:
            return None

        elif event.event_type == 'created':
            time.sleep(5)
            print("Error")
            # Take any action here when a file is first created.
            print("Received created event - %s." % event.src_path)

            file = extract_file(event.src_path)

            if is_yml(file):
                print("Starting explainer dashboard")
                threading.Thread(target=lambda: ExplainerDashboard.from_config(file).run()).start()

            # TODO Treat edge case race condition when model file is read before yaml file

        elif event.event_type == 'modified':
            # TODO reload explainerdashboard at port in config
            print("Received modified event - %s." % event.src_path)

        elif event.event_type == 'deleted':
            # TODO stop explainerdashboard at port in config; might need to map yaml config to port
            print("Received deleted event - %s." % event.src_path)

#function to check if a file extension is .yml
def is_yml(file):
    return file.endswith(".yml") or file.endswith(".yaml")

#function to extract file from a file path
def extract_file(file):
    return file.split("/")[-1]       

if __name__ == '__main__':
    os.chdir(DIRECTORY_TO_WATCH)
    print('starting watcher')
    w = Watcher()
    w.run()
