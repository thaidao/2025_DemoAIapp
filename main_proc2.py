import openai
import speech_recognition as sr

# Step 1: Set up the OpenAI client
client = openai.OpenAI(api_key=openAPIkey")  # 👈 Replace this with your actual key

# Step 2: Initialize the recognizer
recognizer = sr.Recognizer()

def get_voice_input():
    with sr.Microphone() as source:
        print("\n🎙️ Speak something...")
        recognizer.adjust_for_ambient_noise(source)
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
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Or gpt-4 if you have access
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        reply = response.choices[0].message.content.strip()
        print("🤖 ChatGPT says:", reply)
        return reply
    except Exception as e:
        print(f"⚠️ Error from OpenAI: {e}")
        return None

# Main loop
if __name__ == "__main__":
    while True:
        voice_text = get_voice_input()
        if voice_text:
            ask_chatgpt(voice_text)
