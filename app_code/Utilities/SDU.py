# Imports
import sounddevice as sd # type: ignore[import-untyped]
import subprocess
import time
import queue
import threading
import os
import numpy as np

import typing as t
from numpy.typing import NDArray

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

QUEUE_STREAM_DICT_TYPE = t.TypedDict("QUEUE_STREAM_DICT_TYPE", {
    "byte_chunks_queue": t.Union[queue.Queue[bytes | None]],
    "subprocess_obj": t.Union[subprocess.Popen[bytes]]
})
    

# endregion

PCM_CODEC_BYTE_SIZE_MAPPING = {
    "s8": 1,
    "u8": 1,
    "s16le": 2,
    "s16be": 2,
    "u16le": 2,
    "u16be": 2,
    "s24le": 3,
    "s24be": 3,
    "s32le": 4,
    "s32be": 4,
    "u32le": 4,
    "u32be": 4,
    "f32le": 4,
    "f32be": 4,
    "f64le": 8,
    "f64be": 8,
    "alaw": 1,
    "mulaw": 1,
    "s16le_planar": 2,
    "s24le_planar": 3,
}

PCM_CODEC_NP_DTYPE_MAPPING = {
    's16le': np.int16
}

class SDU:
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
            "pulse_name": PLSU.get_pulse_name(sd_info_input["name"], "sinks")
        }
        
        # Get detailed information about the default output device
        sd_info_output: SD_DEVICE_INFO_DICT_TYPE = sd.query_devices(device=devices_index_dict['OUTPUT'], kind='output')
        
        # Create a new DEVICE_INFO_DICT_TYPE from the SD_DEVICE_INFO_DICT_TYPE with an additional field
        default_output_device_info: DEVICE_INFO_DICT_TYPE = {
            **sd_info_output,
            "pulse_name": PLSU.get_pulse_name(sd_info_output["name"], "sources")
        }

        
        # Make the return dict and return it
        return {
            "INPUT": default_input_device_info,
            "OUTPUT": default_output_device_info
        }

    @classmethod
    def start_stream_subprocess(cls, 
                                device_name: str, 
                                sample_rate: t.Optional[int] = None,
                                channels: t.Optional[int] = None,
                                pcm_codec: str = "s16le",
                                wait_after_start:bool = True
                                )-> subprocess.Popen[bytes]:
        '''
        This function returns the subprocess that has the currently running stream using ffmpeg
        '''      
        # Check the device name
        PLSU.check_device_name(device_name=device_name, device_type="sources")
        
        # Get the device's information
        device_info = PLSU.get_short_info(audio_type="sources")
        selected_device_info = [item for item in device_info if item["name"] == device_name][0]

        # Set default values to the optional arguments
        if sample_rate is None:
            sample_rate = selected_device_info["sample_specs"]["sample_rate"]

        if channels is None:
            channels = selected_device_info["sample_specs"]["channels"]
        

        commands_list = [
            "ffmpeg",
            "-y",                    # Overwrite output file without asking
            "-f", "pulse",           # PulseAudio input
            "-i", device_name,  # Your monitor source
            "-ac", str(channels),    
            "-ar", str(sample_rate),    
            "-f", pcm_codec,
            "-",                     # Output to stdout (pipe)
        ]

        ffmpeg_proc = subprocess.Popen(commands_list, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=0)

        # Wait for a few seconds to ensure recording has started
        if wait_after_start:
            time.sleep(2)

        return ffmpeg_proc
    
    @classmethod
    def start_byte_chunks_queue_stream(cls,
                           pulse_source_name: str,
                           chunk_size: int = 1024,
                           sample_rate: t.Optional[int] = None,
                           channels: t.Optional[int] = None,
                           pcm_codec: str = "s16le",
                           wait_after_start: bool = True,
                           verbose: bool = False
                           ) -> QUEUE_STREAM_DICT_TYPE:
        '''
        This function starts a queue stream and returns the queue stream as well as the subprocess object
        '''
        PLSU.check_device_name(pulse_source_name, "sources")

        byte_chunks_queue: queue.Queue[bytes | None] = queue.Queue()

        cls.print("Starting RAW Queue stream...", verbose)

        # Get the stream object
        subprocess_obj = cls.start_stream_subprocess(
            pulse_source_name, 
            sample_rate=sample_rate,
            channels=channels,
            pcm_codec=pcm_codec,
            wait_after_start=True
            )
        def raw_chunks_reader_thread() -> None:
            while True:
                stdout = t.cast(t.IO[bytes], subprocess_obj.stdout)
                chunk = stdout.read(chunk_size)
                if not chunk:
                    break
                byte_chunks_queue.put(chunk)
            stdout.close()
            byte_chunks_queue.put(None)

        threading.Thread(target=raw_chunks_reader_thread, daemon=True).start()

        if wait_after_start:
            time.sleep(2)

        return {
            "byte_chunks_queue": byte_chunks_queue,
            "subprocess_obj": subprocess_obj
        }

    @classmethod
    def get_time_split_queue_stream(cls,
                                    byte_chunks_queue: queue.Queue[bytes | None],
                                    pulse_source_name: str,
                                    split_interval_seconds: int,
                                    sample_rate: t.Optional[int] = None,
                                    channels: t.Optional[int] = None,
                                    pcm_codec: str = "s16le",
                                    verbose: bool = False
                                    ) -> queue.Queue[bytes | None]:
        '''
        This function will take the byte chunks queue and return another queue that is split by the specified time
        '''
        # Validate the device source name
        PLSU.check_device_name(pulse_source_name, "sources")

        # Get the information about the device to know how to split the bytes
        devices_short_info = PLSU.get_short_info("sources")
        device_info = [item for item in devices_short_info if item["name"] == pulse_source_name][0]

        # Set default values to the optional arguments
        if sample_rate is None:
            sample_rate = device_info["sample_specs"]["sample_rate"]

        if channels is None:
            channels = device_info["sample_specs"]["channels"]

        try:
            pcm_codec_bytes = PCM_CODEC_BYTE_SIZE_MAPPING[pcm_codec]
        except:
            raise ValueError(f"ERROR! The pcm_codec '{pcm_codec}' is not an allowed value! Allowed values: {list(PCM_CODEC_BYTE_SIZE_MAPPING.keys())}")

        # Calculate the split bytes
        split_bytes = (sample_rate * channels * split_interval_seconds) * pcm_codec_bytes

        time_split_q: queue.Queue[bytes | None] = queue.Queue()
        start_time = time.time()

        # In general, this function should add to a buffer and wait the wait time, then it will check if the buffer has enough byts to split and adds a new thing to the queue
        def time_split_chunks_thread() -> None:
            '''
            This function takes the bytes divided queue chunks and turns them to to time divided chunks
            '''
            # Stores incoming chunks
            buffer = b''

            while True:
                bytes_chunk = byte_chunks_queue.get()

                if bytes_chunk is not None:
                    cls.print(f"Received bytes, length of buffer: {len(buffer)}", verbose)
                    cls.print(f"Time Duration: {time.time() - start_time}", verbose)

                # LAST OF THE DATA COULD COMPRISE MORE THAN THE ALLOTTED TIME
                # I DO NOT KNOW HOW TO TAKE CARE OF THIS THOUGH
                if bytes_chunk is None:
                    # Add the last of the data, then break
                    time_split_q.put(buffer)
                    # Reset buffer
                    buffer = b''
                    break
                
                # If here, the bytes_chunk is not None
                buffer += bytes_chunk

                # Send new bytes to queue if we can
                if len(buffer) >= split_bytes:
                    time_split_q.put(buffer[:split_bytes])
                    buffer = buffer[split_bytes:]

                # If the chunk is None, send what you can, then break
                if bytes_chunk is None:
                    # Add the last of the data, then break
                    time_split_q.put(buffer)
                    # Reset buffer
                    buffer = b''
                    break
                               
            time_split_q.put(None)            

        threading.Thread(target=time_split_chunks_thread, daemon=True).start()
        return time_split_q

    @classmethod
    def start_filestream_subprocess(cls, device_name:str, filepath:str, wait_after_start:bool = True) -> subprocess.Popen[bytes]:
        '''
        This function returns the subprocess that has the currently running stream that saves to a file using ffmpeg
        '''  
        # Make sure that you can create a file there
        try:
            with open(filepath, 'w') as f:
                f.write("testing")
        except Exception as e:
            raise ValueError(f"ERROR! An error occured when testing write access using a dummy file. Error message: {e} ")

        # If here, remove the dummy file
        os.remove(filepath)
        commands_list = [
            "ffmpeg",
            "-y",                    # Overwrite output file without asking
            "-f", "pulse",           # PulseAudio input
            "-i", device_name,       # Your monitor source
            "-f", "mp3",             # Output format (MP3)
            filepath                 # Output to file

        ]
        ffmpeg_proc = subprocess.Popen(commands_list, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Wait for a few seconds to ensure recording has started
        if wait_after_start:
            time.sleep(2)

        return ffmpeg_proc


    @classmethod
    def bytes_to_np(cls,
                            raw_bytes: bytes, 
                            device_name: str,
                            channels: t.Optional[int] = None, 
                            pcm_codec: str = "s16le",
                            normalize: bool = True
                            ) -> NDArray[np.float32]:
        '''
        This function takes an audio bytes object and transforms it to a numpy array from -1 to 1 
        '''
        try:
            np_dtype = PCM_CODEC_NP_DTYPE_MAPPING[pcm_codec]
        except:
            raise ValueError(f"ERROR! pcm_codec can only be '{list(PCM_CODEC_NP_DTYPE_MAPPING.keys())}'!")
        
        # Check the device name
        PLSU.check_device_name(device_name=device_name, device_type="sources")
        
        # Get the device's information
        device_info = PLSU.get_short_info(audio_type="sources")
        selected_device_info = [item for item in device_info if item["name"] == device_name][0]

        if channels is None:
            channels = selected_device_info["sample_specs"]["channels"]


        
        # Convert bytes to NumPy array
        audio_np: NDArray[t.Any] = np.frombuffer(raw_bytes, dtype=np_dtype)

        # If stereo, reshape and take one channel (e.g. left channel)
        if channels == 2:
            audio_np = audio_np.reshape((-1, 2))
            audio_np = audio_np.mean(axis=1)

         

        if normalize:

            if np.issubdtype(audio_np.dtype, np.integer):
                max_val = np.iinfo(audio_np.dtype).max
                audio_np = audio_np.astype(np.float32) / max_val
            elif np.issubdtype(audio_np.dtype, np.floating):
                audio_np = audio_np.astype(np.float32)
            else:
                raise ValueError("Unsupported audio data type")

        return audio_np
        
        
    @classmethod
    def print(cls, value:t.Any, verbose: bool = True) -> None:
        if verbose:
            print(value)
    
    @classmethod
    def stop_subprocess(cls, subprocess: t.Union[subprocess.Popen[bytes]]) -> None:
        '''
        This function gracefully stops the subprocess sent to it
        '''
        subprocess.terminate()
        subprocess.wait()
        return




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




