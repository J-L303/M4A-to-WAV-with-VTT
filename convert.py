import sys
import importlib.machinery
import importlib.util
import os
from pathlib import Path

# Fix for Python 3.13 removing audioop
pyaudioop_path = os.path.join(
    "/Library/Frameworks/Python.framework/Versions/3.13/lib/python3.13/site-packages",
    "pydub",
    "pyaudioop.py",
)

loader = importlib.machinery.SourceFileLoader("audioop", pyaudioop_path)
spec = importlib.util.spec_from_loader(loader.name, loader)
mod = importlib.util.module_from_spec(spec)
loader.exec_module(mod)
sys.modules["audioop"] = mod

from pydub import AudioSegment
import whisper

file_name = input("Enter m4a file: ").strip()

base = Path(file_name).stem
m4a_file = file_name
wav_filename = f"{base}.wav"
vtt_filename = f"{base}_script.vtt"

# Convert m4a → wav
sound = AudioSegment.from_file(m4a_file, format="m4a")
sound.export(wav_filename, format="wav")

# Load Whisper model
model = whisper.load_model("base")

# Transcribe
result = model.transcribe(wav_filename)

def format_timestamp(seconds):
    ms = int((seconds % 1) * 1000)
    s = int(seconds) % 60
    m = int(seconds // 60) % 60
    h = int(seconds // 3600)
    return f"{h:02}:{m:02}:{s:02}.{ms:03}"   # VTT uses .

with open(vtt_filename, "w") as f:
    f.write("WEBVTT\n\n")

    for seg in result["segments"]:
        start = format_timestamp(seg["start"])
        end = format_timestamp(seg["end"])
        text = seg["text"].strip()

        f.write(f"{start} --> {end}\n{text}\n\n")

print(f"Converted {m4a_file} → {wav_filename} → {vtt_filename}")
