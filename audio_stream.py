import pyaudiowpatch as pyaudio
import wave
import threading
import time
import os
import collections

# --- CONFIGURATION ---
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
RATE = 16000
BUFFER_DURATION = 10  # Keep the last 10 seconds in memory (The "Context Window")


class AudioRecorder:
    def __init__(self):
        self.frames = collections.deque(maxlen=int(RATE / CHUNK_SIZE * BUFFER_DURATION))
        self.recording = False
        self.thread = None
        self.p = pyaudio.PyAudio()

    def get_loopback_device(self):
        try:
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            if not default_speakers["isLoopbackDevice"]:
                for loopback in self.p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]: return loopback
            return default_speakers
        except:
            return None

    def _record_loop(self):
        device = self.get_loopback_device()
        if not device: return

        stream = self.p.open(format=FORMAT,
                             channels=device["maxInputChannels"],
                             rate=int(device["defaultSampleRate"]),
                             input=True,
                             input_device_index=device["index"],
                             frames_per_buffer=CHUNK_SIZE)

        print("🎤 Background Recording Started...")
        while self.recording:
            try:
                data = stream.read(CHUNK_SIZE)
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
        """Saves the recent history (Last 10s) to a file for AI Analysis"""
        if len(self.frames) < 10: return False

        device = self.get_loopback_device()
        if not device: return False

        wf = wave.open(filename, 'wb')
        wf.setnchannels(device["maxInputChannels"])
        wf.setsampwidth(self.p.get_sample_size(FORMAT))
        wf.setframerate(int(device["defaultSampleRate"]))
        wf.writeframes(b''.join(self.frames))
        wf.close()
        return True