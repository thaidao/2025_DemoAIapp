import speech_recognition as sr
import openai

# Step 1: Configure your OpenAI key
openai.api_key = "ChatGPT key"

# Step 2: Initialize recognizer
recognizer = sr.Recognizer()

def get_voice_input():
    with sr.Microphone() as source:
        print("🎙️ Speak something...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print("📝 You said:", text)
            return text
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
        except sr.RequestError as e:
            print(f"⚠️ Could not request results; {e}")
    return None

def ask_chatgpt(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if available
            messages=[{"role": "user", "content": prompt}]
        )
        reply = response.choices[0].message.content.strip()
        print("🤖 ChatGPT says:", reply)
    except Exception as e:
        print(f"⚠️ Error from OpenAI: {e}")

# Main loop
if __name__ == "__main__":
    while True:
        user_input = get_voice_input()
        if user_input:
            ask_chatgpt(user_input)
