from openai import OpenAI
import pygame
import io
import threading
from dotenv import load_dotenv
import os
import random
from pathlib import Path


class SoundAgent:
    def __init__(self):
        load_dotenv(override=True)
        self.client = OpenAI()
        self.current_audio = None
        self.is_playing = False

        # Initialize pygame mixer with specific settings
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
        pygame.mixer.set_num_channels(2)  # Set up two channels

        # Create separate Sound objects for voice and music
        self.voice_channel = pygame.mixer.Channel(0)  # Channel for TTS
        self.music_channel = pygame.mixer.Channel(
            1
        )  # Channel for background music

        self.voice_sound = None  # Will hold the TTS audio
        self.background_sound = None  # Will hold the music

        # Initialize music directory structure
        self.music_root = Path("osrs music")
        self.current_intensity = None
        self.current_mood = None

        # Start with adventerous music
        self.play_background_music(intensity=1, mood="adventerous")

    async def generate_speech(self, text: str) -> bool:
        """Generate speech from text using OpenAI's TTS"""
        try:
            response = self.client.audio.speech.create(
                model="tts-1",
                voice="onyx",  # Lets use onyx then..
                input=text,
            )

            # Create a new BytesIO object and write the audio data
            audio_buffer = io.BytesIO()
            audio_buffer.write(response.content)
            audio_buffer.seek(0)

            self.current_audio = audio_buffer
            return True

        except Exception as e:
            print(f"Error generating speech: {e}")
            return False

    def play_audio(self):
        """Play the TTS audio on the voice channel"""
        if self.current_audio and not self.is_playing:
            try:
                self.current_audio.seek(0)
                self.is_playing = True
                thread = threading.Thread(target=self._play_audio_thread)
                thread.daemon = True
                thread.start()
            except Exception as e:
                print(f"Error starting audio playback: {e}")
                self.is_playing = False

    def _play_audio_thread(self):
        """Play TTS audio in a separate thread using the voice channel"""
        try:
            self.current_audio.seek(0)

            # Load the audio into a Sound object
            try:
                sound_obj = pygame.mixer.Sound(self.current_audio)
                self.voice_sound = sound_obj

                # Play on voice channel
                self.voice_channel.play(self.voice_sound)

                # Wait for voice to finish
                while self.voice_channel.get_busy():
                    pygame.time.wait(100)

            except Exception as e:
                print(f"Error playing voice audio: {e}")

        except Exception as e:
            print(f"Error in voice thread: {e}")

        finally:
            self.is_playing = False
            if self.current_audio:
                self.current_audio.seek(0)

    def play_background_music(self, intensity: int = None, mood: str = None):
        """Play random background music matching the scene intensity and mood"""
        try:
            # Update current settings if provided
            if intensity is not None:
                self.current_intensity = intensity
            if mood is not None:
                self.current_mood = mood

            # If this is the first music being played, don't print "keeping" message
            if self.background_sound is None:
                print(
                    f"Starting music (Intensity: {self.current_intensity}, Mood: {self.current_mood})"
                )
            # Only print "keeping" message if music is already playing and settings haven't changed
            elif (
                intensity is not None
                and mood is not None
                and intensity == self.current_intensity
                and mood == self.current_mood
            ):
                print(
                    f"Keeping current music (Intensity: {self.current_intensity}, Mood: {self.current_mood})"
                )

            # Construct path to appropriate music folder
            music_dir = (
                self.music_root
                / f"{self.current_intensity}. {self._get_intensity_name()}"
                / self.current_mood
            )

            music_files = list(music_dir.glob("*.ogg"))
            if not music_files:
                print(f"No music files found in {music_dir}")
                return

            music_file = random.choice(music_files)

            try:
                # Load and play new music with fadeout
                new_sound = pygame.mixer.Sound(str(music_file))
                new_sound.set_volume(0.2)

                if self.background_sound:
                    self.music_channel.fadeout(1000)
                    pygame.time.wait(1000)

                self.background_sound = new_sound
                self.music_channel.play(self.background_sound, loops=-1)
                print(
                    f"Now playing: {music_file.name} "
                    f"(Intensity: {self.current_intensity}, Mood: {self.current_mood})"
                )

            except Exception as e:
                print(f"Error playing background music: {e}")

        except Exception as e:
            print(f"Error setting up background music: {e}")

    def _get_intensity_name(self) -> str:
        """Convert intensity number to folder name"""
        return {1: "calm", 2: "medium", 3: "intense"}[self.current_intensity]

    def stop_background_music(self):
        """Stop the background music channel"""
        self.music_channel.stop()

    def stop_voice(self):
        """Stop the voice channel"""
        self.voice_channel.stop()
        self.is_playing = False

    def set_background_volume(self, volume: float):
        """Set background music volume (0.0 to 1.0)"""
        if self.background_sound:
            self.background_sound.set_volume(max(0.0, min(1.0, volume)))

    def set_voice_volume(self, volume: float):
        """Set voice volume (0.0 to 1.0)"""
        if self.voice_sound:
            self.voice_sound.set_volume(max(0.0, min(1.0, volume)))
