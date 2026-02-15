#!/usr/bin/env python3
"""
Ambient focus sounds module for Focus Timer CLI.
Generates and plays ambient background sounds during focus sessions.
"""

import numpy as np
import threading
import time
from pathlib import Path

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# Sound generation constants
SAMPLE_RATE = 44100
BUFFER_SIZE = 1024


class AmbientSoundPlayer:
    """Player for ambient focus sounds."""
    
    SOUND_TYPES = ["white-noise", "rain", "coffee-shop", "nature", "none"]
    
    def __init__(self):
        self.current_sound = None
        self.volume = 50
        self.playing = False
        self._thread = None
        self._stop_event = threading.Event()
        
    def _init_pygame(self):
        """Initialize pygame mixer if not already initialized."""
        if not PYGAME_AVAILABLE:
            return False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=SAMPLE_RATE, size=-16, channels=2, buffer=BUFFER_SIZE)
            return True
        except Exception as e:
            print(f"Warning: Could not initialize audio: {e}")
            return False
    
    def _generate_white_noise(self, duration_sec=5):
        """Generate white noise samples."""
        samples = np.random.uniform(-1, 1, int(SAMPLE_RATE * duration_sec))
        return self._convert_to_sound(samples)
    
    def _generate_brown_noise(self, duration_sec=5):
        """Generate brown noise (deeper, like rain/coffee shop)."""
        samples = np.random.uniform(-1, 1, int(SAMPLE_RATE * duration_sec))
        # Apply brown noise filter (integrate with decay)
        brown = np.cumsum(samples)
        brown = brown / np.max(np.abs(brown)) * 0.8
        return self._convert_to_sound(brown)
    
    def _generate_pink_noise(self, duration_sec=5):
        """Generate pink noise (balanced, like nature)."""
        samples = np.random.uniform(-1, 1, int(SAMPLE_RATE * duration_sec))
        # Simple pink noise approximation
        fft = np.fft.rfft(samples)
        freqs = np.fft.rfftfreq(len(samples))
        # Avoid division by zero
        freqs[0] = 1
        pink_filter = 1 / np.sqrt(freqs)
        pink_filter[0] = 1
        filtered = fft * pink_filter
        pink = np.fft.irfft(filtered, len(samples))
        pink = pink / np.max(np.abs(pink)) * 0.8
        return self._convert_to_sound(pink)
    
    def _convert_to_sound(self, samples):
        """Convert numpy array to pygame Sound object."""
        # Convert to 16-bit signed integers
        samples = (samples * 32767).astype(np.int16)
        # Make stereo
        stereo = np.column_stack((samples, samples))
        # Convert to bytes
        sound_bytes = stereo.tobytes()
        return pygame.mixer.Sound(buffer=sound_bytes)
    
    def generate_sound(self, sound_type, duration_sec=5):
        """Generate ambient sound of specified type."""
        if not PYGAME_AVAILABLE:
            return None
            
        if sound_type == "white-noise":
            return self._generate_white_noise(duration_sec)
        elif sound_type == "rain":
            return self._generate_brown_noise(duration_sec)
        elif sound_type == "coffee-shop":
            return self._generate_brown_noise(duration_sec)
        elif sound_type == "nature":
            return self._generate_pink_noise(duration_sec)
        else:
            return None
    
    def play(self, sound_type, volume=50):
        """Start playing ambient sound in a loop."""
        if sound_type == "none" or not PYGAME_AVAILABLE:
            return False
            
        if not self._init_pygame():
            return False
            
        self.current_sound = sound_type
        self.volume = max(0, min(100, volume))
        self.playing = True
        self._stop_event.clear()
        
        # Start playback in a separate thread
        self._thread = threading.Thread(target=self._play_loop, daemon=True)
        self._thread.start()
        return True
    
    def _play_loop(self):
        """Internal loop for continuous sound playback."""
        channel = None
        
        while not self._stop_event.is_set() and self.playing:
            try:
                # Generate a chunk of sound
                sound = self.generate_sound(self.current_sound, duration_sec=3)
                if sound is None:
                    break
                    
                # Set volume (0.0 to 1.0)
                sound.set_volume(self.volume / 100.0)
                
                # Play the sound
                channel = sound.play()
                if channel:
                    # Wait for the sound to finish or stop event
                    while channel.get_busy() and not self._stop_event.is_set():
                        time.sleep(0.1)
                else:
                    time.sleep(0.5)
                    
            except Exception as e:
                # Silently handle audio errors to not disrupt focus
                time.sleep(1)
    
    def stop(self):
        """Stop the ambient sound playback."""
        self.playing = False
        self._stop_event.set()
        
        if PYGAME_AVAILABLE and pygame.mixer.get_init():
            try:
                pygame.mixer.stop()
            except:
                pass
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)
    
    def set_volume(self, volume):
        """Update volume (0-100)."""
        self.volume = max(0, min(100, volume))
        # If currently playing, update pygame channel volume
        if PYGAME_AVAILABLE and pygame.mixer.get_init():
            try:
                for i in range(pygame.mixer.get_num_channels()):
                    channel = pygame.mixer.Channel(i)
                    if channel.get_busy():
                        channel.set_volume(self.volume / 100.0)
            except:
                pass
    
    def get_sound_icon(self):
        """Get emoji icon for current sound type."""
        icons = {
            "white-noise": "🌫️",
            "rain": "🌧️",
            "coffee-shop": "☕",
            "nature": "🌿",
            "none": "🔇",
        }
        return icons.get(self.current_sound, "🔇")
    
    def get_sound_name(self):
        """Get display name for current sound type."""
        names = {
            "white-noise": "White Noise",
            "rain": "Rain",
            "coffee-shop": "Coffee Shop",
            "nature": "Nature",
            "none": "None",
        }
        return names.get(self.current_sound, "None")


# Global player instance
_player = None

def get_player():
    """Get or create the global sound player instance."""
    global _player
    if _player is None:
        _player = AmbientSoundPlayer()
    return _player


def play_ambient(sound_type, volume=50):
    """Convenience function to start playing ambient sound."""
    player = get_player()
    return player.play(sound_type, volume)


def stop_ambient():
    """Convenience function to stop ambient sound."""
    player = get_player()
    player.stop()


def is_playing():
    """Check if ambient sound is currently playing."""
    player = get_player()
    return player.playing


def get_sound_icon(sound_type):
    """Get icon for a sound type without playing."""
    player = AmbientSoundPlayer()
    player.current_sound = sound_type
    return player.get_sound_icon()
