import threading
import time
import os
import collections
import wave

# --- CONFIGURATION ---
CHUNK_SIZE = 1024
RATE = 16000
BUFFER_DURATION = 10

class AudioRecorder:
    def __init__(self):
        self.frames = collections.deque(maxlen=int(RATE / CHUNK_SIZE * BUFFER_DURATION))
        self.recording = False
        self.thread = None
        self.p = None
        self.cloud_mode = False # Flag to track if we are broken

        # --- AGGRESSIVE INITIALIZATION ---
        try:
            # 1. Try Windows Loopback
            import pyaudiowpatch as pyaudio
            self.p = pyaudio.PyAudio()
            self.format = pyaudio.paInt16
        except ImportError:
            try:
                # 2. Try Linux Standard (Local)
                import pyaudio
                self.p = pyaudio.PyAudio()
                self.format = pyaudio.paInt16
            except Exception as e:
                # 3. CLOUD FAILURE (Expected)
                print(f"⚠️ Audio Driver Failed (Running on Cloud?): {e}")
                self.cloud_mode = True # Enable Dummy Mode

    def get_loopback_device(self):
        if self.cloud_mode: return None
        try:
            # Windows strategy
            wasapi_info = self.p.get_host_api_info_by_type(self.p.get_host_api_info_by_type(pyaudio.paWASAPI)["type"])
            default_speakers = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            if not default_speakers["isLoopbackDevice"]:
                for loopback in self.p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]: return loopback
            return default_speakers
        except:
            # Linux strategy
            try:
                return self.p.get_default_input_device_info()
            except:
                return None

    def _record_loop(self):
        if self.cloud_mode: return # Do nothing on cloud

        device = self.get_loopback_device()
        if not device: return

        try:
            stream = self.p.open(format=self.format,
                                 channels=1,
                                 rate=int(device["defaultSampleRate"]),
                                 input=True,
                                 input_device_index=device["index"],
                                 frames_per_buffer=CHUNK_SIZE)
        except:
            # Fallback
            stream = self.p.open(format=self.format,
                                 channels=1,
                                 rate=16000,
                                 input=True,
                                 frames_per_buffer=CHUNK_SIZE)
        
        while self.recording:
            try:
                data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
                self.frames.append(data)
            except:
                break
        
        stream.stop_stream()
        stream.close()

    def start(self):
        if self.cloud_mode:
            print("☁️ Cloud Mode: Live Recording Disabled.")
            return

        if not self.recording:
            self.recording = True
            self.frames.clear()
            self.thread = threading.Thread(target=self._record_loop, daemon=True)
            self.thread.start()

    def stop(self):
        self.recording = False

    def save_current_buffer(self, filename="live_buffer.wav"):
        # On Cloud, we just create a silent file to prevent crashes
        if self.cloud_mode:
            # Create a 1-second silent WAV so the AI doesn't crash
            try:
                with wave.open(filename, 'wb') as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2) # 16-bit
                    wf.setframerate(16000)
                    # Write 1 second of silence
                    wf.writeframes(b'\x00' * 32000) 
                return True
            except:
                return False

        if len(self.frames) < 10: return False
        
        try:
            wf = wave.open(filename, 'wb')
            wf.setnchannels(1)
            wf.setsampwidth(self.p.get_sample_size(self.format))
            wf.setframerate(16000)
            wf.writeframes(b''.join(self.frames))
            wf.close()
            return True
        except:
            return False
