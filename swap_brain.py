import os
import shutil
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor

# PUBLIC Model (No token needed)
NEW_MODEL_ID = "MelodyMachine/Deepfake-audio-detection"
SAVE_PATH = "./models/deepfake_detector"


def swap_brain():
    print(f"🔄 Swapping Brain to Public Model ({NEW_MODEL_ID})...")

    # 1. Clean up old model
    if os.path.exists(SAVE_PATH):
        try:
            shutil.rmtree(SAVE_PATH)
            print("   - Old model removed.")
        except PermissionError:
            print("   ⚠️  Error: Close any running python scripts (like main.py) first!")
            return

    # 2. Download new model
    try:
        print("   - Downloading new weights (Public)...")

        extractor = AutoFeatureExtractor.from_pretrained(NEW_MODEL_ID)
        extractor.save_pretrained(SAVE_PATH)

        model = AutoModelForAudioClassification.from_pretrained(NEW_MODEL_ID)
        model.save_pretrained(SAVE_PATH)

        print(f"✅ SUCCESS: New Brain Installed at {SAVE_PATH}")
        print("🚀 Ready for the Truth Test.")

    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    swap_brain()