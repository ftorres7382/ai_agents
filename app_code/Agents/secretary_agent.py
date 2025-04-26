import time
import shutil
import os
from datetime import datetime
import whisper # type: ignore[import-untyped]
import torch
import numpy as np
import vosk # type: ignore[import-untyped]

import typing as t
from app_code.literals import VALID_MODEL_NAMES
from app_code.Utilities.SDU import DEVICES_INFO_DICT_TYPE


from .base_agent import base_agent
from app_code.Utilities import SDU, PLSU
import config as C



class secretary_agent(base_agent):
    '''
    This agent will take notes of what it hears in the audio out of the computer
    '''

    _REL_DIR_STRUCTURE = {
        "secretary_agent":{
            "audio_recordings":{
                "raw": None,
                "VAD": None,
            },
            "transcriptions": {
                "raw": None,
                "summary": None
            }
        }
    }

    def __init__(self, 
                 name: str,
                 ollama_model_name: VALID_MODEL_NAMES,
                 transcription_model_name: t.Literal["tiny", "base", "small", "medium", "large", "turbo"], 
                 verbose: bool = True):
        super().__init__(name=name, verbose=verbose)
        self.ollama_model_name = ollama_model_name
        self.transcription_model_name = transcription_model_name

        self.transcription_model = whisper.load_model(self.transcription_model_name)
        passive_transcription_vosk_model_path = "assets/models/vosk-model-en-us-0.42-gigaspeech"
        self.passive_transcription_model = vosk.Model(passive_transcription_vosk_model_path)


    
    @classmethod
    def get_flattened_dir_structure(cls) -> t.List[str]:
        '''
        This function returns the flattened version of the dir structure
        '''
        dirs_list: t.List[str] = []

        def flatten_dict(d: t.Any, parent_key: str='', sep:str='/') -> None:
            for k, v in d.items():
                new_key = f"{parent_key}{sep}{k}" if parent_key else k
                dirs_list.append(new_key)
                if isinstance(v, dict):
                    flatten_dict(v, new_key, sep=sep)


        flatten_dict(cls._REL_DIR_STRUCTURE)
        return dirs_list

    @classmethod
    def data_folder_setup(cls, overwrite: bool = False) -> None:
        '''
        This function checks if the secretary data folder is set up correctly, if not it will set it up correctly
        '''
        
        if overwrite:
            for dir_path in list(cls._REL_DIR_STRUCTURE):
                complete_dir_path = os.path.join(C.settings["save_folder_path"])
                shutil.rmtree(complete_dir_path)
        # Flatten out the dir structure
        dirs_list = cls.get_flattened_dir_structure()
        complete_dirs_list = [os.path.join(C.settings["save_folder_path"], dir_path) for dir_path in dirs_list]
        for dir_path in complete_dirs_list:
            if not os.path.exists(dir_path):
                os.mkdir(dir_path)

        return
       
    def setup_audio_loopback(self, default_source: bool = True, default_sink:bool = True) -> DEVICES_INFO_DICT_TYPE:
        '''
        This function sets up the audio loopback
        '''
        if default_source != True or default_sink != True:
            raise NotImplementedError("ERROR! Custom mixing of soruce and sink has not been implemented yet!")
        
        self.print("Setting up Audio Devices...\n")
        default_devices_index = SDU.get_default_devices_index()
        default_devices_info = SDU.get_devices_info(default_devices_index)
        # Set the pulse audio loopback
        self.print("Setting up mixed input and audio loopback device...")

        PLSU.overwrite_combined_pulse_loopback(
            default_devices_info['INPUT']['pulse_name'], 
            default_devices_info['OUTPUT']['pulse_name'],
            C.settings['combined_audio_sink_name']
            )
        return default_devices_info


    def start_passive_listen(self, 
                             loopback_devices_info: DEVICES_INFO_DICT_TYPE, 
                             pulse_source_name: str, 
                             sample_rate:int = 16000, 
                             split_interval_seconds: int = 3) -> None:
        '''
        This function passively listens to the user until it detects that the user is speaking to it
        '''
        self.print("Setting up audio streams...")
        queue_stream_dict = SDU.start_byte_chunks_queue_stream(
            pulse_source_name=pulse_source_name,
            sample_rate=sample_rate

        )
        
        time_split_q = SDU.get_time_split_queue_stream(
            byte_chunks_queue=queue_stream_dict["byte_chunks_queue"],
            pulse_source_name=pulse_source_name,
            split_interval_seconds=split_interval_seconds,
            sample_rate=sample_rate
        )

        # Start passive listening loop
        rec = vosk.KaldiRecognizer(self.passive_transcription_model, sample_rate)
        window = 5
        try: 
            self.print("Starting passive listening loop ...")
            while True:
                q = time_split_q
                bytes_chunk = q.get()
                if bytes_chunk is None:
                    break
                
                # Turn bytes chunk to numpy to standardize the input
                audio_np_array = SDU.bytes_to_np(bytes_chunk, device_name=loopback_devices_info["OUTPUT"]["pulse_name"], normalize=False)
                audio_bytes = audio_np_array.tobytes()


                if rec.AcceptWaveform(audio_bytes):
                    result = rec.Result()
                else:
                    result = rec.PartialResult()

                print(result)
        except KeyboardInterrupt:
            SDU.stop_subprocess(queue_stream_dict["subprocess_obj"])



    def start(self) -> None:
        '''
        This command starts the model
        '''
        self.print("Starting scretary agent...\n")


        self.print("Checking data folder...\n")
        self.data_folder_setup()
        
        # Setup mixed audio
        pulse_source_name = f"{C.settings['combined_audio_sink_name']}.monitor"
        loopback_devices_info = self.setup_audio_loopback()

        # Start passive listening
        self.start_passive_listen(loopback_devices_info = loopback_devices_info,
                                  pulse_source_name = pulse_source_name,
                                  split_interval_seconds= 3
                                  )


        

        return





