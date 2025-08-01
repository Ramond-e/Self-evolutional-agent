import os
from typing import Dict, List
import requests
from dotenv import load_dotenv
from urllib.parse import urlencode
import re
import json
from bs4 import BeautifulSoup

# Load environment variables
load_dotenv()

# GitHub API configuration
GITHUB_API_TOKEN = os.getenv('GITHUB_API_TOKEN')
if not GITHUB_API_TOKEN:
    raise ValueError("GITHUB_API_TOKEN environment variable is not set. Please add it to your .env file.")

GITHUB_API_BASE_URL = "https://api.github.com"

def build_github_search_url(query: str) -> str:
    """
    Builds a GitHub API search URL based on task requirements.
    
    Args:
        query (str): Search query based on task requirements
        
    Returns:
        str: GitHub API search URL
    """
    # Base search parameters
    params = {
        'q': f"{query} language:python",  # Only search Python repositories
        'sort': 'stars',  # Sort by stars to get most popular repos
        'order': 'desc',
        'per_page': 3     # Get top 3 results
    }
    
    # Build the search URL
    search_url = f"{GITHUB_API_BASE_URL}/search/repositories?{urlencode(params)}"
    return search_url

def clean_html_content(content: str) -> str:
    """
    Clean HTML content while preserving markdown formatting.
    
    Args:
        content (str): Raw HTML/markdown content
        
    Returns:
        str: Cleaned content with preserved markdown
    """
    # Use BeautifulSoup to parse HTML
    soup = BeautifulSoup(content, 'html.parser')
    
    # Remove script and style elements
    for script in soup(["script", "style"]):
        script.decompose()
    
    # Get text content
    text = soup.get_text()
    
    # First extract code blocks to preserve them
    code_blocks = []
    text_with_placeholders = text
    
    # Find all code blocks
    current_pos = 0
    while True:
        # Find start of code block
        start = text_with_placeholders.find('```', current_pos)
        if start == -1:
            break
            
        # Find end of code block
        end = text_with_placeholders.find('```', start + 3)
        if end == -1:
            break
            
        # Extract and save code block
        code_block = text_with_placeholders[start:end + 3]
        code_blocks.append(code_block)
        
        # Replace with placeholder
        placeholder = f"\nCODE_BLOCK_{len(code_blocks)-1}\n"
        text_with_placeholders = (
            text_with_placeholders[:start] +
            placeholder +
            text_with_placeholders[end + 3:]
        )
        
        # Update position
        current_pos = start + len(placeholder)
    
    # Clean up whitespace while preserving markdown
    lines = []
    in_list = False
    current_indent = 0
    
    for line in text_with_placeholders.split('\n'):
        stripped = line.strip()
        if not stripped:
            if in_list:
                lines.append('')  # Preserve empty lines in lists
            continue
            
        # Get original indentation
        indent = len(line) - len(line.lstrip())
        
        # Handle markdown elements
        if re.match(r'^#{1,6}\s', stripped):  # Headers
            lines.append(line.strip())
            in_list = False
        elif 'CODE_BLOCK_' in stripped:  # Code block placeholder
            try:
                block_num = int(stripped.strip().split('_')[-1])
                lines.append(code_blocks[block_num])
            except (ValueError, IndexError):
                # If we can't parse the block number, keep the line as is
                lines.append(stripped)
            in_list = False
        elif re.match(r'^[-*+]\s', stripped):  # Unordered list
            if not in_list:
                current_indent = indent
            in_list = True
            lines.append(' ' * (indent - current_indent) + stripped)
        elif re.match(r'^\d+\.\s', stripped):  # Ordered list
            if not in_list:
                current_indent = indent
            in_list = True
            lines.append(' ' * (indent - current_indent) + stripped)
        else:
            if in_list and indent > current_indent:  # List continuation
                lines.append(' ' * (indent - current_indent) + stripped)
            else:
                lines.append(stripped)
                in_list = False
    
    return '\n'.join(lines)

