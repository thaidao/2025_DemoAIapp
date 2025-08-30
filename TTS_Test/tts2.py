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
jaw_open = 0   # max open
jaw_closed = 120   # min closed
hand_neutral = 90
hand_wave = 120


def ts():
    """Return formatted timestamp in ms"""
    return f"{time.time():.3f}s"


def generate_speech(text, filename="speech.wav"):
    """Generate speech audio using pyttsx3"""
    print(f"{ts()} [INFO] Generating speech audio...")
    engine.save_to_file(text, filename)
    engine.runAndWait()
    print(f"{ts()} [INFO] Speech saved to {filename}")


def analyze_text(text, total_duration):
    """Analyze text -> get (syllable_count, duration) per word"""
    words = text.split()
    total_syllables = sum(max(1, syllapy.count(w)) for w in words)

    print(f"{ts()} [DEBUG] Total words: {len(words)}, Total syllables: {total_syllables}")
    print(f"{ts()} [DEBUG] Total speech duration: {total_duration:.2f} sec")

    word_info = []
    for w in words:
        syl = max(1, syllapy.count(w))
        word_duration = total_duration * syl / total_syllables
        word_info.append((w, syl, word_duration))
        print(f"{ts()} [TEXT] Word='{w}', Syllables={syl}, Duration={word_duration:.2f}s")

    return word_info


def play_and_control(filename="speech.wav", text=""):
    """Play audio and control jaw + hand movements"""
    print(f"{ts()} [INFO] Loading audio file...")
    data, samplerate = sf.read(filename, dtype="float32")
    total_duration = len(data) / samplerate

    # Analyze text timing
    word_info = analyze_text(text, total_duration)

    print(f"{ts()} [INFO] Starting audio playback...")
    sd.play(data, samplerate)

    # Synchronize control
    for (word, syllables, word_duration) in word_info:
        syllable_time = word_duration / syllables
        print(f"{ts()} [WORD] '{word}' ({syllables} syllables, {word_duration:.2f}s)")

        # Hand gesture once per word
        msg = f"<JAW:{jaw_closed}:0|HAND:{hand_wave}:200>\n"
        ser.write(msg.encode())
        print(f"{ts()} [SERVO] Hand wave -> {msg.strip()}")
        #time.sleep(0.2)

        msg = f"<JAW:{jaw_closed}:0|HAND:{hand_neutral}:0>\n"
        ser.write(msg.encode())
        print(f"{ts()} [SERVO] Hand back to neutral -> {msg.strip()}")

        # Jaw movements for syllables
        for s in range(syllables):
            msg = f"<JAW:{jaw_open}:{int(syllable_time*500)}|HAND:{hand_neutral}:0>\n"
            ser.write(msg.encode())
            print(f"{ts()} [SERVO] Jaw OPEN (syllable {s+1}/{syllables}) -> {msg.strip()}")
            time.sleep(syllable_time / 2.5)

            msg = f"<JAW:{jaw_closed}:{int(syllable_time*500)}|HAND:{hand_neutral}:0>\n"
            ser.write(msg.encode())
            print(f"{ts()} [SERVO] Jaw CLOSED (syllable {s+1}/{syllables}) -> {msg.strip()}")
            time.sleep(syllable_time / 2.5)

    sd.wait()  # wait until playback finishes
    print(f"{ts()} [INFO] Playback and servo control finished.")
    
    # msg = f"<JAW:{jaw_open}:{jaw_closed}|HAND:{hand_neutral}:0>\n"
    # print(msg)
    # ser.write(msg.encode())


# ---- MAIN ----
generate_speech(text, "speech.wav")
time.sleep(0.5)  # wait for file to be written
play_and_control("speech.wav", text)
