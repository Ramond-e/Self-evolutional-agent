import os
from typing import Dict, Union
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

# OpenRouter API configuration
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY environment variable is not set. Please add it to your .env file.")
OPENROUTER_API_BASE_URL = os.getenv('OPENROUTER_API_BASE_URL')

def get_model_response(prompt: str) -> str:
    """
    Helper function to get response from Claude Sonnet model via OpenRouter API
    """
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": "anthropic/claude-sonnet-4",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    response = requests.post(OPENROUTER_API_BASE_URL, json=payload, headers=headers)
    
    try:
        response_json = response.json()
        if response.status_code == 200:
            return response_json['choices'][0]['message']['content']
        else:
            error_msg = response_json.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"API request failed with status code {response.status_code}: {error_msg}\nResponse: {response_json}")
    except json.JSONDecodeError:
        raise Exception(f"Failed to decode API response. Status code: {response.status_code}, Response text: {response.text}")

def analyze_task(task: str) -> Dict[str, Union[list, str]]:
    """
    Analyzes a task and returns the steps needed to solve it along with any required tools.
    
    Args:
        task (str): The task description to analyze
        
    Returns:
        Dict with:
            steps: List of steps to solve the task
            required_tool: Tool name or "no_extra_tools_needed"
            tool_general_description: General description of what the tool should do (for generic tool creation)
    """
    prompt = f"""
    Analyze the following task and return a JSON object with three fields:
    1. "steps": An array of strings describing the steps needed to solve the task
    2. "required_tool": A string containing either a single tool name that would be helpful for searching (e.g. "youtube transcript", "stock price free") or "no_extra_tools_needed" if no external tool is required
    3. "tool_general_description": A general description of what the tool should do, focusing on universal functionality rather than the specific query. This should describe the tool's general purpose.
    
    The JSON must:
    - Use double quotes for all strings and property names
    - Have proper commas between elements
    - Have no trailing commas
    - Have no comments or additional text
    
    Example 1:
    For task "In the YouTube 360 VR video from March 2018 narrated by the voice actor of Lord of the Rings' Gollum, what number was mentioned by the narrator directly after dinosaurs were first shown in the video?", return:
    {{
        "steps": [
            "Extract subtitles from the YouTube video",
            "Analyze subtitles to find when dinosaurs are first mentioned",
            "Identify the number mentioned immediately after"
        ],
        "required_tool": "youtube transcript",
        "tool_general_description": "A tool that can extract and retrieve transcripts/subtitles from any YouTube video by URL or video ID"
    }}
    
    Example 2:
    For task "What is the latest stock price of NVIDIA (NVDA)?", return:
    {{
        "steps": [
            "Fetch current stock price data for NVIDIA (NVDA)",
            "Extract and return the latest price"
        ],
        "required_tool": "stock price api free",
        "tool_general_description": "A tool that fetches real-time stock price data for any given stock ticker symbol"
    }}
    
    Example 3:
    For task "什么是大模型", return:
    {{
        "steps": [
            "Access knowledge base for information about large language models",
            "Formulate comprehensive explanation"
        ],
        "required_tool": "no_extra_tools_needed",
        "tool_general_description": "no_extra_tools_needed"
    }}
    
    Now analyze this task and return a properly formatted JSON object:
    Task: {task}
    """
    
    response = get_model_response(prompt)
    return json.loads(response)
