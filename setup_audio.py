import os
import urllib.request

# Create assets folder
if not os.path.exists("assets"):
    os.makedirs("assets")

print("⬇️ Downloading Simulation Audio...")

# 1. Real Human Voice (President JFK speech snippet - clearly human/vintage)
# Alternative: "Baby Elephant Walk" intro or similar public domain speech
real_url = "https://www2.cs.uic.edu/~i101/SoundFiles/BabyElephantWalk60.wav"
urllib.request.urlretrieve(real_url, "assets/real_test.wav")
print("✅ Real Audio Saved: assets/real_test.wav")

# 2. Fake/Synthetic Voice (Star Wars Cantina or similar distinct sound)
# Ideally, we want a TTS sample. For now, we use a distinct electronic sample.
fake_url = "https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand60.wav"
urllib.request.urlretrieve(fake_url, "assets/fake_test.wav")
print("✅ Fake Audio Saved: assets/fake_test.wav")

print("\n🚀 Ready! Now run streamlit_app.py")