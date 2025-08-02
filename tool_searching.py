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

def build_github_search_url(query: str, search_type: str = "repositories", search_strategy: int = 1) -> str:
    """
    Builds a GitHub API search URL based on task requirements.
    
    Args:
        query (str): Search query based on task requirements
        search_type (str): Type of search (repositories or code)
        search_strategy (int): Which search strategy to use (1-4)
        
    Returns:
        str: GitHub API search URL
    """
    # Different search strategies - all generic, no hardcoding
    if search_strategy == 1:
        # Strategy 1: Simple direct search
        search_query = f"{query} language:python"
    elif search_strategy == 2:
        # Strategy 2: Focus on API/integration tools
        search_query = f"{query} (API OR sdk OR client OR wrapper OR library) language:python"
    elif search_strategy == 3:
        # Strategy 3: Search popular projects with good documentation
        search_query = f"{query} language:python stars:>100 good-first-issues:>0"
    else:
        # Strategy 4: Search for official or well-maintained tools
        # Use multiple quality indicators without hardcoding names
        search_query = f'{query} language:python (official OR certified OR "well maintained" OR popular) stars:>200'
    
    # Base search parameters
    params = {
        'q': search_query,
        'sort': 'stars',
        'order': 'desc',
        'per_page': 15  # Get more results for better selection
    }
    
    # Build the search URL
    search_url = f"{GITHUB_API_BASE_URL}/search/{search_type}?{urlencode(params)}"
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
        tuple: (score, language)
    """
    # Get language
    language = repo.get('language', '') if repo else ''
    language = language.lower() if language else ''
    
    # Only accept Python tools
    if language != 'python':
        return 0, language
    
    # Base scores - Adjusted to give more weight to popular repos
    max_stars = 5000  # Lowered threshold for better scoring
    star_score = min(20, (repo['stargazers_count'] / max_stars) * 20)  # Star score (0-20 points)
    
    # Documentation score (0-20 points)
    doc_score = 0
    if docs['installation'] != "Installation instructions not found":
        doc_score += 10
    if docs['usage'] != "Usage instructions not found":
        doc_score += 10
    
    # Quality indicators bonus (0-20 points)
    quality_bonus = 0
    name_desc = (repo['name'] + ' ' + (repo['description'] or '')).lower()
    docs_text = (docs['installation'] + ' ' + docs['usage']).lower()
    
    # Check for API/SDK indicators (suggests it's a proper API wrapper)
    api_indicators = [
        'api', 'sdk', 'client', 'wrapper', 'official', 
        'endpoint', 'request', 'response', 'restful', 'rest api', 'library'
    ]
    api_indicator_count = sum(1 for indicator in api_indicators if indicator in name_desc or indicator in docs_text)
    quality_bonus += min(8, api_indicator_count * 2)
    
    # Check for proper package structure indicators
    package_indicators = [
        'pip install', 'python -m pip', 'setup.py', 'pypi', 
        'requirements', 'import', 'from', 'package'
    ]
    package_count = sum(1 for indicator in package_indicators if indicator in docs_text)
    quality_bonus += min(3, package_count)
    
    # Check for authentication mentions (indicates proper API integration)
    auth_patterns = [
        'api_key', 'api key', 'apikey', 'api-key', 'token', 
        'authentication', 'auth', 'credentials', 'secret', 'bearer'
    ]
    if any(pattern in docs_text for pattern in auth_patterns):
        quality_bonus += 3
    
    # Check for data quality indicators
    data_quality_patterns = [
        'real-time', 'realtime', 'live', 'current', 'latest',
        'accurate', 'reliable', 'official', 'verified', 'up-to-date'
    ]
    if any(pattern in docs_text for pattern in data_quality_patterns):
        quality_bonus += 3
    
    # Check for good documentation practices
    doc_quality_indicators = [
        'example', 'usage', 'quick start', 'getting started',
        'response format', 'parameters', 'tutorial', 'guide'
    ]
    doc_indicator_count = sum(1 for indicator in doc_quality_indicators if indicator in docs_text)
    quality_bonus += min(3, doc_indicator_count)
    
    quality_bonus = min(20, quality_bonus)
    
    # Relevance score (0-20 points)
    relevance_score = 0
    
    # Enhanced keyword matching
    keywords = search_keyword.lower().split()
    
    # Check repo name and description
    for keyword in keywords:
        if keyword in name_desc:
            relevance_score += 5
    
    # Check documentation content
    for step in steps:
        if any(keyword in step.lower() for keyword in keywords):
            relevance_score += 3
    
    relevance_score = min(20, relevance_score)
    
    # Freshness score (0-20 points) - recently updated repos are better
    freshness_score = 0
    if repo.get('updated_at'):
        from datetime import datetime
        try:
            updated = datetime.strptime(repo['updated_at'], '%Y-%m-%dT%H:%M:%SZ')
            days_old = (datetime.now() - updated).days
            if days_old < 30:
                freshness_score = 20
            elif days_old < 90:
                freshness_score = 15
            elif days_old < 180:
                freshness_score = 10
            elif days_old < 365:
                freshness_score = 5
        except:
            pass
    
    total_score = star_score + doc_score + quality_bonus + relevance_score + freshness_score
    
    # Debug logging
    repo_name = repo.get('full_name', repo.get('name', 'Unknown'))
    print(f"\nScoring {repo_name}:")
    print(f"  Stars: {star_score:.1f}/20")
    print(f"  Docs: {doc_score}/20")
    print(f"  Quality: {quality_bonus}/20")
    print(f"  Relevance: {relevance_score}/20")
    print(f"  Freshness: {freshness_score}/20")
    print(f"  Total: {total_score:.1f}/100")
    
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
    # Use the new function to get multiple tools and return the best one
    tools = find_best_tools_with_exclusion(question, steps, search_keyword, excluded_tools=set(), max_tools=1)
    
    if tools:
        return tools[0]
    else:
        return {
            "name": "No suitable tool found",
            "description": "Could not find a tool matching the requirements",
            "stars": 0,
            "url": "",
            "score": 0,
            "installation": "",
            "usage": ""
        }

def find_best_tool_original(question: str, steps: List[str], search_keyword: str) -> Dict:
    """
    Original implementation of find_best_tool kept for reference.
    """
    headers = {
        'Authorization': f'token {GITHUB_API_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print(f"\n🔍 Searching GitHub for: {search_keyword}")
    
    # Try multiple search strategies
    search_strategies = [
        # Strategy 1: Simple direct search
        build_github_search_url(search_keyword, search_strategy=1),
        # Strategy 2: Add API/SDK terms
        build_github_search_url(search_keyword, search_strategy=2),
        # Strategy 3: Search in description and readme
        build_github_search_url(search_keyword, search_strategy=3),
        # Strategy 4: Search for well-known API names
        build_github_search_url(search_keyword, search_strategy=4)
    ]
    
    all_repos = []
    seen_repos = set()
    
    for strategy_idx, search_url in enumerate(search_strategies):
        try:
            print(f"\n📡 Search strategy {strategy_idx + 1}...")
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                if response.headers['X-RateLimit-Remaining'] == '0':
                    print("⚠️ GitHub API rate limit reached. Using cached results.")
                    break
            
            if response.status_code != 200:
                print(f"⚠️ Strategy {strategy_idx + 1} returned status: {response.status_code}")
                continue
                
            data = response.json()
            repos = data.get('items', [])
            print(f"   Found {len(repos)} repositories")
            
            # Add unique repos
            for repo in repos:
                repo_id = repo.get('id')
                if repo_id and repo_id not in seen_repos:
                    seen_repos.add(repo_id)
                    all_repos.append(repo)
                    print(f"   Added: {repo['full_name']} ⭐ {repo['stargazers_count']}")
            
            print(f"   Total unique repos so far: {len(all_repos)}")
            
            # Stop if we have enough repos
            if len(all_repos) >= 10:
                break
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Search strategy {strategy_idx + 1} failed: {str(e)}")
            continue
    
    if not all_repos:
        return {
            "name": "No suitable tool found",
            "description": "Could not find a tool matching the requirements",
            "stars": 0,
            "url": "",
            "score": 0,
            "installation": "",
            "usage": ""
        }
    
    print(f"\n📊 Evaluating {len(all_repos)} repositories...")
    
    # Score each repository
    best_score = -1
    best_tool = None
    evaluated = 0
    
    for repo in all_repos[:15]:  # Evaluate top 15 repos
        # Skip if repo has very few stars (likely not reliable)
        if repo['stargazers_count'] < 5:  # Lowered from 10 to 5
            continue
            
        evaluated += 1
        print(f"\n🔍 Evaluating: {repo['full_name']} ⭐ {repo['stargazers_count']}")
        
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
    
    print(f"\n✅ Best tool selected: {best_tool['name'] if best_tool else 'None'} (score: {best_score:.1f})")
    
    return best_tool if best_tool else {
        "name": "No suitable tool found",
        "description": "Could not find a tool matching the requirements",
        "stars": 0,
        "url": "",
        "score": 0,
        "installation": "",
        "usage": ""
    }

def find_best_tools_with_exclusion(question: str, steps: List[str], search_keyword: str, excluded_tools: set = None, max_tools: int = 3) -> List[Dict]:
    """
    Find multiple tools on GitHub for a given task, with support for excluding already tried tools.
    
    Args:
        question (str): Original user question
        steps (List[str]): Steps needed to solve the task
        search_keyword (str): Keyword for tool search
        excluded_tools (set): Set of tool names to exclude from results
        max_tools (int): Maximum number of tools to return
        
    Returns:
        List[Dict]: List of tools with details including name, description, installation and usage
    """
    if excluded_tools is None:
        excluded_tools = set()
    
    headers = {
        'Authorization': f'token {GITHUB_API_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    print(f"\n🔍 Searching GitHub for: {search_keyword}")
    if excluded_tools:
        print(f"   Excluding: {', '.join(excluded_tools)}")
    
    # Try multiple search strategies
    search_strategies = [
        # Strategy 1: Simple direct search
        build_github_search_url(search_keyword, search_strategy=1),
        # Strategy 2: Add API/SDK terms
        build_github_search_url(search_keyword, search_strategy=2),
        # Strategy 3: Search in description and readme
        build_github_search_url(search_keyword, search_strategy=3),
        # Strategy 4: Search for well-known API names
        build_github_search_url(search_keyword, search_strategy=4)
    ]
    
    all_repos = []
    seen_repos = set()
    
    for strategy_idx, search_url in enumerate(search_strategies):
        try:
            print(f"\n📡 Search strategy {strategy_idx + 1}...")
            response = requests.get(search_url, headers=headers)
            
            if response.status_code == 403 and 'X-RateLimit-Remaining' in response.headers:
                if response.headers['X-RateLimit-Remaining'] == '0':
                    print("⚠️ GitHub API rate limit reached. Using cached results.")
                    break
            
            if response.status_code != 200:
                print(f"⚠️ Strategy {strategy_idx + 1} returned status: {response.status_code}")
                continue
                
            data = response.json()
            repos = data.get('items', [])
            print(f"   Found {len(repos)} repositories")
            
            # Add unique repos that aren't excluded
            for repo in repos:
                repo_id = repo.get('id')
                repo_name = repo.get('name', '')
                
                # Skip if excluded
                if repo_name in excluded_tools:
                    continue
                    
                if repo_id and repo_id not in seen_repos:
                    seen_repos.add(repo_id)
                    all_repos.append(repo)
                    print(f"   Added: {repo['full_name']} ⭐ {repo['stargazers_count']}")
            
            print(f"   Total unique repos so far: {len(all_repos)}")
            
            # Stop if we have enough repos
            if len(all_repos) >= max_tools * 3:  # Get 3x to have options after scoring
                break
                
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Search strategy {strategy_idx + 1} failed: {str(e)}")
            continue
    
    if not all_repos:
        return []
    
    print(f"\n📊 Evaluating {len(all_repos)} repositories...")
    
    # Score and rank all repositories
    scored_tools = []
    evaluated = 0
    
    for repo in all_repos[:20]:  # Evaluate top 20 repos
        # Skip if repo has very few stars (likely not reliable)
        if repo['stargazers_count'] < 5:
            continue
            
        evaluated += 1
        print(f"\n🔍 Evaluating: {repo['full_name']} ⭐ {repo['stargazers_count']}")
        
        # Get documentation
        docs = fetch_repository_readme(repo['url'])
        
        # Score the tool
        score, language = score_tool(repo, docs, question, steps, search_keyword)
        
        if score > 0:  # Only include tools with positive scores
            tool_info = {
                "name": repo['name'],
                "description": repo['description'] or "No description available",
                "language": language or "Unknown",
                "stars": repo['stargazers_count'],
                "url": repo['html_url'],
                "score": score,
                "installation": docs['installation'],
                "usage": docs['usage']
            }
            scored_tools.append(tool_info)
    
    # Sort by score and return top N
    scored_tools.sort(key=lambda x: x['score'], reverse=True)
    top_tools = scored_tools[:max_tools]
    
    print(f"\n✅ Found {len(top_tools)} suitable tools")
    
    return top_tools
