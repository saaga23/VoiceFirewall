import torch
import librosa
import numpy as np
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torch.nn.functional as F
import os
import warnings

warnings.filterwarnings("ignore")

MODEL_PATH = "./models/deepfake_detector"


class DeepFakeDetector:
    def __init__(self):
        print("🧠 Loading AI Brain...", end="")
        try:
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_PATH)
            self.model = AutoModelForAudioClassification.from_pretrained(MODEL_PATH)
            self.device = torch.device("cpu")
            self.model.to(self.device)
            self.model.eval()
            print(" ✅ Done!")
        except Exception as e:
            print(f"\n❌ Error: {e}")
            exit(1)

    def simulate_microphone(self, y):
        """
        Hack: Loopback is too clean. We add tiny noise so AI thinks it's a mic.
        """
        # 1. Add White Noise (Dithering) - remarkably small amount (0.005)
        noise = np.random.normal(0, 0.005, y.shape)
        y_noisy = y + noise

        # 2. Normalize Volume (prevent it being too loud)
        return librosa.util.normalize(y_noisy)

    def analyze(self, audio_path):
        if not os.path.exists(audio_path):
            return "ERROR", 0.0

        try:
            # 1. Load Audio
            y, sr = librosa.load(audio_path, sr=16000, mono=True)

            # Check for silence
            if np.max(np.abs(y)) < 0.01:
                return "SILENCE", 0.0

            # 2. APPLY THE PHYSICS HACK
            y = self.simulate_microphone(y)

            # 3. AI Inference
            inputs = self.feature_extractor(
                y, sampling_rate=16000, return_tensors="pt",
                padding=True, truncation=True, max_length=16000 * 4
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.model(**inputs).logits

            probs = F.softmax(logits, dim=-1)

            # Label Mapping (Hemgg: 0=Real, 1=Fake usually)
            # We trust the raw probability for Index 1 (Fake)
            fake_score = probs[0][1].item()
            real_score = probs[0][0].item()

            # 4. Verdict (Using a safer threshold)
            if fake_score > 0.85:  # Must be VERY sure to call it Fake
                return "FAKE", fake_score
            else:
                return "REAL", real_score

        except Exception as e:
            print(f"Analysis Error: {e}")
            return "ERROR", 0.0


if __name__ == "__main__":
    brain = DeepFakeDetector()
    test_file = "./temp_audio/test_clip.wav"

    if os.path.exists(test_file):
        print(f"\n🔍 Analyzing: {test_file}")
        label, score = brain.analyze(test_file)

        if label == "FAKE":
            print(f"⚠️  RESULT: FAKE AUDIO DETECTED! ({score * 100:.1f}%)")
        elif label == "REAL":
            print(f"✅  RESULT: REAL AUDIO ({score * 100:.1f}%)")
        else:
            print(f"ℹ️  RESULT: {label}")