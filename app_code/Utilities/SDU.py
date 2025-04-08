'''
SDU (Sound Utility)

This file is the Sound Utility. 
It uses the pyaudio module to stream, process and echo audio and microphone data

The class is type checked using mypy --strict

AI Context:
Keep this description section, including the AI Context
Do all imports below this section
When importing typing, import it as t
'''


# Imports
import pyaudio
import typing as t

class _DEFAULT_DEVICE_INDEXES_DICT_TYPE(t.TypedDict):
    INPUT: int
    OUTPUT: int

class _DEVICE_INFO_DICT_TYPE(t.TypedDict):
    index: int
    structVersion: int
    name: str
    hostApi: int
    maxInputChannels: int
    maxOutputChannels: int
    defaultLowInputLatency: float
    defaultLowOutputLatency: float
    defaultHighInputLatency: float
    defaultHighOutputLatency: float
    defaultSampleRate: int

class _DEFAULT_DEVICES_STREAM_DICT_TYPE(t.TypedDict):
    INPUT: pyaudio.Stream
    OUTPUT: pyaudio.Stream
    PYAUDIO: pyaudio.PyAudio

class _DEFAULT_DEVICES_INFO_DICT_TYPE(t.TypedDict):
    INPUT: _DEVICE_INFO_DICT_TYPE
    OUTPUT: _DEVICE_INFO_DICT_TYPE

class SDU:
    '''
    This class is a helper class for streaming input and output audio
    '''

    @classmethod
    def close_streams(cls, streams_dict: _DEFAULT_DEVICES_STREAM_DICT_TYPE) -> None:
        '''
        This function will close and terminate all the streams in the dictionary
        '''
        streams_dict["INPUT"].stop_stream()
        streams_dict["INPUT"].close()
        
        streams_dict["OUTPUT"].stop_stream()
        streams_dict["OUTPUT"].close()
        
        streams_dict["PYAUDIO"].terminate()

    @classmethod
    def get_streaming_objects(cls, frames_per_buffer: int = 1024) -> _DEFAULT_DEVICES_STREAM_DICT_TYPE:
        '''
        This function returns the streaming objects for the default INPUT and OUTPUT.
        '''
        default_devices_info = cls.get_default_devices_info()
        p = pyaudio.PyAudio()
        

        return_dict: _DEFAULT_DEVICES_STREAM_DICT_TYPE = {
            
            "INPUT": p.open(
                format=pyaudio.paInt16,
                channels=default_devices_info["INPUT"]["maxInputChannels"],
                rate=default_devices_info["INPUT"]['defaultSampleRate'],
                input=True,
                input_device_index=default_devices_info["INPUT"]["index"],
                frames_per_buffer=frames_per_buffer
            ),
            "OUTPUT": p.open(
                format=pyaudio.paInt16,
                channels=default_devices_info["OUTPUT"]["maxOutputChannels"],
                rate=int(default_devices_info["OUTPUT"]['defaultSampleRate']),
                output=True,
                output_device_index=default_devices_info["OUTPUT"]["index"],
                frames_per_buffer=frames_per_buffer
            ),
            "PYAUDIO": p
        }
        return return_dict

    @classmethod
    def get_default_devices_info(cls) -> _DEFAULT_DEVICES_INFO_DICT_TYPE:
        '''
        Returns the default devices information using the other methods of the classes up until now
        '''
        indexes = cls.get_default_device_indexes()

        result: _DEFAULT_DEVICES_INFO_DICT_TYPE = {
            "INPUT": cls.get_device_info_by_index(indexes["INPUT"]),
            "OUTPUT": cls.get_device_info_by_index(indexes["OUTPUT"])
        }

        return result
    

    @classmethod
    def get_device_info_by_index(cls, index: int) -> _DEVICE_INFO_DICT_TYPE:
        '''
        Gets the dictionary settings for the device information, given the index
        '''
        p = pyaudio.PyAudio()

        raw_info = p.get_device_info_by_index(index)

        result: _DEVICE_INFO_DICT_TYPE = {
            'index': int(raw_info['index']),
            'structVersion': int(raw_info['structVersion']),
            'name': str(raw_info['name']),
            'hostApi': int(raw_info['hostApi']),
            'maxInputChannels': int(raw_info['maxInputChannels']),
            'maxOutputChannels': int(raw_info['maxOutputChannels']),
            'defaultLowInputLatency': float(raw_info['defaultLowInputLatency']),
            'defaultLowOutputLatency': float(raw_info['defaultLowOutputLatency']),
            'defaultHighInputLatency': float(raw_info['defaultHighInputLatency']),
            'defaultHighOutputLatency': float(raw_info['defaultHighOutputLatency']),
            'defaultSampleRate': int(raw_info['defaultSampleRate']),
        }

        return result



        

    
    @classmethod
    def get_default_device_indexes(cls) -> _DEFAULT_DEVICE_INDEXES_DICT_TYPE:
        '''
        This class returns the default audio device indexes for both input and output 
        '''
        p = pyaudio.PyAudio()

        default_input_index = p.get_default_input_device_info()['index']
        default_input_index = int(default_input_index)

        default_output_index = p.get_default_output_device_info()['index']
        default_output_index = int(default_output_index)
        p.terminate()

        result_dict : _DEFAULT_DEVICE_INDEXES_DICT_TYPE = {
            "INPUT": default_input_index,
            "OUTPUT": default_output_index
        }
        return result_dict
    
    @classmethod
    def get_devices_info(cls) -> t.List[t.Any]:
        '''
        Gets the information for all devices
        
        Returns:
            A list of dictionaries containing the device information, where each dictionary
            corresponds to a device and contains keys like 'name', 'index', 'maxInputChannels', etc.
        '''
        p = pyaudio.PyAudio()
        devices_info = []

        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            devices_info.append({
                'name': device_info['name'],
                'index': device_info['index'],
                'maxInputChannels': device_info['maxInputChannels'],
                'maxOutputChannels': device_info['maxOutputChannels'],
                'defaultSampleRate': device_info['defaultSampleRate']
            })

        p.terminate()
        return devices_info
