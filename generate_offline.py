import os
import pyttsx3
import pyaudiowpatch as pyaudio
import wave
import time

# Create assets folder
if not os.path.exists("assets"):
    os.makedirs("assets")


def generate_fake():
    print("🤖 Generating 'Fake' AI Voice (assets/fake_test.wav)...")
    try:
        engine = pyttsx3.init()
        # Slow it down slightly to sound more "serious"
        engine.setProperty('rate', 150)

        text = "This is a synthetic AI voice generated for security testing. My frequency patterns are perfectly consistent."
        save_path = os.path.abspath("assets/fake_test.wav")

        engine.save_to_file(text, save_path)
        engine.runAndWait()
        print("✅ Fake Audio Created!")
    except Exception as e:
        print(f"❌ Error creating fake audio: {e}")


def record_real():
    print("\n🎤 Now we need a REAL Human Voice.")
    print("   I will record your microphone for 5 seconds.")
    print("   Please say: 'This is a verified human voice for the AspitaTech Firewall.'")

    input("👉 Press ENTER to start recording...")

    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "assets/real_test.wav"

    p = pyaudio.PyAudio()

    # Find a working microphone (Input Device)
    # We loop to find the first real microphone, not loopback
    target_index = None
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0 and "loopback" not in info['name'].lower():
            target_index = i
            break

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=target_index,
                    frames_per_buffer=CHUNK)

    print("🔴 RECORDING... (Speak now!)")

    frames = []
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("✅ Recording Finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()
    print(f"✅ Real Audio Saved: {WAVE_OUTPUT_FILENAME}")


if __name__ == "__main__":
    generate_fake()
    record_real()
    print("\n🚀 Assets Ready! You can now run 'streamlit run streamlit_app.py'")