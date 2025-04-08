from app_code.agents.base_agent import BASE_AGENT
from app_code.Utilities.SDU import SDU
from dataclasses import dataclass

import numpy as np

@dataclass
class secretary_agent(BASE_AGENT):
    '''
    This agent will take notes of what it hears in the audio out of the computer
    '''

    def start(self) -> None:
        '''
        This command starts the model
        '''
        streams_dict = SDU.get_streaming_objects()
        output_stream = streams_dict["OUTPUT"]

        print("Playing tone...")

        # Generate a 440 Hz tone (A4 note)
        duration = 1.0  # seconds
        sample_rate = 44100
        frequency = 440.0

        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = 0.5 * np.sin(2 * np.pi * frequency * t)

        # Convert to 16-bit PCM
        tone_int16 = (tone * 32767).astype(np.int16)
        tone_bytes = tone_int16.tobytes()

        # Play the tone
        output_stream.write(tone_bytes)

        print("Tone played.")
        SDU.close_streams(streams_dict)

