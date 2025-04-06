import sys


def main():
    '''
    This is the function from which the other functions will be run
    '''

    check_requirements()

def check_requirements(verbose = False):
    '''
    This function checks for the correct starting requirements to start up the program
    '''
    
    _print("Checking requirements to run...", verbose=verbose)

    ###############################
    # OS MUST be Windows
    ###############################
    if sys.platform != "win32":
        print("ERROR! This program requires Windows to run.")
        return False

    ###############################
    # MUST be Python 3
    ###############################
    if sys.version_info < (3, 0):
        _print("ERROR! This program requires Python 3 or higher.", verbose)
        return False
    
    ###############################
    # MUST have ollama running with the listen port open
    # To confirm we will ping the port
    ###############################


    _print("All requirements are met!", verbose)
    return True

def _print(value, verbose = True):
    '''
    Only prints if verbose is True
    '''
    if verbose: print(value)




if __name__ == "__main__":
    main()