from abc import ABC, abstractmethod
import typing as t


class base_agent(ABC):
    '''
    This class defines the minimum amount of information needed to create an agent
    An agent needs a name and a model name

    Other agent classes will inherit this class 
    '''

    def __init__(self, name:str, verbose: bool = True):
        self.name = name
        self.verbose = verbose


    def print(self, value: t.Any) -> None:
        if self.verbose:
            print(value)

    @abstractmethod
    def start(self) -> None:
        '''
        This is a function all child classes should implement

        It should start the AI agent
        '''
        pass
