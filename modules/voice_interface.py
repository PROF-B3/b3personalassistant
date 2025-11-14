"""
Voice Interface for B3PersonalAssistant

Provides speech-to-text (voice input) and text-to-speech (voice output) capabilities.
"""

import logging
import os
from pathlib import Path
from typing import Optional, List
import tempfile

logger = logging.getLogger(__name__)


class VoiceInterface:
    """
    Voice input and output interface.

    Features:
    - Speech-to-text (multiple engines)
    - Text-to-speech (multiple engines)
    - Voice activity detection
    - Real-time streaming
    - Multiple language support
    - Voice commands recognition

    Example:
        >>> voice = VoiceInterface()
        >>>
        >>> # Record and transcribe
        >>> text = voice.listen(duration=5)
        >>> print(f"You said: {text}")
        >>>
        >>> # Speak response
        >>> voice.speak("Hello, how can I help you?")
        >>>
        >>> # Process audio file
        >>> text = voice.transcribe_file("recording.mp3")
    """

    def __init__(
        self,
        stt_engine: str = "whisper",
        tts_engine: str = "pyttsx3",
        language: str = "en"
    ):
        """
        Initialize voice interface.

        Args:
            stt_engine: Speech-to-text engine ("whisper", "google", "sphinx")
            tts_engine: Text-to-speech engine ("pyttsx3", "gtts", "piper")
            language: Language code (e.g., "en", "es", "fr")
        """
        self.stt_engine = stt_engine
        self.tts_engine = tts_engine
        self.language = language
        self._check_dependencies()
        self._initialize_engines()

    def _check_dependencies(self):
        """Check available voice processing libraries."""
        self.available_engines = {
            "whisper": False,
            "pyttsx3": False,
            "gtts": False,
            "speechrecognition": False,
            "pyaudio": False
        }

        # Check Whisper (STT)
        try:
            import whisper
            self.available_engines["whisper"] = True
            logger.info("Whisper available for speech-to-text")
        except ImportError:
            logger.warning("Whisper not available. Install: pip install openai-whisper")

        # Check pyttsx3 (TTS)
        try:
            import pyttsx3
            self.available_engines["pyttsx3"] = True
            logger.info("pyttsx3 available for text-to-speech")
        except ImportError:
            logger.warning("pyttsx3 not available. Install: pip install pyttsx3")

        # Check gTTS (alternative TTS)
        try:
            import gtts
            self.available_engines["gtts"] = True
            logger.info("gTTS available for text-to-speech")
        except ImportError:
            logger.warning("gTTS not available. Install: pip install gtts")

        # Check SpeechRecognition
        try:
            import speech_recognition
            self.available_engines["speechrecognition"] = True
            logger.info("SpeechRecognition available")
        except ImportError:
            logger.warning("SpeechRecognition not available. Install: pip install SpeechRecognition")

        # Check PyAudio (for microphone)
        try:
            import pyaudio
            self.available_engines["pyaudio"] = True
            logger.info("PyAudio available for microphone input")
        except ImportError:
            logger.warning("PyAudio not available. Install: pip install pyaudio")

    def _initialize_engines(self):
        """Initialize selected engines."""
        self.stt_initialized = False
        self.tts_initialized = False

        # Initialize TTS
        if self.tts_engine == "pyttsx3" and self.available_engines["pyttsx3"]:
            try:
                import pyttsx3
                self.tts = pyttsx3.init()
                # Configure voice
                self.tts.setProperty('rate', 150)  # Speed
                self.tts.setProperty('volume', 0.9)  # Volume
                self.tts_initialized = True
                logger.info("pyttsx3 TTS initialized")
            except Exception as e:
                logger.error(f"Failed to initialize pyttsx3: {e}")

        # Initialize STT (Whisper)
        if self.stt_engine == "whisper" and self.available_engines["whisper"]:
            try:
                import whisper
                # Load model (base is good balance of speed/accuracy)
                self.whisper_model = whisper.load_model("base")
                self.stt_initialized = True
                logger.info("Whisper STT initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Whisper: {e}")

    def listen(self, duration: int = 5, timeout: int = 10) -> Optional[str]:
        """
        Listen to microphone and transcribe speech.

        Args:
            duration: Maximum recording duration in seconds
            timeout: Timeout waiting for speech in seconds

        Returns:
            Transcribed text or None

        Example:
            >>> text = voice.listen(duration=5)
            >>> if text:
            ...     print(f"You said: {text}")
        """
        if not self.available_engines["speechrecognition"] or not self.available_engines["pyaudio"]:
            logger.error("SpeechRecognition or PyAudio not available")
            return None

        try:
            import speech_recognition as sr

            recognizer = sr.Recognizer()

            with sr.Microphone() as source:
                logger.info("Listening...")
                # Adjust for ambient noise
                recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Listen
                audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=duration)

                logger.info("Processing audio...")

                # Transcribe using selected engine
                if self.stt_engine == "whisper" and self.stt_initialized:
                    # Save audio to temp file
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        f.write(audio.get_wav_data())
                        temp_path = f.name

                    # Transcribe
                    text = self.transcribe_file(temp_path)

                    # Clean up
                    Path(temp_path).unlink()

                    return text

                else:
                    # Fallback to Google Speech Recognition (online)
                    text = recognizer.recognize_google(audio, language=self.language)
                    return text

        except sr.WaitTimeoutError:
            logger.warning("No speech detected")
            return None
        except sr.UnknownValueError:
            logger.warning("Could not understand audio")
            return None
        except Exception as e:
            logger.error(f"Error during listening: {e}")
            return None

    def transcribe_file(self, audio_path: str) -> Optional[str]:
        """
        Transcribe audio file to text.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text

        Example:
            >>> text = voice.transcribe_file("meeting_recording.mp3")
            >>> print(text)
        """
        if not self.stt_initialized:
            logger.error("STT engine not initialized")
            return None

        try:
            if self.stt_engine == "whisper":
                result = self.whisper_model.transcribe(str(audio_path), language=self.language)
                return result["text"]

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

    def speak(self, text: str, save_to_file: Optional[str] = None) -> bool:
        """
        Convert text to speech and play it.

        Args:
            text: Text to speak
            save_to_file: Optional path to save audio file

        Returns:
            True if successful

        Example:
            >>> voice.speak("Hello, how can I help you today?")
            >>> voice.speak("Saving to file", save_to_file="output.mp3")
        """
        if not self.tts_initialized:
            logger.error("TTS engine not initialized")
            return False

        try:
            if self.tts_engine == "pyttsx3":
                if save_to_file:
                    self.tts.save_to_file(text, save_to_file)
                    self.tts.runAndWait()
                else:
                    self.tts.say(text)
                    self.tts.runAndWait()
                return True

            elif self.tts_engine == "gtts" and self.available_engines["gtts"]:
                from gtts import gTTS
                import pygame

                tts = gTTS(text=text, lang=self.language)

                if save_to_file:
                    tts.save(save_to_file)
                else:
                    # Save to temp file and play
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
                        temp_path = f.name

                    tts.save(temp_path)

                    # Play audio
                    pygame.mixer.init()
                    pygame.mixer.music.load(temp_path)
                    pygame.mixer.music.play()

                    # Wait for playback to finish
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)

                    # Clean up
                    Path(temp_path).unlink()

                return True

        except Exception as e:
            logger.error(f"Speech synthesis failed: {e}")
            return False

    def detect_voice_activity(self, audio_path: str, threshold: float = 0.01) -> List[tuple]:
        """
        Detect voice activity in audio file.

        Args:
            audio_path: Path to audio file
            threshold: Energy threshold for voice detection

        Returns:
            List of (start_time, end_time) tuples in seconds

        Example:
            >>> segments = voice.detect_voice_activity("recording.wav")
            >>> for start, end in segments:
            ...     print(f"Speech detected: {start:.2f}s - {end:.2f}s")
        """
        try:
            import librosa
            import numpy as np

            # Load audio
            y, sr = librosa.load(audio_path)

            # Calculate energy
            frame_length = int(0.025 * sr)  # 25ms frames
            hop_length = int(0.010 * sr)    # 10ms hop

            # Root mean square energy
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]

            # Find frames above threshold
            voice_frames = rms > threshold

            # Convert to time segments
            segments = []
            in_speech = False
            start_time = 0

            for i, is_voice in enumerate(voice_frames):
                time = i * hop_length / sr

                if is_voice and not in_speech:
                    # Start of speech
                    start_time = time
                    in_speech = True
                elif not is_voice and in_speech:
                    # End of speech
                    segments.append((start_time, time))
                    in_speech = False

            # Handle case where audio ends during speech
            if in_speech:
                segments.append((start_time, len(y) / sr))

            return segments

        except ImportError:
            logger.error("librosa not available. Install: pip install librosa")
            return []
        except Exception as e:
            logger.error(f"Voice activity detection failed: {e}")
            return []

    def recognize_command(self, text: str, commands: List[str]) -> Optional[str]:
        """
        Recognize voice command from text.

        Args:
            text: Transcribed text
            commands: List of valid commands

        Returns:
            Matched command or None

        Example:
            >>> commands = ["open email", "check calendar", "create task"]
            >>> command = voice.recognize_command("please open email", commands)
            >>> if command:
            ...     print(f"Executing: {command}")
        """
        text_lower = text.lower()

        # Exact match
        for command in commands:
            if command.lower() in text_lower:
                return command

        # Fuzzy match (simple)
        from difflib import SequenceMatcher

        best_match = None
        best_ratio = 0.6  # Minimum similarity threshold

        for command in commands:
            ratio = SequenceMatcher(None, command.lower(), text_lower).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = command

        return best_match

    def continuous_listen(self, callback, commands: Optional[List[str]] = None):
        """
        Continuously listen and process voice commands.

        Args:
            callback: Function to call with transcribed text
            commands: Optional list of valid commands

        Example:
            >>> def process_command(text):
            ...     print(f"Processing: {text}")
            ...
            >>> voice.continuous_listen(process_command)
        """
        logger.info("Starting continuous listening... (Ctrl+C to stop)")

        try:
            while True:
                # Listen for speech
                text = self.listen(duration=5, timeout=10)

                if text:
                    logger.info(f"Heard: {text}")

                    # Recognize command if list provided
                    if commands:
                        command = self.recognize_command(text, commands)
                        if command:
                            callback(command, text)
                        else:
                            logger.warning(f"Unknown command: {text}")
                    else:
                        callback(text)

        except KeyboardInterrupt:
            logger.info("Stopped listening")


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Initialize voice interface
    voice = VoiceInterface(stt_engine="whisper", tts_engine="pyttsx3")

    # Test text-to-speech
    print("Testing text-to-speech...")
    voice.speak("Hello! I am your B3 Personal Assistant. How can I help you today?")

    # Test speech-to-text
    print("\nTesting speech-to-text...")
    print("Say something (you have 5 seconds)...")

    text = voice.listen(duration=5)
    if text:
        print(f"You said: {text}")
        voice.speak(f"You said: {text}")
    else:
        print("No speech detected")

    # Test command recognition
    print("\nTesting command recognition...")
    commands = [
        "open email",
        "check calendar",
        "create task",
        "search notes",
        "what's the weather"
    ]

    print(f"Available commands: {', '.join(commands)}")
    print("Say a command...")

    text = voice.listen(duration=5)
    if text:
        command = voice.recognize_command(text, commands)
        if command:
            print(f"✅ Recognized command: {command}")
            voice.speak(f"Executing {command}")
        else:
            print(f"❌ Unknown command: {text}")
    else:
        print("No speech detected")
