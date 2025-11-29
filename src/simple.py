
import speech_recognition as sr

# Initialize the recognizer
r = sr.Recognizer()

# Use the microphone as the audio source
with sr.Microphone() as source:
    print("Say something!")
    # Adjust for ambient noise (optional but recommended)
    r.adjust_for_ambient_noise(source, duration=1)
    # Listen to the audio input
    audio = r.listen(source)

# Attempt to recognize the speech using PocketSphinx
try:
    text = r.recognize_sphinx(audio)
    print("You said: " + text)
except sr.UnknownValueError:
    print("Sphinx could not understand the audio")
except sr.RequestError as e:
    print(f"Sphinx error: {e}")