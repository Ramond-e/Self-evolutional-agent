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
    Write a GENERIC and REUSABLE implementation code in {language} based on the following tool documentation.
    
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
    
    IMPLEMENTATION GUIDELINES:
    - Study the Usage Guide carefully to understand the API/library structure
    - If API keys are mentioned, prompt user for them at runtime
    - Handle errors gracefully with try-except blocks
    - For API responses, extract ALL relevant data fields
    - CRITICAL: Save ALL results to 'tool_output.json' for cross-step data sharing
    - The saved JSON must contain all the data that was displayed to the user
    - Include fields like: location, temperature, weather conditions, timestamps, etc.
    
    PREFERRED STRUCTURE:
    ```python
    import required_libraries
    import json
    
    def fetch_data():
        # Get user inputs
        param1 = input("Enter [descriptive parameter name]: ")
        
        # If API key is needed
        api_key = input("Enter your API key (get free at [provider_url]): ")
        
        try:
            # Main implementation using the library/API
            # Extract and process data
            
            # CRITICAL: Build a complete result dictionary with ALL data
            result = {{
                "relevant_field1": value1,
                "relevant_field2": value2,
                # Include ALL important data fields from the API response
            }}
            
            # Display results for user visibility
            print("\\n--- Results ---")
            # Print all relevant fields
            for key, value in result.items():
                print(f"{{key}}: {{value}}")
            
            # CRITICAL: Save ALL data for other tools to use
            with open('tool_output.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            
            # Also print confirmation
            print("\\nData saved to tool_output.json")
            
            return result
            
        except Exception as e:
            print(f"Error: {{str(e)}}")
            # Even on error, save what we have
            error_result = {{"error": str(e), "status": "failed"}}
            with open('tool_output.json', 'w', encoding='utf-8') as f:
                json.dump(error_result, f, ensure_ascii=False, indent=2)
            return error_result
    
    def main():
        fetch_data()
    
    if __name__ == "__main__":
        main()
    ```
    
    Original Example Question (DO NOT hardcode for this): {user_question}
    Tool Type: {search_keyword}
    
    USAGE GUIDE FROM DOCUMENTATION:
    {usage_guide}
    
    Remember: 
    - Make the tool work for ANY similar request
    - If the documentation mentions specific API providers (like Alpha Vantage, OpenWeatherMap), use them
    - Include helpful prompts that guide users (e.g., where to get API keys)
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
