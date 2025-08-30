import pyttsx3
import sounddevice as sd
import numpy as np
import serial
import time

# Init serial and TTS
#ser = serial.Serial('/dev/ttyACM0', 9600) #linux based
ser = serial.Serial('COM6', 9600) #window
engine = pyttsx3.init()
text = "What a beautiful day, how are you?"

# Config
frame_duration = 0.1  # 100 ms
fs = 16000  # Sample rate

def speak_and_control(text):
    def callback(outdata, frames, time_info, status):
        pass  # We only play audio, not record

    stream = sd.OutputStream(samplerate=fs, channels=1, callback=callback)
    stream.start()

    engine.save_to_file(text, "speech.wav")
    play_and_analyze("speech.wav")
    engine.say(text)
    engine.runAndWait()
    stream.stop()
    stream.close()

def play_and_analyze(filename="speech.wav"):
    import soundfile as sf
    data, samplerate = sf.read(filename)
    chunk_size = int(frame_duration * samplerate)

    for i in range(0, len(data), chunk_size):
        chunk = data[i:i+chunk_size]
        if len(chunk) == 0:
            continue
        volume = np.linalg.norm(chunk)
        angle = int(np.clip(volume * 300, 20, 120))  # map to servo angle
        duration_ms = int(frame_duration * 1000)

        msg = f"<JAW:{angle}:{duration_ms}|HAND:90:0>\n"
        ser.write(msg.encode())
        time.sleep(frame_duration)

speak_and_control(text)
time.sleep(1)  # wait for file to be written
#play_and_analyze("speech.wav")
