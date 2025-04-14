# Imports
import sounddevice as sd # type: ignore
import subprocess


import typing as t
from app_code.literals import VALID_PULSE_AUDIO_VALUES

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
            "pulse_name": cls.get_pulse_name(sd_info_input["name"], "sink")
        }
        
        # Get detailed information about the default output device
        sd_info_output: SD_DEVICE_INFO_DICT_TYPE = sd.query_devices(device=devices_index_dict['OUTPUT'], kind='output')
        
        # Create a new DEVICE_INFO_DICT_TYPE from the SD_DEVICE_INFO_DICT_TYPE with an additional field
        default_output_device_info: DEVICE_INFO_DICT_TYPE = {
            **sd_info_output,
            "pulse_name": cls.get_pulse_name(sd_info_output["name"], "source")
        }
        
        # Make the return dict and return it
        return {
            "INPUT": default_input_device_info,
            "OUTPUT": default_output_device_info
        }

    @classmethod
    def get_pulse_name(cls, sd_name: str, pulse_audio_type: VALID_PULSE_AUDIO_VALUES) -> str:
        '''
        This class translates the sd name to the pulse audio name
        
        Only the default is currently implemented
        '''
        if sd_name != "default":
            raise NotImplementedError("ERROR! Non Default names have not been implemented yet!")
        command = "pactl info | grep "+ f'"Default {pulse_audio_type[0].upper() + pulse_audio_type[1:]}"'
        result = subprocess.run(command, capture_output=True, shell=True, text=True)
        
        result_str: str = str(result.stdout).replace("\n", "")
        
        final_result = result_str.split(": ")[-1]
        
        
        return final_result

    @classmethod
    def overwrite_pulse_loopback(cls, ):
        '''
        This method overwrites whatever the current pulse config is with the one sent to it
        
        The loopback created will combine INPUT and OUTPUT
        '''



