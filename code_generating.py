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

def generate_code(language: str, usage_guide: str, user_question: str, search_keyword: str, tool_general_description: str) -> str:
    """
    Use LLM to generate code based on usage guide and requirements
    
    Args:
        language (str): Programming language to use
        usage_guide (str): Usage instructions from tool documentation
        user_question (str): Original user question
        search_keyword (str): Tool search keyword
        tool_general_description (str): General description of what the tool should do
        
    Returns:
        str: Generated code
    """
    prompt = f"""
    Write a GENERIC and REUSABLE implementation code in {language} based on the following tool description and usage guide.
    
    Tool General Purpose: {tool_general_description}
    
    CRITICAL REQUIREMENTS:
    1. Create a UNIVERSAL tool that can handle ANY input, not just the specific example
    2. Make the tool REUSABLE for different scenarios
    3. Get ALL required inputs from the user during runtime using input()
    4. NO hardcoded values specific to the example question
    5. Return ONLY the code implementation
    6. NO documentation, explanations, or markdown
    7. Make the tool flexible enough to handle various use cases
    8. IMPORTANT: The tool should both PRINT results AND RETURN them as a dictionary or structured format
    
    Example format:
    import xyz
    
    def get_data():
        # Get generic inputs that work for any use case
        param1 = input("Enter [generic parameter name]: ")
        param2 = input("Enter [another generic parameter]: ")
        
        # implementation that works for ANY input
        result = {{"key": "value", "data": "..."}}
        
        # Print for user visibility
        print("Result:", result)
        
        # Return for programmatic access
        return result
    
    def main():
        result = get_data()
        # Save result for other tools to access
        import json
        with open('tool_output.json', 'w') as f:
            json.dump(result, f)
    
    if __name__ == "__main__":
        main()
    
    Original Example Question (DO NOT hardcode for this): {user_question}
    Tool Type: {search_keyword}
    Usage Guide: {usage_guide}
    
    Remember: The code should work for ANY similar request, not just this specific example!
    """
    
    try:
        code = get_model_response(prompt)
        # Remove any markdown formatting
        code = re.sub(r'^```\w*\n|```$', '', code.strip())
        return code
    except Exception as e:
        print(f"Error generating code: {e}")
        return ""

def clean_and_validate_code(code: str, language: str, user_question: str, search_keyword: str, usage_guide: str, tool_general_description: str) -> str:
    """
    Clean and validate generated code to ensure it meets language standards and requirements.
    Uses LLM to check and fix code until it's correct.
    
    Args:
        code (str): Generated code from LLM
        language (str): Programming language of the code
        user_question (str): Original user question
        search_keyword (str): Tool search keyword
        usage_guide (str): Usage instructions and examples
        tool_general_description (str): General description of what the tool should do
        
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
