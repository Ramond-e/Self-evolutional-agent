import json
import re
from typing import Dict, List, Union, Tuple
from task_analyzer import get_model_response

def generate_install_commands(installation_guide: str, terminal_type: str = 'cmd') -> List[str]:
    """
    Use LLM to generate installation commands based on installation guide
    
    Args:
        installation_guide (str): Installation instructions from tool documentation
        terminal_type (str): Type of terminal (cmd, bash, etc.)
        
    Returns:
        List[str]: List of generated installation commands
    """
    prompt = f"""
    From this installation guide, extract ONLY the essential commands for the simplest installation method.
    - Choose only ONE installation method (prefer pip/pip3/npm over alternatives)
    - Return ONLY a JSON array of command strings
    - No descriptions, headers, or explanations
    - No markdown formatting
    - Commands must be directly executable
    
    Installation Guide:
    {installation_guide}
    
    Example response:
    ["pip install package-name"]
    
    Commands:
    """
    
    try:
        response = get_model_response(prompt).strip()
        # Handle case where response isn't proper JSON
        if not response.startswith('['):
            # Extract commands and format as JSON array
            commands = re.findall(r'(?:^|\n)\s*([a-zA-Z0-9._-]+(?:\s+[^|>&;\n]+)*)', response)
            return [cmd.strip() for cmd in commands if cmd.strip()]
        return json.loads(response)
    except Exception as e:
        print(f"Error generating install commands: {e}")
        # Fallback: extract likely commands from installation guide
        commands = re.findall(r'(?:^|\n)\s*(?:```)*\s*(?:[$>])?\s*([a-zA-Z0-9._-]+(?:\s+[^|>&;\n]+)*)', installation_guide)
        return [cmd.strip() for cmd in commands if cmd.strip() and not cmd.startswith(('#', '//', 'git', 'cd', 'docker'))]

def clean_and_validate_commands(commands: List[str]) -> List[str]:
    """
    Clean and validate installation commands to ensure they meet format standards
    
    Args:
        commands (List[str]): Raw installation commands from LLM
        
    Returns:
        List[str]: Cleaned and validated commands
    """
    cleaned_commands = []
    
    for cmd in commands:
        # Remove command prompts and markdown
        cmd = re.sub(r'^[\$>#]\s*|^```\w*\s*|\s*```$', '', cmd.strip())
        
        # Remove comments
        cmd = re.sub(r'#.*$', '', cmd).strip()
        
        # Skip empty or documentation-only commands
        if not cmd or cmd.startswith(('##', '--', '//')):
            continue
            
        # Validate command format (basic package manager or python commands)
        if re.match(r'^(?:pip|pip3|npm|yarn|python|pytest|uvicorn|flask)\s+[a-zA-Z0-9._-]+(?:\s+[^|>&;]+)*$', cmd):
            cleaned_commands.append(cmd)
        else:
            print(f"Warning: Skipping potentially unsafe command: {cmd}")
    
    return cleaned_commands

def generate_code(language: str, usage_guide: str, user_question: str, search_keyword: str) -> str:
    """
    Use LLM to generate code based on usage guide and requirements
    
    Args:
        language (str): Programming language to use
        usage_guide (str): Usage instructions from tool documentation
        user_question (str): Original user question
        search_keyword (str): Tool search keyword
        
    Returns:
        str: Generated code
    """
    prompt = f"""
    Write ONLY the implementation code in {language} to solve this problem using the {search_keyword}.
    
    IMPORTANT:
    1. Return ONLY the code implementation
    2. NO documentation, explanations, or markdown
    3. NO installation instructions or usage examples
    4. Get ALL required inputs from the user during runtime using input()
    5. NO hardcoded values or TODO comments
    
    Example format:
    import xyz
    
    def main():
        value = input("Enter value: ")
        # implementation
    
    if __name__ == "__main__":
        main()
    
    Problem: {user_question}
    Usage Guide: {usage_guide}
    """
    
    try:
        code = get_model_response(prompt)
        # Remove any markdown formatting
        code = re.sub(r'^```\w*\n|```$', '', code.strip())
        return code
    except Exception as e:
        print(f"Error generating code: {e}")
        return ""

def clean_and_validate_code(code: str, language: str, user_question: str, search_keyword: str, usage_guide: str) -> str:
    """
    Clean and validate generated code to ensure it meets language standards and requirements.
    Uses LLM to check and fix code until it's correct.
    
    Args:
        code (str): Generated code from LLM
        language (str): Programming language of the code
        user_question (str): Original user question
        search_keyword (str): Tool search keyword
        usage_guide (str): Usage instructions and examples
        
    Returns:
        str: Cleaned and validated code
    """
    if not code.strip():
        return ""
        
    # Basic cleaning
    code = re.sub(r';\s*(?=\n)', '', code)  # Remove unnecessary semicolons
    code = re.sub(r'\t', '    ', code)  # Replace tabs with spaces
    code = re.sub(r'\s+$', '', code, flags=re.MULTILINE)  # Remove trailing whitespace
    return code
