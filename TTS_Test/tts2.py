import pyttsx3
import sounddevice as sd
import soundfile as sf
import syllapy
import numpy as np
import serial
import time

# Init serial and TTS
ser = serial.Serial('COM6', 9600)  # Adjust COM port if needed
engine = pyttsx3.init()
text = (
    "The quick fox jumps over the lazy dog. "
    "Then he ate all grapes in a garden. "
    "A farmer got mad of the lazy dog. "
    "Next time, when the fox come over, he didn't see that dog anymore"
)

# Config
fs = 16000  # sample rate
jaw_open = 120   # max open
jaw_closed = 0   # min closed
hand_neutral = 90
hand_wave = 120


def generate_speech(text, filename="speech.wav"):
    """Generate speech audio using pyttsx3"""
    print("[INFO] Generating speech audio...")
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"[INFO] Speech saved to {filename}")


def analyze_text(text, total_duration):
    """Analyze text -> get (syllable_count, duration) per word"""
    words = text.split()
    total_syllables = sum(max(1, syllapy.count(w)) for w in words)

    print(f"[DEBUG] Total words: {len(words)}, Total syllables: {total_syllables}")
    print(f"[DEBUG] Total speech duration: {total_duration:.2f} sec")

    word_info = []
    for w in words:
        syl = max(1, syllapy.count(w))
        word_duration = total_duration * syl / total_syllables
        word_info.append((w, syl, word_duration))
        print(f"[TEXT] Word='{w}', Syllables={syl}, Duration={word_duration:.2f}s")

    return word_info


def play_and_control(filename="speech.wav", text=""):
    """Play audio and control jaw + hand movements"""
    print("[INFO] Loading audio file...")
    data, samplerate = sf.read(filename, dtype="float32")
    total_duration = len(data) / samplerate

    # Analyze text timing
    word_info = analyze_text(text, total_duration)

    print("[INFO] Starting audio playback...")
    sd.play(data, samplerate)

    # Synchronize control
    for (word, syllables, word_duration) in word_info:
        syllable_time = word_duration / syllables
        print(f"[WORD] '{word}' ({syllables} syllables, {word_duration:.2f}s)")

        # Hand gesture once per word
        msg = f"<JAW:{jaw_closed}:0|HAND:{hand_wave}:200>\n"
        ser.write(msg.encode())
        print(f"[SERVO] Hand wave -> {msg.strip()}")
        time.sleep(0.2)

        msg = f"<JAW:{jaw_closed}:0|HAND:{hand_neutral}:0>\n"
        ser.write(msg.encode())
        print(f"[SERVO] Hand back to neutral -> {msg.strip()}")

        # Jaw movements for syllables
        for s in range(syllables):
            msg = f"<JAW:{jaw_open}:{int(syllable_time*500)}|HAND:{hand_neutral}:0>\n"
            ser.write(msg.encode())
            print(f"[SERVO] Jaw OPEN (syllable {s+1}/{syllables}) -> {msg.strip()}")
            time.sleep(syllable_time / 2)

            msg = f"<JAW:{jaw_closed}:{int(syllable_time*500)}|HAND:{hand_neutral}:0>\n"
            ser.write(msg.encode())
            print(f"[SERVO] Jaw CLOSED (syllable {s+1}/{syllables}) -> {msg.strip()}")
            time.sleep(syllable_time / 2)

    sd.wait()  # wait until playback finishes
    print("[INFO] Playback and servo control finished.")


# ---- MAIN ----
generate_speech(text, "speech.wav")
time.sleep(0.5)  # wait for file to be written
play_and_control("speech.wav", text)
