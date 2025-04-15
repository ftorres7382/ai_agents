import sounddevice as sd # type: ignore[import-untyped]
from dataclasses import dataclass
import time

from .base_agent import base_agent
from app_code.Utilities import SDU, PLSU
import config as C


@dataclass
class secretary_agent(base_agent):
    '''
    This agent will take notes of what it hears in the audio out of the computer
    '''

    def start(self) -> None:
        '''
        This command starts the model
        '''
        print("Starting scretary agent...")
        default_devices_index = SDU.get_default_devices_index()
        default_devices_info = SDU.get_devices_info(default_devices_index)

        # PLSU.delete_pulse_loopback(C.settings['combined_audio_sink_name'])


        # Set the pulse audio loopback
        print("Creating mixed input and audio loopback device...")
        SDU.overwrite_combined_pulse_loopback(
            default_devices_info['INPUT']['pulse_name'], 
            default_devices_info['OUTPUT']['pulse_name'],
            C.settings['combined_audio_sink_name'],
            dry_run=True
            )
        
        # Start the stream
        audio_stream_dict = SDU.start_stream(
            f"{C.settings['combined_audio_sink_name']}.monitor"
        )
        start_time = time.time()
        end_sec = 10
        while (time.time() - start_time) <= end_sec:
            chunk = audio_stream_dict['queue'].get()
            if chunk is None:
                break
            print(f"Got audio chunk of size: {len(chunk)}")
        
        SDU.stop_stream(audio_stream_dict)





