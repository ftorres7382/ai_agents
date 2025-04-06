import sys
import typing as t

import config as C
from app_code.Utilities.OLM import OLM


def main() -> None:
    '''
    This is the function from which the other functions will be run
    '''

    passed = check_requirements()
    if not passed:
        quit()

    

def check_requirements(verbose: bool = False) -> bool:
    '''
    This function checks for the correct starting requirements to start up the program
    '''
    
    _print("Checking requirements to run...", verbose=verbose)

    ###############################
    # OS MUST be Windows
    ###############################
    if sys.platform != "win32":
        _print("ERROR! This program requires Windows to run.", verbose)
        return False

    ###############################
    # MUST be Python 3
    ###############################
    if sys.version_info < (3, 0):
        _print("ERROR! This program requires Python 3 or higher.", verbose)
        return False
    
    ###############################
    # Ollama MUST be running
    ###############################
    try:
        OLM.get_version()
    except:
        _print(f"ERROR! Was not able to get the version of ollama! Make sure ollama is running on {C.complete_ollama_api_url}", verbose=False)
    
    ###############################
    # ALL valid modes MUST be in the ollama
    ###############################
    
    
    breakpoint()

    _print("All requirements are met!", verbose)
    return True

def _print(value: t.Any, verbose: bool = True) -> None:
    '''
    Only prints if verbose is True
    '''
    if verbose: print(value)




if __name__ == "__main__":
    main()