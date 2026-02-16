import os
import shutil
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor

# The Model ID
MODEL_ID = "Hemgg/Deepfake-audio-detection"
SAVE_PATH = "./models/deepfake_detector"


def setup():
    print(f"⬇️  Downloading {MODEL_ID}...")

    if os.path.exists(SAVE_PATH):
        shutil.rmtree(SAVE_PATH)  # Clean up partial downloads

    try:
        # 1. Download & Save the Feature Extractor (Processor)
        print("   - Fetching Feature Extractor...")
        extractor = AutoFeatureExtractor.from_pretrained(MODEL_ID)
        extractor.save_pretrained(SAVE_PATH)

        # 2. Download & Save the Model Weights
        print("   - Fetching Model Weights...")
        model = AutoModelForAudioClassification.from_pretrained(MODEL_ID)
        model.save_pretrained(SAVE_PATH)

        print(f"✅ SUCCESS: Model verified and saved to {SAVE_PATH}")

    except Exception as e:
        print(f"❌ ERROR: {e}")


if __name__ == "__main__":
    setup()