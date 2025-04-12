import numpy as np
import sounddevice as sd

# Parameters
duration = 5  # in seconds
frequency = 440.0  # Frequency in Hz (A4 note)
sample_rate = 44100  # Samples per second
volume = 0.5  # Volume level (0.0 to 1.0)

# Generate samples for the sine wave
t = np.arange(int(sample_rate * duration)) / sample_rate  # Time values
samples = (np.sin(2 * np.pi * frequency * t) * volume).astype(np.float32)  # sounddevice prefers float32

# Play the audio
sd.play(samples, samplerate=sample_rate)

# Wait until playback is finished
sd.wait()
