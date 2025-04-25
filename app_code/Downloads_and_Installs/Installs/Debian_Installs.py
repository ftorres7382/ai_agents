import os
import subprocess
import typing as t
import time
import shutil

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
        time.sleep(3)

        shell_content = """
            apt update -y
            apt upgrade -y
            apt install -y build-essential libssl-dev zlib1g-dev libbz2-dev \\
                libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \\
                xz-utils tk-dev libffi-dev liblzma-dev python3-openssl git
            wget https://www.python.org/ftp/python/3.12.0/Python-3.12.0.tgz
            tar -xf Python-3.12.0.tgz
            cd Python-3.12.0
            ./configure --enable-optimizations
            make -j 8
            make altinstall
        """

        # Create a directory in the temp directory to make all the files to install
        temp_dir = "./temp"
        python_install_dir = os.path.join(temp_dir, "python_install")
        if os.path.exists(python_install_dir):
            shutil.rmtree(python_install_dir)

        os.mkdir(python_install_dir)

        install_script_filepath = os.path.join(python_install_dir, "python_install.sh")

        with open(install_script_filepath, 'w') as f:
            f.write(f"cd {python_install_dir}\n")
            f.write(shell_content)
        
        result = subprocess.run(f"bash {install_script_filepath}", shell=True)
        print()
        if result.returncode != 0:
            print("Python install failed! Please install python3.12 manually...")
            exit(1)
        else:
            print("Successfully installed python3.12!")

        


