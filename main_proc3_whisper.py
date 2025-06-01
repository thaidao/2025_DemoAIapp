import os
import whisper
import sounddevice as sd
import scipy.io.wavfile as wav
from openai import OpenAI

# ✅ CONFIGURATION
DURATION = 5  # seconds
OUTPUT_FILE = "recorded_audio.wav"
OPENROUTER_API_KEY = "tbd"  # Replace with your key

# ✅ RECORD AUDIO
def record_audio(filename, duration):
    print("🎙️ Recording... Speak now.")
    fs = 44100  # Sample rate
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    wav.write(filename, fs, audio)
    print("✅ Recording finished.")

# ✅ TRANSCRIBE AUDIO USING WHISPER
def transcribe_audio(filename):
    print("🧠 Transcribing audio...")
    model = whisper.load_model("base")  # You can also try 'tiny' or 'small'
    result = model.transcribe(filename)
    print("📜 Transcription:", result["text"])
    return result["text"]

# ✅ SEND TEXT TO OPENROUTER GPT MODEL
def ask_chatgpt(prompt):
    client = OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )

    response = client.chat.completions.create(
        model="openai/gpt-3.5-turbo",  # You can change model here
        messages=[{"role": "user", "content": prompt}],
    )

    return response.choices[0].message.content

# ✅ MAIN FLOW
if __name__ == "__main__":
    record_audio(OUTPUT_FILE, DURATION)
    text = transcribe_audio(OUTPUT_FILE)
    
    print("🤖 Sending to ChatGPT (via OpenRouter)...")
    reply = ask_chatgpt(text)
    
    print("\n💬 AI Response:")
    print(reply)
