from mem.speech.tts.text_to_speech_handler import TextToSpeechHandler
from mem.utils.rich_setup import Prompt, console, rprint

logger = logging.getLogger(__name__)


class ChatLoop:
    def __init__(self, config_manager, stt_handler=None, tts_handler=None):
        """
        Initializes the ChatLoop which manages the chat process.
        Args:
            config_manager: Manages configuration settings for the chat.
            stt_handler: Optional. Handles speech-to-text functionality if provided.
            tts_handler: Optional. Handles text-to-speech functionality if provided.
        """
        self.config_manager = config_manager
        self.stt_handler = stt_handler
        self.tts_handler = tts_handler
        self.request_manager = RequestManager()
        self.queue = Queue()

    async def run_loop(self, chat_config):
        """
        Runs the main loop for the chat application. Initializes speech handlers based on configuration.
        Args:
            chat_config: A dictionary containing configuration settings such as whether to use STT or TTS.
        """
        if chat_config.get("speech_to_text"):
            if not self.stt_handler:
                self.stt_handler = SpeechToTextHandler(
                    os.path.expanduser("~/_path_to_media"), self.queue
                )
            rprint("Speech-to-text activated.")
            self.stt_handler.start()

        if chat_config.get("text_to_speech") and not self.tts_handler:
            self.tts_handler = TextToSpeechHandler(chat_config["speech_model"])
            self.tts_handler.load_model()

        await self._process_chat(chat_config)

    async def _process_chat(self, chat_config):
        """
        Processes each message received through the chat loop. Checks for exit commands.
        Args:
            chat_config: Configuration used to set up the chat properties.
        """
        exit_words = {"exit", "quit", "bye", "q", "x", "z"}
        while True:
            try:
                user_input = self.queue.get(
                    timeout=1
                )  # Attempt to get user input from the queue.
            except Empty:
                user_input = Prompt.ask("Type your message: ")

            if any(word in user_input.lower() for word in exit_words):
                rprint("Chat session ending...")
                break

            response = await self.request_manager.make_request(chat_config, user_input)
            if self.tts_handler:
                await self.tts_handler.speak(response)

            rprint(f"Assistant: {response}")

    def stop(self):
        """
        Stops any running speech handlers.
        """
        if self.stt_handler:
            self.stt_handler.stop()
        if self.tts_handler:
            self.tts_handler.stop()
