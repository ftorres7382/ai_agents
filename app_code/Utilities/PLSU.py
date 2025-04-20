import subprocess
import typing as t
import re

# Literal type Definitions
VALID_PULSE_AUDIO_VALUES = t.Literal[
    "sinks",
    "sources",
]
VALID_PULSE_AUDIO_VALUES_LIST = t.get_args(VALID_PULSE_AUDIO_VALUES)

SAMPLE_SPEC_DICT_TYPE = t.TypedDict("SAMPLE_SPEC_DICT_TYPE", {
    "data_format": str,
    "channels": int,
    "sample_rate": int
})
SAMPLE_SPEC_DICT_TYPE_KEYS_LIST = list(SAMPLE_SPEC_DICT_TYPE.__annotations__.keys())

SHORT_INFO_DICT_TYPE = t.TypedDict("SHORT_INFO_DICT_TYPE", {
    "id": int,
    "name": str,
    "driver": str,
    "sample_specs": SAMPLE_SPEC_DICT_TYPE,
    "state": str
})

SHORT_INFO_DICT_TYPE_KEYS_LIST = list(SHORT_INFO_DICT_TYPE.__annotations__.keys())
 


class PLSU:
    '''
    The purpose of this class us to handle any operations that involve pulse audio
    '''
    # TODO:
    # Add get_devices info
    # Add get_sinks_info
    # Add get_sources_info?


    @classmethod
    def get_pulse_name(cls, sd_name: str, pulse_audio_type: VALID_PULSE_AUDIO_VALUES) -> str:
        '''
        This class translates the sd name to the pulse audio name
        
        Only the default is currently implemented
        '''
        if sd_name != "default":
            raise NotImplementedError("ERROR! Non Default names have not been implemented yet!")
        #                                           Set the firs char to uppercase, remove the 's' at the end of the name
        command = "pactl info | grep "+ f'"Default {pulse_audio_type[0].upper() + pulse_audio_type[1:-1]}"'

        result = subprocess.run(command, capture_output=True, shell=True, text=True)
        
        result_str: str = str(result.stdout).replace("\n", "")
        
        final_result = result_str.split(": ")[-1]
        
        
        return final_result

    @classmethod
    def get_pulse_loopback_ids_by_sink_name(cls, loopback_name:str) -> t.List[int]:
        '''
        Returns a list of ids using 'pactl list modules short | grep {pulse_name}' and parsing the output
        '''
        command = f"pactl list modules short | grep {loopback_name}"
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        result_list = result.stdout.split("\n")
        result_list = [item for item in result_list if item != ""]

        ids_list = [int(item.split("\t")[0]) for item in result_list]
        return ids_list

    @classmethod
    def get_short_info(cls, audio_type: VALID_PULSE_AUDIO_VALUES) -> t.List[SHORT_INFO_DICT_TYPE]:
        '''
        Uses pactl list sources short to return the information on the sources
        '''
        if audio_type not in VALID_PULSE_AUDIO_VALUES_LIST:
            raise ValueError(f"ERROR! 'audio_type' can only be on of the values '{VALID_PULSE_AUDIO_VALUES_LIST}'. Received: {audio_type}") 
        command = f"pactl list {audio_type} short"
        result = subprocess.run(command, capture_output=True, text=True, shell=True).stdout
        lines = result.split("\n")
        lines = [line for line in lines if line != ""]

        header_keys = SHORT_INFO_DICT_TYPE_KEYS_LIST
        return_result: t.List[SHORT_INFO_DICT_TYPE] = []
        for line in lines:
            values = line.split("\t")
            append_dict = {}
            for i, value in enumerate(values):
                save_value: t.Union[str,int, SAMPLE_SPEC_DICT_TYPE]
                key_name = header_keys[i]
                
                if key_name == "sample_specs":
                    # Split the sample specs values
                    sample_specs_values = value.split(" ")
                    sample_specs_values = [item for item in sample_specs_values if item != ""]

                    sample_specs_header = SAMPLE_SPEC_DICT_TYPE_KEYS_LIST
                    sample_specs_dict: dict[t.Any, t.Any] = {}
                    
                    for i, sample_value in enumerate(sample_specs_values):
                        save_sample_value: t.Union[str, int]
                        sample_key = sample_specs_header[i]
                        # Data cleanup
                        if sample_key == "channels":
                            sample_value = sample_value.replace("ch", "")
                            save_sample_value = int(sample_value)
                        elif sample_key == "sample_rate":
                            sample_value = sample_value.replace("Hz", "")
                            save_sample_value = int(sample_value)    
                        else:
                            save_sample_value = sample_value

                        sample_specs_dict[sample_key] = save_sample_value
                    save_value = t.cast(SAMPLE_SPEC_DICT_TYPE, sample_specs_dict)
                elif key_name == "id":
                    save_value = int(value)
                else: 
                    save_value = value
                append_dict[key_name] = save_value
            final_append_dict = t.cast(SHORT_INFO_DICT_TYPE, append_dict)
            return_result.append(final_append_dict)
        
        return return_result
        




    @classmethod
    def delete_pulse_loopbacks(cls, loopback_name:str) -> None:
        '''
        Deletes any pulse loopback with the defined name
        '''
        # Get the information about the pulse
        pulse_ids = cls.get_pulse_loopback_ids_by_sink_name(loopback_name=loopback_name)
        for pulse_id in pulse_ids:
            command = f"pactl unload-module {pulse_id}"
            subprocess.run(command, shell=True)
        

    @classmethod
    def overwrite_combined_pulse_loopback(cls, input_pulse_name: str, output_pulse_name: str, loopback_name: str) -> None:
        '''
        This method overwrites whatever the current pulse config is with the one sent to it
        If the pulse config already exists, it will delete it by finding its id using 'pactl list sinks short' and the loopback_name 
        Once the ID is found, it will delete it using pactl 'unload-module {id}'

        The loopback sink created will combine INPUT and OUTPUT in a fashion similar to
        ----------------
        # Create a null sink
        pactl load-module module-null-sink sink_name=combineSink

        # Route mic to combineSink
        pactl load-module module-loopback source=<mic_source> sink=combineSink

        # Route monitor of speaker to combineSink
        pactl load-module module-loopback source=<speaker_monitor_source> sink=combineSink
        ----------------
        '''
        pulse_audio_type:VALID_PULSE_AUDIO_VALUES = "sinks"
        cls.delete_pulse_loopbacks(loopback_name=loopback_name)
        

        # Create the new module        
        create_null_sink_command = f"pactl load-module module-null-sink sink_name={loopback_name} sink_properties=device.description=SilentSink"
        subprocess.run(create_null_sink_command, capture_output=True, shell=True)
        
        # Add output monitor        
        command = f"pactl load-module module-loopback source={output_pulse_name}.monitor sink={loopback_name}"
        subprocess.run(command, capture_output=True, shell=True)

        # Add input monitor
        command = f"pactl load-module module-loopback source={input_pulse_name} sink={loopback_name}"
        subprocess.run(command, capture_output=True, shell=True)

    @classmethod
    def listen_echo(cls, loopback_name: str, output_pulse_name: t.Union[str, None] = None, interactive:bool = False) -> None:
        '''
        This function starts up an echo of the loopack to the output device specified

        If interactive is turned on, it will display a menu to control which device the loopback will go through
        '''
        if not interactive:
            raise NotImplementedError("ERROR! The non interactive code has not been completed!")
        else:
            raise NotImplementedError("ERROR! The interactive code has not been completed!")


    




    '''
    Keeping this code in case I need it later

    get_loopback_short_info_ERRORS = t.Literal[
        "",
        "Not Found",
        "Multiple Found"
    ]

    # Typed Dictionary Definitions 
    class SAMPLE_SPEC_DICT_TYPE(t.TypedDict):
        sample_type: str
        channels: int
        sample_rate: int


    class LOOPBACK_INFO_DICT_TYPE(t.TypedDict):
        pulse_type: VALID_PULSE_AUDIO_VALUES
        id: str
        pulse_name: str
        driver: str
        sample_spec: SAMPLE_SPEC_DICT_TYPE
        status: str



    @classmethod
    def get_loopback_short_info_list(cls, 
                                loopback_name: str, 
                                pulse_audio_type: VALID_PULSE_AUDIO_VALUES, 
                                regex: bool=False, 
                                ) -> t.List[LOOPBACK_INFO_DICT_TYPE]:
        \'''
        Returns a dictionary with the pulse loopback information
        \'''
        def parse_sample_format(fmt_string:str) -> SAMPLE_SPEC_DICT_TYPE:
            parts = fmt_string.split()
            if len(parts) != 3:
                raise ValueError("Unexpected format: " + fmt_string)
            
            sample_type = parts[0]
            
            # Extract numeric channel count
            channels = int(parts[1].replace("ch", ""))
            
            # Extract numeric sample rate
            sample_rate = int(parts[2].replace("Hz", ""))
            
            return {
                "sample_type": sample_type,
                "channels": channels,
                "sample_rate": sample_rate
            }
    
        command = f'pactl list {pulse_audio_type} short'
        result = subprocess.run(command, capture_output=True, text=True, shell=True)
        results_list = result.stdout.split("\n")
        results_list = [item for item in results_list if item != ""]
        
        info_results: t.List[LOOPBACK_INFO_DICT_TYPE] = []
        for line in results_list:
            parts = line.split('\t')
            loopback_info: LOOPBACK_INFO_DICT_TYPE = {
                'pulse_type': pulse_audio_type,
                'id': parts[0],
                'pulse_name': parts[1],
                'driver': parts[2],
                'sample_spec': parse_sample_format(parts[3]),
                'status': parts[4]
            }
            if regex:
                if re.search(loopback_name, loopback_info['pulse_name']):
                    info_results.append(loopback_info.copy())
            else: 
                if loopback_info['pulse_name'] == loopback_name:
                    info_results.append(loopback_info.copy())

        
        return info_results
    '''