def fetch_repository_readme(repo_url: str) -> Dict[str, str]:
    """
    Fetches and processes README content for a repository.
    
    Args:
        repo_url (str): Repository API URL
        
    Returns:
        Dict with installation and usage instructions
    """
    headers = {
        'Authorization': f'token {GITHUB_API_TOKEN}',
        'Accept': 'application/vnd.github.v3.raw'
    }
    
    try:
        api_url = f"{repo_url}/readme"
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        content = response.text
        
        # Clean HTML/markdown content
        cleaned_content = clean_html_content(content)
        
        # Split content into sections
        sections = []
        current_section = []
        current_header = ""
        
        for line in cleaned_content.split('\n'):
            # Check for section headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if header_match:
                if current_section:
                    sections.append((current_header, '\n'.join(current_section)))
                current_header = header_match.group(2).lower()
                current_section = [line]
            else:
                current_section.append(line)
        
        # Add the last section
        if current_section:
            sections.append((current_header, '\n'.join(current_section)))
            
        
        # Find installation sections
        installation_content = []
        for i, (header, content) in enumerate(sections):
            header_lower = header.lower()
            if any(word in header_lower for word in ['install', 'setup', 'getting started', 'requirement', 'dependency', 'prerequisites','dependancies','docker']):
                installation_content.append(content)
        
        # Combine installation sections
        installation = '\n\n'.join(installation_content).strip() or "Installation instructions not found"
        
        # Remove non-technical sections from cleaned content
        technical_sections = []
        exclude_words = ['donate', 'sponsor', 'license', 'author', 'contributor', 'contributing']
        
        for header, content in sections:
            header_lower = header.lower()
            if not any(word in header_lower for word in exclude_words):
                technical_sections.append(content)
        
        # Return cleaned content as usage
        usage = '\n\n'.join(technical_sections).strip() or "Usage instructions not found"
        
        return {
            'installation': installation,
            'usage': usage
        }
    except requests.exceptions.RequestException:
        return {
            'installation': "Installation instructions not found",
            'usage': "Usage instructions not found"
        }

def score_tool(repo: Dict, docs: Dict, question: str, steps: List[str], search_keyword: str) -> tuple[float, str]:
    """
    Score a tool based on its stars and ability to solve the task.
    
    Args:
        repo: Repository information
        docs: Documentation (installation/usage)
        question: Original user question
        steps: Solution steps needed
        search_keyword: Tool search keyword
        
    Returns:
        float: Score from 0-100
    """
    # Get language
    language = repo.get('language', '') if repo else ''
    language = language.lower() if language else ''
    
    # Base scores
    max_stars = 10000
    star_score = min(25, (repo['stargazers_count'] / max_stars) * 25)  # Star score (0-25 points)
    
    # Documentation score (0-25 points)
    doc_score = 0
    if docs['installation'] != "Installation instructions not found":
        doc_score += 12.5
    if docs['usage'] != "Usage instructions not found":
        doc_score += 12.5
    
    # Relevance score (0-30 points)
    relevance_score = 0
    
    # Check name and description match
    name_desc = (repo['name'] + ' ' + (repo['description'] or '')).lower()
    for term in search_keyword.lower().split():
        if term in name_desc:
            relevance_score += 7.5
    
    # Check if documentation covers solution steps
    docs_text = (docs['installation'] + ' ' + docs['usage']).lower()
    for step in steps:
        step_terms = step.lower().split()
        matches = sum(1 for term in step_terms if term in docs_text)
        if matches / len(step_terms) > 0.5:  # If more than 50% of terms match
            relevance_score += 7.5
    
    # Cap relevance score at 30
    relevance_score = min(30, relevance_score)
    
    # Language score (0-30 points)
    # Only accept Python tools
    if language == 'python':
        language_score = 30
    else:
        return 0, language  # Immediately return 0 score for non-Python tools
    
    total_score = star_score + doc_score + relevance_score + language_score
    
    return total_score, language

def find_best_tool(question: str, steps: List[str], search_keyword: str) -> Dict:
    """
    Find the best tool on GitHub for a given task.
    
    Args:
        question (str): Original user question
        steps (List[str]): Steps needed to solve the task
        search_keyword (str): Keyword for tool search
        
    Returns:
        Dict: Best tool's details including name, description, installation and usage
    """
    headers = {
        'Authorization': f'token {GITHUB_API_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    search_url = build_github_search_url(search_keyword)
    
    try:
        # Get top 3 repositories
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        repos = response.json().get('items', [])[:3]
        
        if not repos:
            return {
                "name": "No suitable tool found",
                "description": "Could not find a tool matching the requirements",
                "stars": 0,
                "url": "",
                "score": 0,
                "installation": "",
                "usage": ""
            }
        
        # Score each repository
        best_score = -1
        best_tool = None
        
        for repo in repos:
            # Get documentation
            docs = fetch_repository_readme(repo['url'])
            
            # Score the tool
            score, language = score_tool(repo, docs, question, steps, search_keyword)
            
            if score > best_score:
                best_score = score
                best_tool = {
                    "name": repo['name'],
                    "description": repo['description'] or "No description available",
                    "language": language or "Unknown",
                    "stars": repo['stargazers_count'],
                    "url": repo['html_url'],
                    "score": score,
                    "installation": docs['installation'],
                    "usage": docs['usage']
                }
        
        return best_tool
        
    except requests.exceptions.RequestException as e:
        return {
            "name": "Error occurred",
            "description": f"Failed to search GitHub: {str(e)}",
            "language": "Unknown",
            "stars": 0,
            "url": "",
            "score": 0,
            "installation": "",
            "usage": ""
        }
