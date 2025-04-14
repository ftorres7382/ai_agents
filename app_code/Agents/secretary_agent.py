import sounddevice as sd # type: ignore[import-untyped]
from dataclasses import dataclass
import numpy as np

from .base_agent import base_agent
from app_code.Utilities import SDU


@dataclass
class secretary_agent(base_agent):
    '''
    This agent will take notes of what it hears in the audio out of the computer
    '''

    def start(self) -> None:
        '''
        This command starts the model
        '''
        default_devices_index = SDU.get_default_devices_index()
        default_devices_info = SDU.get_devices_info(default_devices_index)

        # Set the pulse audio loopback
        

        print(default_devices_info)

        # print("Playing tone...")

        # # Parameters
        # duration = 5  # in seconds
        # frequency = 440.0  # Frequency in Hz (A4 note)
        # sample_rate = 44100  # Samples per second
        # volume = 0.1  # Volume level (0.0 to 1.0)

        # # Generate samples for the sine wave
        # t = np.arange(int(sample_rate * duration)) / sample_rate  # Time values
        # samples = (np.sin(2 * np.pi * frequency * t) * volume).astype(np.float32)  # sounddevice prefers float32

        # # Play the audio
        # sd.play(samples, samplerate=sample_rate)

        # # Wait until playback is finished
        # sd.wait()

