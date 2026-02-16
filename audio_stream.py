import threading
import time
import os
import collections
import wave
import sys

# --- CONFIGURATION ---
CHUNK_SIZE = 1024
RATE = 16000
BUFFER_DURATION = 10 

# --- DETECTION LOGIC ---
# We check if we are on Streamlit Cloud to avoid crashing the C-library
IS_CLOUD = os.getenv('STREAMLIT_SERVER_HEADLESS') == 'true' or os.path.exists("/mount/src")

class DummyRecorder:
    """
    A fake recorder for the Cloud. 
    It doesn't record anything (prevents crashes), but keeps the app alive.
    """
    def __init__(self):
        self.frames = collections.deque(maxlen=int(RATE / CHUNK_SIZE * BUFFER_DURATION))
        self.recording = False
        print("☁️ CLOUD MODE DETECTED: Audio Hardware Disabled (Dummy Recorder Active)")

    def start(self):
        self.recording = True
        print("☁️ Dummy Recorder Started (No Audio)")

    def stop(self):
        self.recording = False
        print("☁️ Dummy Recorder Stopped")

    def save_current_buffer(self, filename="live_buffer.wav"):
        # Generate 1 second of silence so the AI doesn't break
        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2) # 16-bit
                wf.setframerate(16000)
                # Write 1 second of silent bytes
                wf.writeframes(b'\x00' * 32000) 
            return True
        except:
            return False

class RealRecorder:
    """
    The Real Recorder for Local Windows/Linux Machines.
    """
    def __init__(self):
        self.frames = collections.deque(maxlen=int(RATE / CHUNK_SIZE * BUFFER_DURATION))
        self.recording = False
        self.thread = None
        self.p = None
        
        # Import PyAudio ONLY if we are local
        try:
            import pyaudiowpatch as pyaudio
        except ImportError:
            import pyaudio
            
        self.p = pyaudio.PyAudio()
        self.format = pyaudio.paInt16

    def get_device(self):
        # ... (Existing logic for finding devices) ...
        try:
            wasapi_info = self.p.get_host_api_info_by_type(self.p.get_host_api_info_by_type(self.p.get_host_api_info_by_type(pyaudio.paWASAPI)["type"])["type"])
            # ... simple fallback ...
            return self.p.get_default_input_device_info()
        except:
            return self.p.get_default_input_device_info()

    def _record_loop(self):
        try:
            # Simple default stream for robustness
            stream = self.p.open(format=self.format,
                                 channels=1,
                                 rate=16000,
                                 input=True,
                                 frames_per_buffer=CHUNK_SIZE)
        except Exception as e:
            print(f"Mic Error: {e}")
            return

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

    def save_current_buffer(self, filename="live_buffer.wav"):
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

# --- FACTORY ---
# This decides which class to give the App
if IS_CLOUD:
    AudioRecorder = DummyRecorder
else:
    # Only try to load RealRecorder if we are NOT on cloud
    try:
        # Quick check if PyAudio is even installed/working
        import pyaudio
        p = pyaudio.PyAudio()
        p.terminate()
        AudioRecorder = RealRecorder
    except:
        print("⚠️ Audio Init Failed. Falling back to Dummy.")
        AudioRecorder = DummyRecorder
