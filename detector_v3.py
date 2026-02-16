import torch
import librosa
import numpy as np
from transformers import AutoModelForAudioClassification, AutoFeatureExtractor
import torch.nn.functional as F
import os
import warnings

# Suppress warnings for cleaner terminal output
warnings.filterwarnings("ignore")

MODEL_PATH = "./models/deepfake_detector"


class VoiceFirewall:
    def __init__(self):
        print("🛡️  Initializing Firewall Logic...", end="")
        try:
            self.feature_extractor = AutoFeatureExtractor.from_pretrained(MODEL_PATH)
            self.model = AutoModelForAudioClassification.from_pretrained(MODEL_PATH)
            self.device = torch.device("cpu")
            self.model.to(self.device)
            self.model.eval()
            print(" ✅ Done!")
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {e}")
            exit(1)

    def get_jitter(self, y):
        """Calculates Vocal Jitter (Micro-tremors in pitch). Humans have it. AI is perfect."""
        try:
            f0, voiced_flag, _ = librosa.pyin(y, fmin=60, fmax=500)  # Human Voice Range
            f0 = f0[voiced_flag]
            if len(f0) < 5: return 0.0
            jitter = np.mean(np.abs(np.diff(f0))) / np.mean(f0)
            return jitter
        except:
            return 0.0

    def analyze(self, audio_path):
        if not os.path.exists(audio_path):
            return "ERROR", 0.0

        try:
            # 1. LOAD AUDIO
            y, sr = librosa.load(audio_path, sr=16000, mono=True)

            # Check for Silence
            if np.max(np.abs(y)) < 0.01:
                return "SILENCE", 0.0

            # 2. PHYSICS CHECK (Jitter)
            jitter = self.get_jitter(y)
            # Human range is typically 0.005 to 0.05. AI is often < 0.002.
            is_physically_human = (jitter > 0.005)

            # 3. AI INFERENCE
            # Hack: Add tiny noise so Loopback doesn't look "too perfect" to the AI
            y_noisy = y + np.random.normal(0, 0.001, y.shape)

            inputs = self.feature_extractor(
                y_noisy, sampling_rate=16000, return_tensors="pt",
                padding=True, truncation=True, max_length=16000 * 4
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                logits = self.model(**inputs).logits
            probs = F.softmax(logits, dim=-1)

            # 4. ROBUST LABEL DECODING (The Fix for 0.0%)
            id2label = self.model.config.id2label
            fake_prob = 0.0
            real_prob = 0.0

            # Try to read names
            for idx, label in id2label.items():
                lbl = label.lower()
                if "spoof" in lbl or "fake" in lbl:
                    fake_prob = probs[0][idx].item()
                elif "bonafide" in lbl or "real" in lbl:
                    real_prob = probs[0][idx].item()

            # FALLBACK: If names failed (both 0.0), assume Index 1 is FAKE (Standard)
            if fake_prob == 0.0 and real_prob == 0.0:
                fake_prob = probs[0][1].item()
                real_prob = probs[0][0].item()

            # 5. FINAL DECISION LOGIC
            print(f"   [Debug] AI Score: {fake_prob * 100:.1f}% Fake | Physics Jitter: {jitter:.5f}")

            # CASE A: AI says FAKE, but Physics says HUMAN
            if fake_prob > 0.50 and is_physically_human:
                print("   ⚠️  AI Hallucination detected! Physics Override engaged.")
                return "REAL", 0.95  # Force high confidence

            # CASE B: Standard AI Decision
            if fake_prob > 0.80:
                return "FAKE", fake_prob
            else:
                return "REAL", real_prob

        except Exception as e:
            print(f"Analysis Error: {e}")
            return "ERROR", 0.0


# --- RUN TEST ---
if __name__ == "__main__":
    firewall = VoiceFirewall()
    test_file = "./temp_audio/test_clip.wav"

    if os.path.exists(test_file):
        print(f"\n🔍 Analyzing: {test_file}")
        label, score = firewall.analyze(test_file)

        print("-" * 30)
        if label == "FAKE":
            print(f"⚠️  RESULT: FAKE AUDIO DETECTED! ({score * 100:.1f}%)")
        elif label == "REAL":
            print(f"✅  RESULT: REAL AUDIO ({score * 100:.1f}%)")
        else:
            print(f"ℹ️  RESULT: {label}")
        print("-" * 30)