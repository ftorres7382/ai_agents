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
import time

import config as C

# Global variable to track verbosity
verbose_build = False
python_command = None
venv_python_path = os.path.join(
    C.settings["venv_folderpath"],
    "bin/python3"    
)

def main():
    '''
    Checks for the minimum needed to create the virtual environment, install the dependencies and run the project
    '''
    print()

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
    v_print("Checking modules installed in virtual environment...")
    check_venv()
    v_print("PASSED! All required modules validated/installed!")
    v_print()
    # endregion

    # Activate the 

    # Run mypy check first
    print("Checking code with mypy...")
    command = f"{venv_python_path} -m mypy --strict app_code/main.py" #It could be run with the binś version of the mypy command, but I like it better this way, more explicit
    run_command(command, capture_output=False, return_error=True)
    print()

    
    # Run the code using the 
    print("Running app_code/main.py...")
    command = f"{venv_python_path} app_code/main.py"
    run_command(command)

    print()
    

def check_ollama():
    '''
    This function checks all ollama requirements in a few ways:
    1. Checks for ollama -v
    2. Checks for a response on 
    '''

##########################
# Python Virtual Environment Setup Functions
##########################
# region:
def check_venv():
    '''
    Will check the venv dependencies, compared to requirements.txt

    If they differ, then delete the venv directory and try to install requirements to C.settings["venv_folderpath"].
    '''   
    
    # Create the command that will do this
    commands = f"{venv_python_path} -m pip freeze"
    result = run_command(commands, verbose=True)

    # Read in the requirements
    with open(C.settings["requirements_filepath"],'r') as f:
        requirements_str = f.read()
    
    # All requirements in the file must be found in the venv
    venv_reqs_list = result.split("\n")
    
    # Remove all empty strings
    venv_reqs_list = [req for req in venv_reqs_list if req != '']

    reqs_list = requirements_str.split("\n")
    reqs_list = [req for req in reqs_list if req != '']

    # Check that all requirements are in the venv
    missing_reqs = list(set(reqs_list) - set(venv_reqs_list))
    if len(missing_reqs) == 0:
        return True
    
    print(f"\nThe python virtual environment is missing modules. Attempting to install requirements...\n")
    time.sleep(1)
    v_print(f"It is missing {len(missing_reqs)} requirements: {missing_reqs}")

    # Try to install the requirements
    command = f"{venv_python_path} -m pip install -r {C.settings['requirements_filepath']}"
    result = run_command(command, capture_output=False,return_error=True)
    if result is not None:
        print("ERROR! Was not able to install the packages automatically! Please Install the packages manually or delete the .venv folder and try again!")
        print(f"Received error: {result}")
        exit(1)

    return True
    


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
    result = run_command(command_list, verbose=False, return_error=True)

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
        result = run_command(command_list, return_error=True, verbose=False)

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
    result = run_command(commands_list, verbose=False, return_error=True)

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

def run_command(
        command: t.Union[str,t.List[str]], 
        return_error = False, 
        capture_output = True, 
        verbose = True) -> t.Union[None, str, subprocess.CalledProcessError]:
    '''
    This function tries to run the command and raises an exception if if fails
    
    If it does not fail it will return the resulting oputput as a string

    The error command will be of the format: ERROR! When running command '{command}' got error: {error}
    '''

    if not isinstance(command, str):
        command = " ".join(command)

    try:
        # Run the command using subprocess
        result = subprocess.run(command, capture_output=capture_output, text=True, check=True,shell=True, executable="/bin/bash")
        return result.stdout
    except subprocess.CalledProcessError as e:
        # Format and raise an exception with the error message
        error_message = f"ERROR! When running command '{command}' got error: {e.stderr}"
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
