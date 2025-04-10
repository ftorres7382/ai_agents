from abc import ABC, abstractmethod

from dataclasses import dataclass
from app_code.literals import VALID_MODEL_NAMES
@dataclass
class BASE_AGENT(ABC):
    '''
    This class defines the minimum amount of information needed to create an agent
    An agent needs a name and a model name

    Other agent classes will inherit this class 
    '''
    name: str
    model_name: VALID_MODEL_NAMES

    @abstractmethod
    def start(self) -> None:
        '''
        This is a function all child classes should implement

        It should start the AI agent
        '''
        pass
