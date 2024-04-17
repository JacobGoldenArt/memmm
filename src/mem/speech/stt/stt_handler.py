import logging
import os
from queue import Queue

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

logger = logging.getLogger(__name__)


class SpeechToTextHandler:
    def __init__(self, directory, queue: Queue):
        """
        Initializes the handler for managing speech-to-text files. Sets up a directory watcher to handle incoming files.
        Args:
            directory: The directory to watch for new .txt files containing transcribed speech.
            queue: The queue where transcriptions will be put for processing by the chat system.
        """
        self.directory = directory
        self.queue = queue
        self._setup_directory()
        self.observer = Observer()
        self.event_handler = self._create_event_handler()

    def _setup_directory(self):
        """
        Cleans up the specified directory upon initialization. This ensures that any leftover files
        do not interfere with the operation of the application.
        """
        for filename in os.listdir(self.directory):
            file_path = os.path.join(self.directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
                logger.debug(f"Deleted old file: {filename}")

    def _create_event_handler(self):
        """
        Creates a file system event handler that triggers on file modifications.
        Specifically looks for modifications to .txt files as indicators that new
        transcription data is available.
        """

        class Handler(FileSystemEventHandler):
            def on_modified(self, event):
                if event.src_path.endswith(".txt"):
                    self._process_file(event.src_path)

        return Handler()

    def _process_file(self, file_path):
        """
        Processes the specified .txt file, extracts its content, and enqueues it for chat processing.
        The file is removed immediately after processing to keep the directory clean.
        Args:
            file_path: The path to the .txt file to be processed.
        """
        with open(file_path, "r") as file:
            contents = file.read().strip()
            self.queue.put(contents)
            logger.info(f"Processed and queued speech-to-text content from {file_path}")
        os.remove(file_path)
        logger.debug(f"Deleted processed file: {file_path}")

    def start(self):
        """
        Starts the directory observer, beginning continuous monitoring for changes to .txt files.
        This method should be called after all setup is complete and the system is ready to start processing.
        """
        self.observer.schedule(self.event_handler, self.directory, recursive=False)
        self.observer.start()
        logger.info(
            "Speech-to-text handler started, watching directory: " + self.directory
        )

    def stop(self):
        """
        Stops the directory observer and waits for it to finish, effectively halting the monitoring process.
        This should be called when the application is closing or no longer needs to process incoming transcriptions.
        """
        self.observer.stop()
        self.observer.join()
        logger.info("Speech-to-text handler stopped.")
