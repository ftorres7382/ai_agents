from app_code.agents.base_agent import BASE_AGENT
from app_code.Utilities.SDU import SDU
from dataclasses import dataclass

@dataclass
class secretary_agent(BASE_AGENT):
    '''
    This agent will take notes of what it hears in the audio out of the computer
    '''

    def start(self) -> None:
        '''
        This command starts the model
        '''

        print(SDU.get_devices_info())

        print("start")

