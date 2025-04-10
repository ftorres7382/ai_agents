'''
The purpose of this code is to check minimum requirements, 
set up the basic environment and install all the python dependencies for the project.

It should ONLY use the standard python libraries

'''

import platform
import sys
import argparse
import subprocess
import os
import typing as t

import config as C

# Global variable to track verbosity
verbose_build = False
python_command = None

def main():
    '''
    Checks for the minimum needed to create the virtual environment, install the dependencies and run the project
    '''

    ##########################
    # System level checks
    ##########################
    # region:


    # Must be Linux OS
    v_print("Checking that the OS is Linux...")
    check_os()
    v_print("PASSED! Operating System is Linux!")
    v_print()

    # Must have the bash installed
    v_print("Checking that bash is available for use...")
    check_bash()
    v_print("PASSED! bash is available for use")
    v_print()

    # Must have python 3.12
    v_print("Checking that Python 3.12 is available for use...")
    check_python()
    v_print("PASSED! Python 3.12 IS available for use")
    v_print()

    # Python has to have the venv module installed
    v_print(f"Checking that '{python_command}' has the venv module installed...")
    check_venv_module()
    v_print(f"PASSED! '{python_command}' HAS the venv module installed")
    v_print()


    # endregion


    ##########################
    # Python Virtual Environment Setup
    ##########################
    # region:
    # Create empty venv folder if it does not exist
    v_print(f"Checking '{C.settings['venv_folderpath']}' folder exists...")
    make_initial_venv_folder()    
    v_print()

    # Check all the requirements for venv
    print("Checking venv installed modules...")
    check_venv()
    v_print()

    # endregion

##########################
# Python Virtual Environment Setup Functions
##########################
# region:
def check_venv():
    '''
    Will check the venv dependencies, compared to requirements.txt

    If they differ, then delete the venv directory and try to install requirements to C.settings["venv_folderpath"].
    '''
    
    pass


def make_initial_venv_folder():
    '''
    Creates the .venv folder if it doesn't exist
    '''

    if not os.path.exists(C.settings["venv_folderpath"]):
        print(f"Creating virtual environment folder at {C.settings["venv_folderpath"]}...")
        subprocess.run([python_command, "-m","venv", C.settings["venv_folderpath"]])
    else:
        v_print(f"Virtual environment folder already exists at '{C.settings["venv_folderpath"]}'.")

# endregion


##########################
# System level checks
##########################
# region: 
def check_os():
    '''
    Checks if the OS is a linux distribution
    If not, it will print an ERROR! and exit the program
    '''
    if platform.system().lower() != "linux":
        print("ERROR! This script can only be run on a Linux distribution.")
        sys.exit(1)

def check_bash():
    '''
    This function makes sure that bash is installed
    '''

    # Try to get the bash version
    command_list = ["bash", "--version"]
    result = run_command_list(command_list, verbose=False, return_error=True)

    if not isinstance(result, str):
        print("ERROR! bash MUST be installed!")
        exit(1)


    # bash should be present in the first line
    first_line = result.split("\n")[0]
    if "bash" not in first_line:
        print(f"ERROR! The command '{' '.join(command_list)}' did not give an error \
              but does not contain 'bash' in its first line. Instead it received: {result}")
        exit(1)
    
def check_python():
    '''
    Uses subprocess to check if the python3.12 command is available.
    If not, it will check if python3 is available and then check if the version is 3.12.
    Else, it will print an ERROR! and exit the program.

    v_prints will be used to print the messages along the way.
    '''
    global python_command

    def check_python_command():
        '''
        This function will check the requriements given the current global python command
        '''
        v_print(f"Checking for {python_command} CLI command...")

        command_list = [python_command, '--version']
        result = run_command_list(command_list, return_error=True, verbose=False)

        if not isinstance(result, str):
            v_print(f"{python_command} is not installed...")
            return False


        # The command ran successfully, but check that it is python 3.12
        if 'Python 3.12' in result:
            v_print(f"Python 3.12 found using '{' '.join(command_list)}' command.")
            return True
        else:
            v_print(f"{python_command} does not point to a Python 3.12 version")
            return False

    python_command = "python3.12"
    if check_python_command(): 
        return True
    
    python_command = "python3"
    if check_python_command():
        return True

    # Python 3.12 is not available, print error and exit
    print("ERROR! Neither python3.12 or python3 (pointing to a python3.12 version) commands are available. Please install Python 3.12!")
    sys.exit(1)

def check_venv_module():
    '''
    This function checks if the venv module is installed in the python we found 
    '''
    commands_list = [python_command, "-m", "venv", "--help"]
    result = run_command_list(commands_list, verbose=False, return_error=True)

    if not isinstance(result, str):
        print(f"ERROR! '{python_command}' MUST have the venv module installed!")

    first_line = result.split("\n")[0]
    if "venv" not in first_line:
        print(f"ERROR! The command '{' '.join(commands_list)}' \
              does not have venv in the first line. Instead received: {result}")
    
# endregion    


##########################
# Misc functions not used in main
########################## 
# region:
def setup_arguments():
    '''
    Sets up argument parsing for --verbose and --help
    '''
    global verbose_build
    parser = argparse.ArgumentParser(description="Setup environment for the project.")
    parser.add_argument('--verbose_build', action='store_true', help="Enable verbose output when building.")
    args = parser.parse_args()
    
    verbose_build = args.verbose_build

def v_print(message="", verbose = None):
    '''
    Override the print function to handle verbose output.
    '''
    if verbose is None:
        verbose = verbose_build

    if verbose:
        print(message)

def run_command_list(command_list, return_error = False, verbose = True) -> t.Union[str, subprocess.CalledProcessError]:
    '''
    This function tries to run the command and raises an exception if if fails
    
    If it does not fail it will return the resulting oputput as a string

    The error command will be of the format: ERROR! When running command '{command}' got error: {error}
    '''
    try:
        # Run the command using subprocess
        result = subprocess.run(command_list, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Format and raise an exception with the error message
        error_message = f"ERROR! When running command '{' '.join(command_list)}' got error: {e.stderr}"
        v_print(error_message, verbose)
        if return_error:
            return e
        exit(1)

# endregion 


if __name__ == "__main__":

    setup_arguments()
    
    v_print("-"*30)
    v_print("Building the environment before running the project...\n")

    main()

    v_print("Environment built successfully!")
    v_print("-"*30)
    v_print("Running the project...")
    # Placeholder for running the project
    # run_project()
