from abc import ABC, abstractmethod


class Base_Installs(ABC):
    '''
    This class defines all the functions that need to be implemented by the other classes
    As well as functions that would also be used by the other classes
    '''

    @classmethod
    @abstractmethod
    def install_python(cls):
        '''
        All classes must implement this method
        '''
        pass