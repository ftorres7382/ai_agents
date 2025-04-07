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

class SDU:
    '''
    This class is a helper class for streaming input and output audio
    '''
    
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
