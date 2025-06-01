import whisper
import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav
import tempfile
import openai

# Set up OpenRouter API
openai.api_key = "openRouterKey"  # 👈 Replace this
openai.api_base = "https://openrouter.ai/api/v1"

# Load Whisper model (base is fast and reasonably accurate)
model = whisper.load_model("base")

def record_audio(duration=5, fs=16000):
    print(f"🎙️ Recording for {duration} seconds...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    
    # Save to a temporary WAV file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
    wav.write(temp_file.name, fs, np.int16(audio * 32767))
    print(f"✅ Audio saved to {temp_file.name}")
    return temp_file.name

def transcribe_audio(audio_path):
    print("🧠 Transcribing audio with Whisper...")
    result = model.transcribe(audio_path)
    print("📝 You said:", result["text"])
    return result["text"]

def ask_ai(message):
    print("🤖 Sending message to ChatGPT...")
    response = openai.ChatCompletion.create(
        model="openai/gpt-3.5-turbo",  # Or try another model like "anthropic/claude-3-sonnet"
        messages=[{"role": "user", "content": message}]
    )
    reply = response.choices[0].message.content.strip()
    print("🤖 ChatGPT replies:", reply)
    return reply

# 🧪 Demo run
if __name__ == "__main__":
    audio_path = record_audio(duration=5)
    user_text = transcribe_audio(audio_path)
    if user_text:
        ask_ai(user_text)