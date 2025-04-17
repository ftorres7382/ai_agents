import typing as t
import platform
import os

from .Base_Installs import Base_Installs
from .Debian_Installs import Debian_Installs

##########################
# Type definitions
##########################
# region:
SUPPORTED_OS_PRETTY_NAMES_TYPE: t.TypeAlias = t.Literal[
    # Uses the pretty names from platform.freedesktop_os_release()
    "Debian GNU/Linux 12 (bookworm)",
    # "Linux Mint 22" # Needs to be tested at a later date!!!!!!!!!!!!!!!!!!!!!!!!!!!!
]


INSTALL_CLASS_MAPPING_DICT_TYPE = t.TypedDict(
    "INSTALL_CLASS_MAPPING_DICT_TYPE",{
        "Debian GNU/Linux 12 (bookworm)": t.Type[Debian_Installs]
    }
)
# endregion


class Installs_Manager(Base_Installs):
    '''
    This class handles all installs using the child classes and their methods
    '''
    INSTALL_CLASS_MAPPING: INSTALL_CLASS_MAPPING_DICT_TYPE = {
        "Debian GNU/Linux 12 (bookworm)": Debian_Installs
    }
    SUPPORTED_OS_PRETTY_NAME_LIST = list(INSTALL_CLASS_MAPPING.keys())
    @classmethod
    def running_as_root(cls) -> bool:
        '''
        This function returns whether the current program is being run as root
        '''
        return os.geteuid() == 0
    
    @classmethod
    def check_root(cls) -> None:
        '''
        Raises and error if the program is not running as root
        '''
        if not cls.running_as_root():
            print("ERROR! The program needs to be run with sudo priviliges!")
            print("Run as root or with 'sudo python3 run.py'")
            quit(1)


    @classmethod 
    def get_os_pretty_name(cls):
        '''
        Returns the pretty name from platform.freedesktop_os_release()
        '''
        return platform.freedesktop_os_release()["PRETTY_NAME"]
    
    @classmethod
    def supported_os(cls) -> bool:
        '''
        Returns whether or not the current os is supported
        '''
        return cls.get_os_pretty_name() in cls.SUPPORTED_OS_PRETTY_NAME_LIST


    @classmethod
    def check_os(cls):
        '''
        Raises an error if the OS is not supported
        '''
        os_pretty_name = cls.get_os_pretty_name() 
        if os_pretty_name not in cls.SUPPORTED_OS_PRETTY_NAME_LIST:
            raise Exception(f"ERROR! '{os_pretty_name}' is not supported!") 


    @classmethod
    def get_install_class(cls, os_pretty_name = None):
        '''
        Returns the appropriate install class based on the class mapping
        '''
        if os_pretty_name is None:
            os_pretty_name = cls.get_os_pretty_name()
        
        
        allowed_values = t.get_args(SUPPORTED_OS_PRETTY_NAMES_TYPE)
        if os_pretty_name not in allowed_values:
            raise ValueError(f"ERROR! Only '{allowed_values}' are allowed! Received: {os_pretty_name}")
        
        return cls.INSTALL_CLASS_MAPPING[os_pretty_name]
    
    @classmethod
    def install_python(cls) -> None:
        '''
        This method does all required checks and calls the correct install python method
        '''
        cls.check_os()
        cls.check_root()

        # Run the install
        cls.get_install_class().install_python()

