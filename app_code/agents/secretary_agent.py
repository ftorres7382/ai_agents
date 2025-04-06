from app_code.enums import *
from dataclasses import dataclass

@dataclass
class secretary_agent:
    '''
    This agent will take nots of what it hears in mettings and such
    '''
    model: VALID_MODELS_NAMES
    name: str

    def start(self):
        '''
        This command starts the model
        '''

