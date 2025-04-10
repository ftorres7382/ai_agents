'''
Using a python file as a config because it is the easiest way to create a config file that has good documentation

Plus it is easier to edit and understand than a json or yaml file

This could have issues in the furture with safe loading
    To fix this we can strictly enforce the class structures
    possibly make objects from them safe load only what we need

ORRR make a mini program that creates the configuration and checks all the settings to make sure they are correct

'''

from app_code.literals import VALID_MODEL_NAMES

import typing as t

class SETTINGS_DICT(t.TypedDict):    
    ##########################
    # Build and Requirements Validation Settings
    ##########################
    # region:
    requirements_filepath: str
    venv_folderpath: str
    # endregion


    ##########################
    # Ollama Settings
    ##########################
    # region:
    ollama_url: str
    ollama_api_port: int
    complete_ollama_api_url: t.Union[str, None]
    # endregion


    ##########################
    # Agents Settings
    ##########################
    # region:
    # agent_object
    # endregion


settings: SETTINGS_DICT = {
    ##########################
    # Build and Requirements Validation Settings
    ##########################
    # region:
    "requirements_filepath": "./requirements.txt",
    "venv_folderpath": ".venv",
    # endregion

    ##########################
    # Ollama Settings
    ##########################
    # region:
    "ollama_url": "http://localhost",
    "ollama_api_port": 11434,

    # This will be completely filled in later
    "complete_ollama_api_url": None,
    # endregion

    ##########################
    # Agents Settings
    ##########################
    # region:
    # "agent_object": secretary_agent(
    #     name="Quinn",
    #     model_name=VALID_MODEL_NAMES.deepseek_r1_14b
    # )
    # endregion
}

# Fill in the missing values
settings['complete_ollama_api_url'] = f"{settings['ollama_url']}:{settings['ollama_api_port']}"