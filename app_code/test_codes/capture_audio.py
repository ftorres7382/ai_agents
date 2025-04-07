import pyaudio
import numpy as np

sample_rate = 44100
channels = 2  # Set channels to 1 for mono
frames_per_buffer = 1024

# Initialize PyAudio
p = pyaudio.PyAudio()

# Get the default output device index
output_device_index = p.get_default_output_device_info()['index']

# Open the stream to capture audio from the default output device
stream = p.open(format=pyaudio.paInt16,
                channels=channels,
                rate=sample_rate,
                input=False,
                output=True,
                input_device_index=output_device_index,
                frames_per_buffer=frames_per_buffer)

print("Capturing audio from the default output device...")

# Continuously read and process the audio data from the output device
while True:
    data = np.frombuffer(stream.read(frames_per_buffer), dtype=np.int16)
    print(data)  # Process or output the captured audio (e.g., print, save, etc.)

# Close the stream after you're done
stream.stop_stream()
stream.close()
p.terminate()
