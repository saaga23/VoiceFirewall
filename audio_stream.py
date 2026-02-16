import threading
import time
import os
import collections
import wave

# --- SMART IMPORT (The Fix) ---
try:
    # Try loading Windows Loopback (Development)
    import pyaudiowpatch as pyaudio
except ImportError:
    # Fallback to Standard Linux Audio (Production/Streamlit Cloud)
    print("⚠️ Windows Loopback not found. Using standard Linux audio.")
    import pyaudio

# --- CONFIGURATION ---
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000
BUFFER_DURATION = 10 

class AudioRecorder:
    def __init__(self):
        self.frames = collections.deque(maxlen=int(RATE / CHUNK_SIZE * BUFFER_DURATION))
        self.recording = False
        self.thread = None
        self.p = pyaudio.PyAudio()

    def get_loopback_device(self):
        """
        Tries to find a loopback device (Windows) or default input (Linux).
        """
        try:
            # WINDOWS STRATEGY: Look for "Loopback"
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            if not default_speakers["isLoopbackDevice"]:
                for loopback in self.p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]: return loopback
            return default_speakers
        except:
            # LINUX STRATEGY: Just use default microphone
            return self.p.get_default_input_device_info()

    def _record_loop(self):
        device = self.get_loopback_device()
        if not device: 
            print("❌ No input device found.")
            return

        try:
            stream = self.p.open(format=FORMAT,
                                 channels=1, # Force Mono for compatibility
                                 rate=int(device["defaultSampleRate"]),
                                 input=True,
                                 input_device_index=device["index"],
                                 frames_per_buffer=CHUNK_SIZE)
        except Exception as e:
            # Fallback for Linux if specific device fails
            stream = self.p.open(format=FORMAT,
                                 channels=1,
                                 rate=16000,
                                 input=True,
                                 frames_per_buffer=CHUNK_SIZE)
        
        print("🎤 Background Recording Started...")
        while self.recording:
            try:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                self.frames.append(data)
            except:
                break
        
        stream.stop_stream()
        stream.close()

    def start(self):
        if not self.recording:
            self.recording = True
            self.frames.clear()
            self.thread = threading.Thread(target=self._record_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.recording = False
        print("🛑 Recording Stopped.")

    def save_current_buffer(self, filename="live_buffer.wav"):
        if len(self.frames) < 10: return False
        
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
            wf.setframerate(16000) # Force standard rate
            wf.writeframes(b''.join(self.frames))
            wf.close()
            return True
        except:
            return False
