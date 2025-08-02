import subprocess
import os
import sys
from typing import Union, Tuple

def install_dependencies(install_command: str) -> Tuple[bool, str]:
    """
    Install dependencies using the provided installation command.
    Supports any package manager or installation method (pip, conda, apt-get, etc.)
    
    Args:
        install_command (str): The installation command (e.g., "pip install pandas", 
                                                            "conda install numpy",
                                                            "apt-get install python3-dev")
    
    Returns:
        Tuple[bool, str]: A tuple containing:
            - bool: True if installation was successful, False otherwise
            - str: Output message or error message
    """
    try:
        # Execute installation command
        process = subprocess.Popen(
            install_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Get output and error
        output, error = process.communicate()
        
        # Check if installation was successful
        if process.returncode == 0:
            return True, output
        else:
            return False, error
            
    except Exception as e:
        error_msg = f"Error during dependency installation: {str(e)}"
        return False, error_msg

def execute_python_code(file_name: str, capture_output: bool = False) -> Tuple[bool, Union[str, object]]:
    """
    Execute a Python file from the tools directory and return its output.
    
    Args:
        file_name (str): Name of the Python file to execute (must be in tools directory)
        capture_output (bool): If True, captures output; if False, allows interactive execution
    
    Returns:
        Tuple[bool, Union[str, object]]: A tuple containing:
            - bool: True if execution was successful, False otherwise
            - Union[str, object]: Output from the execution or error message
    """
    try:
        # Check if file_name is already a full path (for temp files)
        if os.path.exists(file_name):
            file_path = file_name
        else:
            # Construct full path to the Python file in tools directory
            tools_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tools')
            file_path = os.path.join(tools_dir, file_name)
        
        # Verify file exists
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            return False, error_msg
            
        if capture_output:
            # Run script and capture output
            process = subprocess.run(
                [sys.executable, "-u", file_path],  # -u for unbuffered output
                capture_output=True,
                text=True,
                shell=False
            )
            
            if process.returncode == 0:
                return True, process.stdout
            else:
                return False, process.stderr or "Script execution failed"
        else:
            # Run script with full terminal access (for interactive input)
            process = subprocess.run(
                [sys.executable, file_path],
                shell=True  # Enable terminal interaction
            )
            
            if process.returncode == 0:
                return True, "Script execution completed"
            else:
                return False, "Script execution failed"
            
    except Exception as e:
        error_msg = f"Error during code execution: {str(e)}"
        return False, error_msg
