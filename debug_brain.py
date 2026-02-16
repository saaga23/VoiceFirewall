import torch
import librosa
import numpy as np
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torch.nn.functional as F

MODEL_PATH = "./models/deepfake_detector"
TEST_FILE = "./temp_audio/test_clip.wav"


def show_raw_numbers():
    print(f"🔍 INSPECTING RAW OUTPUT for {TEST_FILE}...")

    # Load Brain
    feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_PATH)
    model = AutoModelForAudioClassification.from_pretrained(MODEL_PATH)

    # Load Audio
    y, sr = librosa.load(TEST_FILE, sr=16000, mono=True)
    inputs = feature_extractor(y, sampling_rate=16000, return_tensors="pt", padding=True, truncation=True,
                               max_length=16000 * 4)

    # Predict
    with torch.no_grad():
        logits = model(**inputs).logits

    probs = F.softmax(logits, dim=-1)

    # PRINT EVERYTHING
    print("\n--- RAW MODEL CONFIDENCE ---")
    id2label = model.config.id2label

    # Print Score for ID 0
    score_0 = probs[0][0].item()
    label_0 = id2label[0]
    print(f"   ID 0 ({label_0}): {score_0:.4f}  ({score_0 * 100:.1f}%)")

    # Print Score for ID 1
    score_1 = probs[0][1].item()
    label_1 = id2label[1]
    print(f"   ID 1 ({label_1}): {score_1:.4f}  ({score_1 * 100:.1f}%)")

    print("----------------------------")

    if score_0 > score_1:
        print(f"👉 Model votes for: ID 0 ({label_0})")
    else:
        print(f"👉 Model votes for: ID 1 ({label_1})")


if __name__ == "__main__":
    show_raw_numbers()