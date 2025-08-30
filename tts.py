import pyttsx3
import sounddevice as sd
import soundfile as sf
import numpy as np
import serial
import time
import threading

# Init serial and TTS
ser = serial.Serial('COM6', 9600)  # Windows COM port
engine = pyttsx3.init()
# text = "What a beautiful day, how are you?"
text = "The quick fox jumps over the lazy dog. Then he ate all grapes in a garden. A farmer got mad of the lazy dog. Next time, when the fox come over, he didn't see that dog anymore"

# Config
frame_duration = 0.1  # 100 ms
fs = 16000  # Sample rate


def generate_speech(text, filename="speech.wav"):
    """Generate TTS audio file"""
    engine.save_to_file(text, filename)
    engine.runAndWait()


def play_and_analyze(filename="speech.wav"):
    """Play audio and control servos in sync"""
    data, samplerate = sf.read(filename, dtype="float32")
    chunk_size = int(frame_duration * samplerate)

    # index pointer for chunks
    frame_idx = [0]

    def callback(outdata, frames, time_info, status):
        if status:
            print(status)

        start = frame_idx[0]
        end = start + frames
        if end > len(data):
            outdata[: len(data) - start] = data[start:]
            outdata[len(data) - start :] = 0
            raise sd.CallbackStop()

        out_chunk = data[start:end]
        outdata[:] = out_chunk.reshape(-1, 1)

        # ---- Servo control ----
        # Use same chunk to calculate volume
        chunk = out_chunk
        volume = np.linalg.norm(chunk)
        angle = int(np.clip(volume * 300, 0, 100))  # map to servo angle from 0 to 120 degree,  # jaw: 0 = closed, 120 = wide open
        duration_ms = int(frame_duration * 1000)

        msg = f"<JAW:{angle}:{duration_ms}|HAND:90:0>\n"
        ser.write(msg.encode())

        # move index forward
        frame_idx[0] = end

    with sd.OutputStream(samplerate=samplerate, channels=1, callback=callback):
        sd.sleep(int(len(data) / samplerate * 1000))  # wait until playback done


# ---- Main ----
generate_speech(text, "speech.wav")
time.sleep(0.5)  # ensure file is written
play_and_analyze("speech.wav")
