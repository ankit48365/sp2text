"""
install these 
    "pocketsphinx>=5.0.4",
    "pyaudio>=0.2.14",
    "speechrecognition>=3.14.4",
    
"""


import speech_recognition as sr
import pyaudio
import os
from datetime import datetime
import threading
import sys

# Create output directory if it doesn't exist
os.makedirs('./output', exist_ok=True)

def record_and_transcribe():
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

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

    # Create AudioData from frames
    raw_audio = b''.join(frames)
    audio_data = sr.AudioData(raw_audio, RATE, 2)  # 2 bytes per sample for paInt16

    # Recognize speech
    r = sr.Recognizer()
    try:
        # Optional: Adjust for ambient noise (uncomment if needed, but adds delay)
        # r.adjust_for_ambient_noise(audio_data)
        text = r.recognize_sphinx(audio_data)
        print("Transcription: " + text)

        # Save to file with datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./output/transcript_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(text)
        print(f"Saved to {filename}")

    except sr.UnknownValueError:
        print("Sphinx could not understand the audio")
        # Still save empty or note
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./output/transcript_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write("No transcription (unrecognized audio)")
        print(f"Saved note to {filename}")
    except sr.RequestError as e:
        print(f"Sphinx error: {e}")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"./output/transcript_{timestamp}.txt"
        with open(filename, 'w') as f:
            f.write(f"Error: {e}")
        print(f"Saved error note to {filename}")

# Main loop for multiple recordings
print("Speech-to-Text Recorder")
print("Press Enter to start the first recording. After stopping, type 'q' to quit or press Enter to record again.")

# Wait for Enter to start first time
input("Press Enter to start recording...\n")

while True:
    record_and_transcribe()
    
    user_input = input("Type 'q' to quit, or press Enter to record again: ").strip().lower()
    if user_input == 'q':
        print("Goodbye!")
        sys.exit(0)
    else:
        print("Press Enter to start next recording...")
        input()  # Wait for Enter