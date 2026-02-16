import os
import sys
import time


def check_system():
    print("\n🛡️  VOICE FIREWALL SYSTEM CHECK")
    print("------------------------------")

    # 1. Check Virtual Environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  WARNING: You are NOT in a virtual environment!")
    else:
        print("✅ Environment:  Isolated (venv)")

    # 2. Check Model (Specifically looking for config.json)
    model_path = "./models/deepfake_detector"
    if os.path.exists(os.path.join(model_path, "config.json")):
        print("✅ AI Brain:     Loaded (Offline Ready)")
    else:
        print("❌ AI Brain:     MISSING or CORRUPT (Run download_model.py)")

    # 3. Check Audio Drivers
    try:
        import pyaudiowpatch
        print("✅ Audio Driver: PyAudioWPatch (Windows Loopback)")
    except ImportError:
        try:
            import pyaudio
            print("✅ Audio Driver: PyAudio (Standard)")
        except ImportError:
            print("❌ Audio Driver: MISSING (pip install failed?)")


if __name__ == "__main__":
    check_system()