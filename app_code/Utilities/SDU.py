# Imports
import sounddevice as sd # type: ignore[import-untyped]
import subprocess
import time
import queue
import threading


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

class STREAM_DICT_TYPE(t.TypedDict):
    stream_obj: subprocess.Popen[bytes]
    queue: queue.Queue[bytes | None]

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
    def start_stream_subprocess(cls, device_name: str)-> subprocess.Popen[bytes]:
        '''
        This function returns the subprocess that has the currently running stream using ffmpeg
        '''        
        ffmpeg_proc = subprocess.Popen([
            "ffmpeg",
            "-y",                    # Overwrite output file without asking
            "-f", "pulse",           # PulseAudio input
            "-i", device_name,  # Your monitor source
            "-f", "mp3",             # Output format (MP3)
            "-",                     # Output to stdout (pipe)
        ], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)

        # Wait for a few seconds to ensure recording has started
        time.sleep(2)

        return ffmpeg_proc

    @classmethod
    def start_stream(cls, device_name: str, chunk_size: int = 1024) -> STREAM_DICT_TYPE:
        '''
        Returns the stream subprocess and the queque of the stream's data
        '''
        q: queue.Queue[bytes | None] = queue.Queue()
        stream_subprocess = cls.start_stream_subprocess(device_name)

        def reader_thread() -> None:
            while True:
                stdout = t.cast(t.IO[bytes], stream_subprocess.stdout)
                chunk = stdout.read(chunk_size)
                if not chunk:
                    break
                q.put(chunk)
            stdout.close()
            q.put(None)

        threading.Thread(target=reader_thread, daemon=True).start()
        return {
            "queue":q,
            "stream_obj": stream_subprocess
        }


    @classmethod
    def stop_stream(cls, stream_dict: STREAM_DICT_TYPE) -> None:
        '''
        This method grecefully stops the stream
        '''
        stream_obj = stream_dict["stream_obj"]
        try:
            stream_obj.terminate()
            stream_obj.wait(timeout=5)
        except subprocess.TimeoutExpired:
            stream_obj.kill()
        
        




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




