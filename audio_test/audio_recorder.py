import sounddevice as sd
import soundfile as sf
import numpy as np
import threading
import sys

print(sd.query_devices())

def record_audio(filename, samplerate=44100, channels=1):
    """Records audio until Enter is pressed and saves it to a file."""
    print("Recording started. Press Enter to stop recording...")

    q = []
    
    # Create an event to signal when recording should stop
    stop_recording_event = threading.Event()

    def callback(indata, frames, time, status):
        """This is called (potentially in a separate thread) for each audio block."""
        if status:
            print(status, file=sys.stderr)
        q.append(indata.copy())
        if stop_recording_event.is_set():
            raise sd.CallbackStop

    try:
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback):
            # Wait for Enter key press in the main thread
            input()
            stop_recording_event.set() # Signal the callback to stop

        # Concatenate all recorded blocks
        print("Recording stopped. Processing audio...")
        if q:
            recorded_.audio = np.concatenate(q, axis=0)
            sf.write(filename, recorded_audio, samplerate)
            print(f"Audio saved to {filename}")
        else:
            print("No audio was recorded.")

    except Exception as e:
        print(f"An error occurred during recording: {e}")

def play_audio(filename):
    """Plays back an audio file."""
    print(f"Playing audio from {filename}...")
    try:
        data, fs = sf.read(filename, dtype='float32')
        sd.play(data, fs)
        sd.wait()  # Wait until file is done playing
        print("Audio playback finished.")
    except Exception as e:
        print(f"An error occurred during playback: {e}")

if __name__ == "__main__":
    output_filename = "output.wav"
    #record_audio(output_filename)
    #play_audio(output_filename)