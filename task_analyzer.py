import os
from typing import Dict, Union
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# API KEY 选择逻辑 (OpenRouter优先，如果都没填则报错)
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENROUTER_API_BASE_URL = os.getenv('OPENROUTER_API_BASE_URL')
OPENAI_API_BASE_URL = os.getenv('OPENAI_API_BASE_URL')

if OPENROUTER_API_KEY:
    USE_API = 'openrouter'
    API_KEY = OPENROUTER_API_KEY
elif OPENAI_API_KEY:
    USE_API = 'openai'
    API_KEY = OPENAI_API_KEY
else:
    raise ValueError("Neither OPENROUTER_API_KEY nor OPENAI_API_KEY is set. Please add one of them to your .env file.")

def get_model_response(prompt: str) -> str:
    """
    Helper function to get response from LLM via OpenRouter API (优先) 或 OpenAI API
    """
    if USE_API == 'openrouter':
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "anthropic/claude-sonnet-4",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(OPENROUTER_API_BASE_URL, json=payload, headers=headers)
    elif USE_API == 'openai':
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(OPENAI_API_BASE_URL, json=payload, headers=headers)
    else:
        raise Exception("No valid API key found for either OpenRouter or OpenAI.")

    try:
        response_json = response.json()
        if response.status_code == 200:
            return response_json['choices'][0]['message']['content']
        else:
            error_msg = response_json.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"API request failed with status code {response.status_code}: {error_msg}\nResponse: {response_json}")
    except json.JSONDecodeError:
        raise Exception(f"Failed to decode API response. Status code: {response.status_code}, Response text: {response.text}")

def analyze_task(task: str) -> Dict[str, Union[list, str, bool]]:
    """
    Analyzes a task and returns the steps needed to solve it along with any required tools.
    
    Args:
        task (str): The task description to analyze
        
    Returns:
        Dict with:
            needs_external_tool: Boolean indicating if external tools are needed
            steps: List of steps to solve the task
            required_tool: Tool name or "no_extra_tools_needed"
            tool_general_description: General description of what the tool should do (for generic tool creation)
    """
    prompt = f"""
    Analyze the following task and determine if it requires external tools or APIs.
    
    CRITICAL: First determine if this task needs external tools:
    - Tasks that ask about real-time data (weather, stock prices, news, etc.) need external tools
    - Tasks that ask about general knowledge, explanations, or advice DO NOT need external tools
    - Simple questions, greetings, or conversations DO NOT need external tools
    - Mathematical calculations, text processing, or code generation usually DO NOT need external tools
    
    Return a JSON object with these fields:
    1. "needs_external_tool": true/false - Whether ANY external tool/API is needed
    2. "steps": An array of step objects (ONLY if needs_external_tool is true), each containing:
       - "description": What needs to be done in this step
       - "requires_tool": true/false - whether this step needs an external tool
       - "tool_type": The type of tool needed (e.g. "weather api", "stock api", "no_tool") for this specific step
    3. "main_required_tool": The primary tool needed (or "no_extra_tools_needed" if none needed)
    4. "tool_general_description": A general description of what the main tool should do (empty string if no tool needed)
    
    If needs_external_tool is false, steps should be an empty array.
    
    The JSON must:
    - Use double quotes for all strings and property names
    - Have proper commas between elements
    - Have no trailing commas
    - Have no comments or additional text
    
    Examples:
    
    1. For task "What's the weather like in Tokyo?", return:
    {{
        "needs_external_tool": true,
        "steps": [
            {{
                "description": "Get current weather data for Tokyo",
                "requires_tool": true,
                "tool_type": "weather api"
            }},
            {{
                "description": "Summarize the weather information and present to user",
                "requires_tool": false,
                "tool_type": "no_tool"
            }}
        ],
        "main_required_tool": "weather api",
        "tool_general_description": "A tool that fetches current weather data for any location"
    }}
    
    2. For task "What is machine learning?", return:
    {{
        "needs_external_tool": false,
        "steps": [],
        "main_required_tool": "no_extra_tools_needed",
        "tool_general_description": ""
    }}
    
    3. For task "Hello, how are you?", return:
    {{
        "needs_external_tool": false,
        "steps": [],
        "main_required_tool": "no_extra_tools_needed",
        "tool_general_description": ""
    }}
    
    4. For task "What is the latest stock price of NVIDIA (NVDA)?", return:
    {{
        "needs_external_tool": true,
        "steps": [
            {{
                "description": "Fetch current stock price data for NVIDIA (NVDA)",
                "requires_tool": true,
                "tool_type": "stock price api"
            }},
            {{
                "description": "Format and present the stock price to user",
                "requires_tool": false,
                "tool_type": "no_tool"
            }}
        ],
        "main_required_tool": "stock price api free",
        "tool_general_description": "A tool that fetches real-time stock price data for any given stock ticker symbol"
    }}
    
    Now analyze this task and return a properly formatted JSON object:
    Task: {task}
    """
    
    response = get_model_response(prompt)
    return json.loads(response)
