# Imports
import sounddevice as sd # type: ignore
from dataclasses import dataclass


import typing as t
from .PLSU import PLSU


##########################
# Typed Dict Definitions
##########################
# region: 
class DEVICES_INDEX_DICT_TYPE(t.TypedDict):
    INPUT: int
    OUTPUT: int

class SD_DEVICE_INFO_DICT_TYPE(t.TypedDict):
    name: str
    index: int
    hostapi: int
    max_input_channels: int
    max_output_channels: int
    default_low_input_latency: float
    default_low_output_latency: float
    default_high_input_latency: float
    default_high_output_latency: float
    default_samplerate: float

class DEVICE_INFO_DICT_TYPE(SD_DEVICE_INFO_DICT_TYPE):
    pulse_name:str

class DEVICES_INFO_DICT_TYPE(t.TypedDict):
    INPUT: DEVICE_INFO_DICT_TYPE
    OUTPUT: DEVICE_INFO_DICT_TYPE
# endregion



class SDU(PLSU):
    '''
    The Sound Device Utility (SDU) class standardizes getting information and interacting with the host's audio devices. 
    '''
    @classmethod
    def get_default_devices_index(cls) -> DEVICES_INDEX_DICT_TYPE:
        '''
        This class returns a dictionary with the indexes for the default input and output devices
        '''
        # Get default device indexes
        default_indexes = sd.default.device
        
        return {
            'INPUT': default_indexes[0],
            'OUTPUT': default_indexes[1]
        }

    @classmethod
    def get_devices_info(cls, devices_index_dict: DEVICES_INDEX_DICT_TYPE) -> DEVICES_INFO_DICT_TYPE:
        '''
        This function gets the information for a given input and output device index dictionary
        '''

        # Get detailed information about the default input device
        sd_info_input: SD_DEVICE_INFO_DICT_TYPE = sd.query_devices(device=devices_index_dict['INPUT'], kind='input')
        
        # Create a new DEVICE_INFO_DICT_TYPE from the SD_DEVICE_INFO_DICT_TYPE with an additional field
        default_input_device_info: DEVICE_INFO_DICT_TYPE = {
            **sd_info_input,
            "pulse_name": cls.get_pulse_name(sd_info_input["name"], "sinks")
        }
        
        # Get detailed information about the default output device
        sd_info_output: SD_DEVICE_INFO_DICT_TYPE = sd.query_devices(device=devices_index_dict['OUTPUT'], kind='output')
        
        # Create a new DEVICE_INFO_DICT_TYPE from the SD_DEVICE_INFO_DICT_TYPE with an additional field
        default_output_device_info: DEVICE_INFO_DICT_TYPE = {
            **sd_info_output,
            "pulse_name": cls.get_pulse_name(sd_info_output["name"], "sources")
        }
        
        # Make the return dict and return it
        return {
            "INPUT": default_input_device_info,
            "OUTPUT": default_output_device_info
        }

    @classmethod
    def start_stream(cls, device_name: str, to_file:bool = False, overwrite:bool=True)-> None:
        '''
        This function returns the subprocess that has the currently running stream using ffmpeg
        '''
        if not overwrite:
            raise NotImplementedError("ERROR! overwrite=False has not been implemented yet!")
        
        if to_file:
            raise NotImplementedError("ERROR! to_file=True has not been implemented yet!")
        




'''
import subprocess
import time

# Start the ffmpeg process to record and stream to MP3
ffmpeg_proc = subprocess.Popen([
    "ffmpeg",
    "-y",                    # Overwrite output file without asking
    "-f", "pulse",           # PulseAudio input
    "-i", "ai_agents_combined_sink.monitor",  # Your monitor source
    "-f", "mp3",             # Output format (MP3)
    "output.mp3"
], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

# Wait for a few seconds to ensure recording has started
time.sleep(2)

# Open the MP3 file for reading (non-blocking)
with open("output.mp3", "rb") as file:
    while True:
        data = file.read(1024)
        if not data:
            break
        # Process the chunk of data (e.g., send it to another program or process)
        print("Reading chunk...")

# Stop the ffmpeg process
ffmpeg_proc.terminate()
ffmpeg_proc.wait()


Get data directly using PIPE
import subprocess
import time

# Start the ffmpeg process to stream audio to a pipe
ffmpeg_proc = subprocess.Popen([
    "ffmpeg",
    "-y",                    # Overwrite output file without asking
    "-f", "pulse",           # PulseAudio input
    "-i", "ai_agents_combined_sink.monitor",  # Your monitor source
    "-f", "mp3",             # Output format (MP3)
    "-",                     # Output to stdout (pipe)
], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

# Wait for a few seconds to ensure recording has started
time.sleep(2)

# Read from the pipe as ffmpeg streams the MP3 data
while True:
    data = ffmpeg_proc.stdout.read(1024)
    if not data:
        break
    # Process the chunk of data (e.g., send it to another program)
    print("Reading chunk...")

# Stop the ffmpeg process
ffmpeg_proc.terminate()
ffmpeg_proc.wait()


'''




