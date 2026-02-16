import os
import shutil
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor

# Back to the one that worked!
OLD_MODEL_ID = "Hemgg/Deepfake-audio-detection"
SAVE_PATH = "./models/deepfake_detector"


def revert_brain():
    print(f"↺ Reverting Brain to Stable Model ({OLD_MODEL_ID})...")

    if os.path.exists(SAVE_PATH):
        shutil.rmtree(SAVE_PATH)  # Delete the paranoid model

    try:
        extractor = AutoFeatureExtractor.from_pretrained(OLD_MODEL_ID)
        extractor.save_pretrained(SAVE_PATH)

        model = AutoModelForAudioClassification.from_pretrained(OLD_MODEL_ID)
        model.save_pretrained(SAVE_PATH)

        print(f"✅ SUCCESS: Restored Stable Brain at {SAVE_PATH}")

    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    revert_brain()