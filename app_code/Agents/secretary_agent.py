from dataclasses import dataclass
import time
import shutil
import typing as t
import os
from datetime import datetime


from .base_agent import base_agent
from app_code.Utilities import SDU, PLSU
import config as C


@dataclass
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
       
        

    def start(self) -> None:
        '''
        This command starts the model
        '''
        self.print("Starting scretary agent...\n")

        self.print("Checking data folder...\n")
        self.data_folder_setup()
        
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
        
        
        # Start the stream
        pulse_source_name = f"{C.settings['combined_audio_sink_name']}.monitor"
        queue_stream_dict = SDU.start_byte_chunks_queue_stream(
            pulse_source_name=pulse_source_name            
        )
        time_split_q = SDU.get_time_split_queue_stream(
            byte_chunks_queue=queue_stream_dict["byte_chunks_queue"],
            pulse_source_name=pulse_source_name,
            split_interval_seconds=1
        )

        start_time = time.time()
        end_sec = 10
        while (time.time() - start_time) <= end_sec:
            q = time_split_q
            if q is not None:
                chunk = q.get()
                if chunk is None:
                    break
                print(f"Got audio chunk of size: {len(chunk)}")
            else:
                print("Sleeping...")
                time.sleep(.5)


        return


        audio_dirpath = os.path.join(C.settings["save_folder_path"], "secretary_agent", "audio_recordings", "raw")
        
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S-%f")[:-3]
        audio_filepath = os.path.join(audio_dirpath, timestamp + ".mp3")



        start_time = time.time()
        end_sec = 10
        while (time.time() - start_time) <= end_sec:
            q = queue_stream_dict["byte_chunks_queue"]
            if q is not None:
                chunk = q.get()
                if chunk is None:
                    break
                print(f"Got audio chunk of size: {len(chunk)}")
            else:
                print("Sleeping...")
                time.sleep(.5)



        return
    
        audio_stream_dict = SDU.start_stream(
            f"{C.settings['combined_audio_sink_name']}.monitor",
            start_queue_stream=True,
            start_filestream=True,
            filestream_filepath=audio_filepath,
            verbose=self.verbose
        )
        start_time = time.time()
        end_sec = 10
        while (time.time() - start_time) <= end_sec:
            if audio_stream_dict["queue"] is not None:
                chunk = audio_stream_dict['queue'].get()
                if chunk is None:
                    break
                print(f"Got audio chunk of size: {len(chunk)}")
            else:
                print(audio_stream_dict)
                print("Sleeping...")
                time.sleep(.5)
        
        # Note use SpeechBrain VAD, ASR, speaker ID. Check it out later
        # Or just use faster whisper
        '''
        pip install faster-whisper
        
        from faster_whisper import WhisperModel

        model = WhisperModel("base", compute_type="int8")  # or "small", "medium"
        segments, info = model.transcribe("audio.wav", vad_filter=True)

        for segment in segments:
            print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")

        Buut SpeechBrain Has built-in speaker diarization pipeline:
        from speechbrain.pretrained import SpeakerDiarization
        diarize = SpeakerDiarization.from_hparams("speechbrain/speaker-diarization")
        segments = diarize("audio.wav")

        '''


        SDU.stop_stream(audio_stream_dict)





