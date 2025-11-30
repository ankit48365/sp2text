"""Speech-to-text recorder using OpenAI Whisper
Requires: uv add openai-whisper pyaudio speechrecognition
"""

import speech_recognition as sr  # Still used for AudioData compatibility, but optional now
import pyaudio
import os
import threading
import sys
import wave  # For saving WAV
import tempfile  # For temp file
import whisper  # New: For transcription
from datetime import datetime

# Create output directory if it doesn't exist
os.makedirs('./output', exist_ok=True)

# Load Whisper model (downloads on first run; "base" is a good start—change to "small" or "medium" for better quality)
print("Loading Whisper model...")
model = whisper.load_model("base")

def record_and_transcribe():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000  # Whisper prefers 16kHz; changed from 44.1kHz for better results

    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    frames = []
    stop_recording = threading.Event()  # Event to signal stop

    def wait_for_stop():
        """Thread to wait for Enter press to stop recording."""
        input("Press Enter to stop recording...\n")  # Blocks until Enter
        stop_recording.set()

    # Start the stop-waiting thread
    stop_thread = threading.Thread(target=wait_for_stop, daemon=True)
    stop_thread.start()

    print("Recording... (Press Enter in the terminal to stop.)")
    while not stop_recording.wait(0.1):  # Poll the event periodically
        try:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
        except IOError:
            pass  # Handle potential audio read errors gracefully

    # Cleanup
    stream.stop_stream()
    stream.close()
    p.terminate()

    if not frames:
        print("No audio recorded (stopped too quickly).")
        return

    # Save frames to temporary WAV file
    # Create a unique temporary filename manually to avoid Windows file locking issues
    timestamp_temp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    temp_filename = os.path.join(tempfile.gettempdir(), f"whisper_temp_{timestamp_temp}.wav")
    
    with wave.open(temp_filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))

    # Transcribe with Whisper
    try:
        # Verify temp file exists before transcription
        if not os.path.exists(temp_filename):
            raise FileNotFoundError(f"Temporary audio file not created: {temp_filename}")
        
        print(f"Transcribing audio file: {temp_filename} (size: {os.path.getsize(temp_filename)} bytes)")
        
        # import torch
        # print(torch.cuda.is_available())
        # print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU only")

        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        # Try transcription with fp16=False for CPU compatibility or fp16=True for GPU acceleration
        result = model.transcribe(temp_filename, fp16=(device=="cuda"))
        # result = model.transcribe(temp_filename, fp16=True)
        text = result["text"].strip()
        # print("Transcription: " + text)

        # Save to file with datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./output/transcript_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(text) 
        print(f"Saved to {filename}")

        # Clean up temp file
        os.unlink(temp_filename)

    except FileNotFoundError as e:
        print(f"File error: {e}")
        print("\nPossible issue: FFmpeg may not be installed or not in PATH.")
        print("Whisper requires FFmpeg for audio processing.")
        print("Install FFmpeg: https://www.ffmpeg.org/download.html")
        # Save error note
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./output/transcript_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(f"Error: {e}\n\nThis error typically means FFmpeg is not installed or not in your system PATH.\nPlease install FFmpeg from https://www.ffmpeg.org/download.html")
        print(f"Saved error note to {filename}")
        # Clean up temp file if it exists
        try:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
        except Exception:
            pass
    except Exception as e:
        print(f"Whisper error: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        
        # Save error note
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./output/transcript_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(f"Error during transcription: {e}\nError type: {type(e).__name__}\n\n")
            f.write("If you see 'file not found' errors, FFmpeg may be missing.\n")
            f.write("Install FFmpeg from https://www.ffmpeg.org/download.html")
        print(f"Saved error note to {filename}")
        # Clean up temp file if it exists
        try:
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
        except Exception:
            pass  # Ignore cleanup errors

def start_point():
    print("Offline Speech-to-Text Recorder (Powered by Whisper)")
    input("Press Enter to start recording...\n")

    while True:
        record_and_transcribe()
        
        user_input = input("Type 'q' to quit, or press Enter to record again: ").strip().lower()
        if user_input == 'q':
            # print("Goodbye!")
            sys.exit(0)
        else:
            print("Press Enter to start next recording...")
            input()  # Wait for Enter


if __name__ == '__main__':
    start_point()