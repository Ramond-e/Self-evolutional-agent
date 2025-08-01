import os
from typing import Optional, List
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from task_analyzer import get_model_response
import re
from tqdm import tqdm

# Global model instance for reuse
_model = None

def _load_model(desc: str = "Loading sentence-transformers model") -> SentenceTransformer:
    """
    Load the sentence-transformers model with progress display.
    """
    global _model
    if _model is None:
        print(f"\n{desc}...")
        with tqdm(total=100, desc="Progress", ncols=100) as pbar:
            # Model loading typically happens in 4 main steps
            _model = SentenceTransformer('all-MiniLM-L6-v2')
            pbar.update(100)  # Complete the progress bar
    return _model

def generate_code_description(user_question: str, required_tool: str, code: str, tool_name: str) -> str:
    """
    Generate a one-sentence description of the code's functionality using LLM.
    
    Args:
        user_question (str): The original user question
        required_tool (str): The required tool identified by task analyzer
        code (str): The generated code
        tool_name (str): Name of the tool
        
    Returns:
        str: A description in format "sanitized_tool_name: one-sentence description"
    """
    prompt = f"""
    Given a tool's code and context, generate a SINGLE SENTENCE description (max 100 characters) that captures its core functionality.
    The description should be clear, concise, and focus on what the tool does.
    
    Context:
    - User Question: {user_question}
    - Required Tool: {required_tool}
    - Code: {code}
    
    Format your response EXACTLY as:
    {sanitize_tool_name(tool_name)}: [your one-sentence description]
    
    Example formats:
    youtube_search: Searches YouTube videos using specified keywords and filters
    stock_price_checker: Fetches real-time stock prices from financial APIs
    weather_api: Retrieves current weather conditions for a given location
    """
    
    description = get_model_response(prompt)
    
    # Ensure format compliance
    if ':' not in description:
        description = f"{sanitize_tool_name(tool_name)}: {description}"
    
    return description

def sanitize_tool_name(tool_name: str) -> str:
    """
    Convert tool name to a valid filename by removing special characters
    and replacing spaces with underscores.
    """
    # Remove special characters and replace spaces with underscores
    sanitized = re.sub(r'[^\w\s-]', '', tool_name)
    sanitized = re.sub(r'[-\s]+', '_', sanitized).strip('-_')
    return sanitized.lower()

def save_tool_code(description: str, code: str, tool_name: str) -> str:
    """
    Save the code with its description as a comment to the tools directory.
    
    Args:
        description (str): The code's functionality description
        code (str): The actual code
        tool_name (str): Name of the tool
        
    Returns:
        str: The sanitized tool name used for the file
    """
    # Create tools directory if it doesn't exist
    if not os.path.exists('tools'):
        os.makedirs('tools')
    
    # Sanitize tool name for filename
    safe_name = sanitize_tool_name(tool_name)
    
    # Format the code with description as comment
    formatted_code = f'''"""
{description}
Tool Name: {tool_name}
"""

{code}'''
    
    # Save to file
    filename = f'tools/{safe_name}.py'
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(formatted_code)
    
    return safe_name

def vectorize_description(description: str, tool_name: str) -> None:
    """
    Vectorize the description using sentence-transformers and save to vectorized_tools.
    
    Args:
        description (str): The code's functionality description
        tool_name (str): Name of the tool
    """
    # Create vectorized_tools directory if it doesn't exist
    if not os.path.exists('vectorized_tools'):
        os.makedirs('vectorized_tools')
    
    # Load model with progress display
    model = _load_model("Loading model for vectorization")
    
    # Generate embedding with progress display
    print("Generating embedding...")
    with tqdm(total=100, desc="Progress", ncols=100) as pbar:
        embedding = model.encode([description])[0]
        pbar.update(100)
    
    # Save embedding using sanitized tool name
    safe_name = sanitize_tool_name(tool_name)
    filename = f'vectorized_tools/{safe_name}.npy'
    np.save(filename, embedding)

def search_similar_tool(required_tool: str, similarity_threshold: float = 0.7) -> Optional[str]:
    """
    Search for similar existing tools by comparing the required tool type with tool descriptions.
    
    Args:
        required_tool (str): The required tool identified by task analyzer
        similarity_threshold (float): Minimum similarity score to consider a match (0-1)
        
    Returns:
        Optional[str]: The tool name if a similar tool is found, None otherwise
    """
    try:
        # Get all available tools and their descriptions
        available_tools = list_available_tools()
        if not available_tools:
            return None
        
        # Load model with progress display
        model = _load_model("Loading model for similarity search")
        
        # Create embeddings for comparison
        descriptions = [tool['description'] for tool in available_tools]
        descriptions.append(required_tool)
        
        # Generate embeddings with progress display
        print("Generating embeddings...")
        with tqdm(total=100, desc="Progress", ncols=100) as pbar:
            embeddings = model.encode(descriptions)
            pbar.update(100)
        
        # Get query embedding (last one) and tool embeddings (all except last one)
        query_embedding = embeddings[-1]
        tool_embeddings = embeddings[:-1]
        
        # Calculate similarities
        similarities = cosine_similarity(
            query_embedding.reshape(1, -1),
            tool_embeddings
        )[0]
        
        # Find best match
        best_idx = np.argmax(similarities)
        best_similarity = similarities[best_idx]
        
        # Return match if above threshold
        if best_similarity >= similarity_threshold:
            return sanitize_tool_name(available_tools[best_idx]['name'])
        
        return None
        
    except Exception as e:
        print(f"Error in search_similar_tool: {str(e)}")
        return None

def list_available_tools() -> List[dict]:
    """
    List all available tools with their names and descriptions.
    
    Returns:
        List[dict]: List of dictionaries containing tool names and descriptions
    """
    tools = []
    
    if not os.path.exists('tools'):
        return tools
        
    for filename in os.listdir('tools'):
        if filename.endswith('.py'):
            tool_path = os.path.join('tools', filename)
            with open(tool_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Extract description from docstring
            doc_match = re.search(r'"""(.*?)"""', content, re.DOTALL)
            if doc_match:
                doc_content = doc_match.group(1).strip()
                # Extract tool name from docstring
                name_match = re.search(r'Tool Name: (.*?)$', doc_content, re.MULTILINE)
                tool_name = name_match.group(1) if name_match else filename[:-3]
                # Get description (everything before Tool Name)
                description = doc_content.split('Tool Name:')[0].strip()
                
                tools.append({
                    'name': tool_name,
                    'description': description,
                    'filename': filename
                })
            
    return tools
