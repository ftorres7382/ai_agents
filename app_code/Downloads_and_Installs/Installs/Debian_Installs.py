import os
import subprocess
import typing as t

from .Base_Installs import Base_Installs

class Debian_Installs(Base_Installs):
    '''
    This class runs all installs neede to get a debian system up to date
    '''
    @classmethod
    def install_python(cls) -> bool:
        '''
        This function installs the correct version of python on Debian12
        '''
        print("Starting Python3.12 install...")

        print("Done")
        asdf
        


