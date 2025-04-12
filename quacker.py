import subprocess
import whisper
import wave
import sys
import pyaudio
import time

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1 if sys.platform == "darwin" else 2
RATE = 44100
RECORD_SECONDS = 2

QUACK_SLEEP = 0.5
MODEL = "tiny.en"
TMP_FILE = "/tmp/buddy-stt-out.wav"
LAUNCH_PHRASE = "go"


def beep():
    cmd = "paplay quack.opus".split()
    subprocess.call(cmd, shell=False)

def is_speech():
    return True

def recognize_segment():
    with wave.open(TMP_FILE, "wb") as wf:
        p = pyaudio.PyAudio()
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True)
        print("Recording...")
        time.sleep(QUACK_SLEEP)
        for _ in range(0, RATE // CHUNK * RECORD_SECONDS):
            wf.writeframes(stream.read(CHUNK))
        print("Done")
        stream.close()
        p.terminate()
    if not is_speech():
        return ""
    model = whisper.load_model(MODEL)
    result = model.transcribe(TMP_FILE)
    text = result['text'].lower() # pyright: ignore
    return text

def launch(text):
    cmd = []
    if "browser" in text:
        cmd = ["swaymsg", "exec", "'flatpak run app.zen_browser.zen -p default'"]
    elif "obsidian" in text:
        cmd = ["swaymsg", "exec", "'flatpak run md.obsidian.Obsidian'"]
    elif "launch" in text:
        cmd = ["swaymsg", "exec", "'rofi -show drun'"]
    elif "music" in text:
        subprocess.Popen(["swaymsg", "exec", "'strawberry -p'"], shell=False)
        return True
    if cmd:
        subprocess.Popen(cmd, shell=False)
        return True
    return False


need_quacking = True
while True:
    if not need_quacking:
        beep()
    text = recognize_segment()
    print(text)
    if need_quacking:
        need_quacking = LAUNCH_PHRASE not in text
    else:
        need_quacking = launch(text)
