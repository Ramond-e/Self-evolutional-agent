import os
import json
import time
import re
from typing import Optional, List, Dict, Set
from task_analyzer import get_model_response
from difflib import SequenceMatcher

def sanitize_tool_name(tool_name: str) -> str:
    """
    Convert tool name to a valid filename by removing special characters
    and replacing spaces with underscores.
    """
    # Remove special characters and replace spaces with underscores
    sanitized = re.sub(r'[^\w\s-]', '', tool_name)
    sanitized = re.sub(r'[-\s]+', '_', sanitized).strip('-_')
    return sanitized.lower()

def generate_tool_id(tool_name: str) -> str:
    """
    Generate a unique tool ID using tool name and timestamp.
    
    Args:
        tool_name (str): Name of the tool
        
    Returns:
        str: Tool ID in format "sanitized_name_timestamp"
    """
    sanitized_name = sanitize_tool_name(tool_name)
    timestamp = str(int(time.time()))
    return f"{sanitized_name}_{timestamp}"

def extract_keywords(text: str) -> Set[str]:
    """
    Extract keywords from text by removing common words and keeping meaningful terms.
    
    Args:
        text (str): Input text
        
    Returns:
        Set[str]: Set of keywords
    """
    # Comprehensive list of stop words in both English and Chinese contexts
    stop_words = {
        # English stop words
        'the', 'is', 'at', 'which', 'on', 'and', 'a', 'an', 'as', 'are', 
        'been', 'by', 'for', 'from', 'has', 'had', 'have', 'in', 'of', 
        'or', 'that', 'to', 'was', 'will', 'with', 'get', 'fetch', 'retrieve',
        'data', 'information', 'using', 'use', 'via', 'through', 'tool',
        'any', 'all', 'can', 'could', 'would', 'should', 'may', 'might',
        'must', 'shall', 'will', 'would', 'do', 'does', 'did', 'done',
        'be', 'being', 'been', 'am', 'is', 'are', 'was', 'were',
        'this', 'that', 'these', 'those', 'it', 'its', 'their', 'them',
        'we', 'us', 'our', 'you', 'your', 'he', 'him', 'his', 'she', 'her',
        'they', 'me', 'my', 'i', 'not', 'no', 'nor', 'but', 'only',
        'just', 'very', 'too', 'also', 'more', 'most', 'much', 'many',
        'some', 'few', 'all', 'any', 'each', 'every', 'either', 'neither',
        'one', 'two', 'first', 'second', 'third', 'last', 'next',
        'new', 'old', 'good', 'bad', 'great', 'small', 'large', 'big',
        'high', 'low', 'same', 'different', 'such', 'so', 'than', 'then',
        'if', 'else', 'when', 'where', 'what', 'who', 'why', 'how',
        'because', 'since', 'while', 'after', 'before', 'during',
        'about', 'above', 'below', 'between', 'into', 'out', 'up', 'down',
        'main', 'def', 'self', 'none', 'true', 'false', 'try', 'except',
        'import', 'return', 'pass', 'break', 'continue', 'class', 'function',
        'specified', 'specific', 'general', 'generic', 'common', 'simple',
        'available', 'current', 'latest', 'recent', 'update', 'check'
    }
    
    # Programming-specific stop words
    programming_stop_words = {
        'def', 'import', 'from', 'class', 'return', 'if', 'else', 'try', 
        'except', 'raise', 'finally', 'with', 'as', 'pass', 'break', 
        'continue', 'while', 'for', 'in', 'and', 'or', 'not', 'is', 
        'none', 'true', 'false', 'self', '__init__', '__main__', 'main',
        'print', 'input', 'output', 'file', 'open', 'close', 'read', 'write',
        'str', 'int', 'float', 'list', 'dict', 'set', 'tuple', 'object',
        'args', 'kwargs', 'param', 'parameter', 'result', 'value', 'item',
        'error', 'exception', 'warning', 'debug', 'info', 'log'
    }
    
    # Combine all stop words
    all_stop_words = stop_words | programming_stop_words
    
    # Convert to lowercase and extract words (including Chinese characters)
    # Also handle camelCase and snake_case
    words = []
    
    # Handle snake_case
    text = text.replace('_', ' ')
    
    # Handle camelCase
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    
    # Extract words (including Chinese characters)
    # Handle Chinese text specially
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    english_pattern = re.compile(r'\b[a-zA-Z]+\b')
    
    # Extract Chinese words/phrases
    chinese_words = chinese_pattern.findall(text)
    english_words = english_pattern.findall(text.lower())
    
    # Process Chinese text - common patterns
    chinese_keywords = set()
    for chinese_text in chinese_words:
        # Add the whole phrase
        chinese_keywords.add(chinese_text)
        
        # Common Chinese keyword patterns
        if '天气' in chinese_text:
            chinese_keywords.update(['天气', 'weather', 'temperature', 'forecast'])
        if '股票' in chinese_text:
            chinese_keywords.update(['股票', 'stock', 'price', 'market'])
        if '价格' in chinese_text:
            chinese_keywords.update(['价格', 'price', 'cost', 'value'])
        if '查询' in chinese_text or '查看' in chinese_text:
            chinese_keywords.update(['查询', '查看', 'check', 'query', 'search'])
        if '获取' in chinese_text:
            chinese_keywords.update(['获取', 'get', 'fetch', 'retrieve'])
        if '北京' in chinese_text:
            chinese_keywords.update(['北京', 'beijing'])
        if '上海' in chinese_text:
            chinese_keywords.update(['上海', 'shanghai'])
        if '苹果' in chinese_text:
            chinese_keywords.update(['苹果', 'apple', 'aapl'])
        if '公司' in chinese_text:
            chinese_keywords.update(['公司', 'company', 'corporation'])
    
    # Combine English and Chinese processing
    raw_words = english_words
    
    # Filter words
    keywords = set()
    for word in raw_words:
        # Skip if it's a stop word
        if word in all_stop_words:
            continue
            
        # Skip if too short (but allow Chinese characters which might be single)
        if len(word) < 3 and not re.match(r'[\u4e00-\u9fff]', word):
            continue
            
        # Skip if it's all numbers
        if word.isdigit():
            continue
            
        keywords.add(word)
    
    # Extract meaningful domain-specific keywords
    domain_keywords = set()
    
    # Weather-related
    weather_terms = {'weather', 'temperature', 'forecast', 'climate', 'rain', 
                     'snow', 'sunny', 'cloudy', 'wind', 'humidity', 'pressure'}
    
    # Stock/Finance-related  
    finance_terms = {'stock', 'price', 'market', 'trading', 'finance', 'ticker',
                     'quote', 'share', 'investment', 'portfolio', 'dividend',
                     'earnings', 'revenue', 'profit', 'loss', 'nasdaq', 'nyse'}
    
    # API/Service-related
    api_terms = {'api', 'endpoint', 'request', 'response', 'authentication',
                 'token', 'key', 'client', 'server', 'rest', 'graphql', 'sdk'}
    
    # Check for domain terms
    text_lower = text.lower()
    for term_set in [weather_terms, finance_terms, api_terms]:
        for term in term_set:
            if term in text_lower and term not in all_stop_words:
                domain_keywords.add(term)
    
    # Add location names if detected (common cities)
    common_locations = {'beijing', 'shanghai', 'london', 'newyork', 'tokyo',
                       'paris', 'sydney', 'toronto', 'singapore', 'hongkong'}
    
    for location in common_locations:
        if location in text_lower:
            domain_keywords.add(location)
    
    # Add company names if detected
    tech_companies = {'apple', 'google', 'microsoft', 'amazon', 'tesla',
                      'nvidia', 'meta', 'netflix', 'intel', 'amd'}
    
    for company in tech_companies:
        if company in text_lower:
            domain_keywords.add(company)
    
    # Combine all keywords (including Chinese)
    final_keywords = keywords | domain_keywords | chinese_keywords
    
    # Remove any remaining low-quality keywords
    final_keywords = {k for k in final_keywords if k not in {'any', 'all', 'main', 'self', 'none', 'retrieves', 'fetches'}}
    
    return final_keywords

def generate_tool_keywords(tool_name: str, tool_description: str, required_tool: str, code: str) -> str:
    """
    Generate comprehensive keywords for tool search matching.
    Focus on user-friendly search terms and common variations.
    
    Args:
        tool_name (str): Name of the tool
        tool_description (str): Description of the tool
        required_tool (str): The required tool type from task analyzer
        code (str): The tool's code
        
    Returns:
        str: Space-separated keywords optimized for search
    """
    # Start with basic keyword extraction
    name_keywords = extract_keywords(tool_name)
    desc_keywords = extract_keywords(tool_description)
    req_keywords = extract_keywords(required_tool)
    
    # Initialize comprehensive keyword set
    all_keywords = name_keywords | desc_keywords | req_keywords
    
    # Add common search variations and synonyms
    search_variations = {
        # Weather related
        'weather': ['weather', 'temperature', 'forecast', 'climate', 'condition', 
                   'humidity', 'wind', 'rain', 'sunny', 'cloudy', '天气', '温度', '预报'],
        'temperature': ['temperature', 'temp', 'degree', 'celsius', 'fahrenheit', '温度'],
        'forecast': ['forecast', 'prediction', 'outlook', '预报'],
        
        # Stock/Finance related
        'stock': ['stock', 'share', 'equity', 'ticker', 'symbol', '股票', '股价'],
        'price': ['price', 'cost', 'value', 'quote', 'rate', '价格', '价值'],
        'market': ['market', 'trading', 'exchange', 'nasdaq', 'nyse', '市场', '交易'],
        'finance': ['finance', 'financial', 'investment', 'money', '金融', '财务'],
        
        # Company related
        'company': ['company', 'corporation', 'business', 'firm', '公司', '企业'],
        'apple': ['apple', 'aapl', '苹果'],
        'nvidia': ['nvidia', 'nvda', '英伟达'],
        'tesla': ['tesla', 'tsla', '特斯拉'],
        'microsoft': ['microsoft', 'msft', '微软'],
        
        # Location related
        'beijing': ['beijing', 'peking', '北京'],
        'shanghai': ['shanghai', '上海'],
        'newyork': ['newyork', 'nyc', '纽约'],
        'london': ['london', '伦敦'],
        'tokyo': ['tokyo', '东京'],
        
        # Action related
        'get': ['get', 'fetch', 'retrieve', 'obtain', 'acquire', '获取', '查询'],
        'check': ['check', 'view', 'see', 'look', 'query', '查看', '查询'],
        'download': ['download', 'save', 'fetch', '下载'],
        'search': ['search', 'find', 'lookup', 'query', '搜索', '查找'],
        
        # Time related
        'current': ['current', 'now', 'today', 'latest', 'recent', '当前', '今天', '最新'],
        'realtime': ['realtime', 'live', 'instant', 'immediate', '实时'],
        
        # Data related
        'data': ['data', 'info', 'information', 'details', '数据', '信息'],
        'api': ['api', 'interface', 'service', 'endpoint', '接口'],
        
        # Video/Media related
        'video': ['video', 'movie', 'clip', 'media', '视频'],
        'youtube': ['youtube', 'yt', 'video', '油管'],
        
        # News related
        'news': ['news', 'article', 'report', 'headline', '新闻', '资讯']
    }
    
    # Analyze description and code to add relevant variations
    text_to_analyze = f"{tool_name} {tool_description} {required_tool} {code}".lower()
    
    for base_term, variations in search_variations.items():
        if base_term in text_to_analyze:
            all_keywords.update(variations)
    
    # Extract from code - focus on meaningful terms
    code_lower = code.lower()
    
    # Find imported libraries
    import_pattern = re.compile(r'import\s+(\w+)|from\s+(\w+)', re.IGNORECASE)
    for match in import_pattern.findall(code):
        for lib in match:
            if lib and len(lib) > 2:
                all_keywords.add(lib.lower())
    
    # Find API domains
    url_pattern = re.compile(r'https?://(?:www\.)?([^/\s]+)')
    for url in url_pattern.findall(code):
        domain = url.split('.')[0]
        if len(domain) > 2 and domain not in ['api', 'www']:
            all_keywords.add(domain)
    
    # Add specific identifiers based on code patterns
    if 'weather' in code_lower or 'temperature' in code_lower:
        all_keywords.update(['weather', 'temperature', 'forecast', 'climate'])
    if 'stock' in code_lower or 'ticker' in code_lower:
        all_keywords.update(['stock', 'price', 'market', 'trading', 'finance'])
    if 'youtube' in code_lower or 'video' in code_lower:
        all_keywords.update(['youtube', 'video', 'download', 'media'])
    
    # Remove low-quality keywords
    filtered_keywords = set()
    exclude_words = {
        'any', 'all', 'main', 'self', 'none', 'true', 'false', 
        'def', 'class', 'import', 'return', 'print', 'input',
        'str', 'int', 'float', 'dict', 'list', 'set', 'tuple',
        'args', 'kwargs', 'param', 'value', 'item', 'object'
    }
    
    for keyword in all_keywords:
        if keyword not in exclude_words and len(keyword) >= 2:
            filtered_keywords.add(keyword)
    
    # Sort by relevance (longer terms are usually more specific)
    sorted_keywords = sorted(filtered_keywords)
    
    # Return up to 50 keywords for better search coverage
    return ' '.join(sorted_keywords[:50])

def save_tool_as_json(
    tool_name: str,
    tool_description: str,
    keywords: str,
    install_dependencies: List[str],
    python_code: str
) -> str:
    """
    Save tool information as JSON file in the tools directory.
    
    Args:
        tool_name (str): Name of the tool
        tool_description (str): Description of the tool's functionality
        keywords (str): Space-separated keywords for searching
        install_dependencies (List[str]): List of installation commands
        python_code (str): The tool's Python code
        
    Returns:
        str: The tool ID used for the file
    """
    # Create tools directory if it doesn't exist
    if not os.path.exists('tools'):
        os.makedirs('tools')
    
    # Generate tool ID
    tool_id = generate_tool_id(tool_name)
    
    # Create tool data structure
    tool_data = {
        "id": tool_id,
        "tool_description": tool_description,
        "keywords": keywords,
        "install_dependencies": install_dependencies,
        "python_code": python_code,
        "created_at": time.time(),
        "original_name": tool_name
    }
    
    # Save as JSON only (removed .py file generation)
    filename = f'tools/{tool_id}.json'
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(tool_data, f, ensure_ascii=False, indent=2)
    
    return tool_id

def search_tool_by_keywords(required_tool: str, task_keywords: Set[str] = None) -> Optional[Dict]:
    """
    Enhanced search for existing tools using flexible keyword matching.
    
    Args:
        required_tool (str): The required tool description from task analyzer
        task_keywords (Set[str]): Additional keywords from the task
        
    Returns:
        Optional[Dict]: Tool data if found, None otherwise
    """
    if not os.path.exists('tools'):
        return None
    
    # Extract and expand search keywords
    search_keywords = extract_keywords(required_tool)
    if task_keywords:
        search_keywords = search_keywords | task_keywords
    
    # Expand search keywords with common variations
    expanded_keywords = search_keywords.copy()
    keyword_expansions = {
        'weather': ['temperature', 'forecast', 'climate'],
        'stock': ['price', 'market', 'finance', 'trading'],
        'download': ['fetch', 'get', 'retrieve'],
        'beijing': ['北京', 'weather'],
        'nvidia': ['nvda', 'stock', 'price'],
        'apple': ['aapl', 'stock', 'price'],
        'financial': ['finance', 'earnings', 'revenue']
    }
    
    for keyword in search_keywords:
        if keyword in keyword_expansions:
            expanded_keywords.update(keyword_expansions[keyword])
    
    best_match = None
    best_score = 0
    
    # Debug print
    print(f"🔍 Searching with keywords: {', '.join(sorted(expanded_keywords))}")
    
    # Search through JSON files
    for filename in os.listdir('tools'):
        if filename.endswith('.json'):
            filepath = os.path.join('tools', filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    tool_data = json.load(f)
                
                # Extract tool keywords
                tool_keywords = set(tool_data.get('keywords', '').split())
                tool_desc_lower = tool_data.get('tool_description', '').lower()
                tool_name_lower = tool_data.get('original_name', '').lower()
                
                # Calculate different matching scores
                # 1. Direct keyword matching
                matching_keywords = expanded_keywords & tool_keywords
                keyword_score = len(matching_keywords) / len(expanded_keywords) if expanded_keywords else 0
                
                # 2. Check if search terms appear in tool description
                desc_matches = sum(1 for kw in expanded_keywords if kw in tool_desc_lower)
                desc_score = desc_matches / len(expanded_keywords) if expanded_keywords else 0
                
                # 3. Check if search terms appear in tool name
                name_matches = sum(1 for kw in expanded_keywords if kw in tool_name_lower)
                name_score = name_matches / len(expanded_keywords) if expanded_keywords else 0
                
                # 4. Partial matching for compound words
                partial_matches = 0
                for search_kw in expanded_keywords:
                    for tool_kw in tool_keywords:
                        if len(search_kw) >= 4 and len(tool_kw) >= 4:
                            if search_kw in tool_kw or tool_kw in search_kw:
                                partial_matches += 0.5
                                break
                partial_score = partial_matches / len(expanded_keywords) if expanded_keywords else 0
                
                # 5. Domain-specific boosting
                domain_boost = 0
                if 'weather' in expanded_keywords and 'weather' in tool_keywords:
                    domain_boost = 0.3
                elif 'stock' in expanded_keywords and any(kw in tool_keywords for kw in ['stock', 'finance', 'market']):
                    domain_boost = 0.3
                
                # Calculate total score with weights
                total_score = (
                    keyword_score * 0.4 +      # Direct keyword match (40%)
                    desc_score * 0.2 +         # Description contains keywords (20%)
                    name_score * 0.1 +         # Name contains keywords (10%)
                    partial_score * 0.2 +      # Partial matches (20%)
                    domain_boost               # Domain-specific boost (bonus)
                )
                
                # Bonus for very relevant tools
                req_tool_lower = required_tool.lower()
                if any(term in req_tool_lower for term in ['weather', 'temperature']) and 'weather' in tool_keywords:
                    total_score += 0.3
                elif any(term in req_tool_lower for term in ['stock', 'price', 'finance']) and any(kw in tool_keywords for kw in ['stock', 'finance']):
                    total_score += 0.3
                
                # Debug print for high-scoring tools
                if total_score > 0.2:
                    print(f"  Tool: {tool_data.get('original_name')} - Score: {total_score:.2f}")
                    print(f"    Matching keywords: {', '.join(matching_keywords)}")
                
                if total_score > best_score:
                    best_score = total_score
                    best_match = tool_data
                    best_match['match_score'] = total_score
                    best_match['matching_keywords'] = list(matching_keywords)
                    best_match['score_breakdown'] = {
                        'keyword_score': keyword_score,
                        'desc_score': desc_score,
                        'name_score': name_score,
                        'partial_score': partial_score,
                        'domain_boost': domain_boost
                    }
            
            except Exception as e:
                print(f"Error reading tool file {filename}: {e}")
                continue
    
    # Lower threshold for better matching
    if best_match and best_score >= 0.2:  # Lowered from 0.3 to 0.2
        print(f"✅ Best match: {best_match['original_name']} (score: {best_score:.2f})")
        return best_match
    
    print("❌ No matching tool found")
    return None

def list_available_tools_v2() -> List[Dict]:
    """
    List all available tools from JSON files.
    
    Returns:
        List[Dict]: List of tool information dictionaries
    """
    tools = []
    
    if not os.path.exists('tools'):
        return tools
    
    for filename in os.listdir('tools'):
        if filename.endswith('.json'):
            filepath = os.path.join('tools', filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    tool_data = json.load(f)
                    tools.append({
                        'id': tool_data.get('id'),
                        'name': tool_data.get('original_name', tool_data.get('id')),
                        'description': tool_data.get('tool_description'),
                        'keywords': tool_data.get('keywords'),
                        'filename': filename
                    })
            except Exception as e:
                print(f"Error reading tool file {filename}: {e}")
                continue
    
    return tools

def load_tool_by_id(tool_id: str) -> Optional[Dict]:
    """
    Load tool data by its ID.
    
    Args:
        tool_id (str): The tool ID
        
    Returns:
        Optional[Dict]: Tool data if found, None otherwise
    """
    filename = f'tools/{tool_id}.json'
    if os.path.exists(filename):
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading tool {tool_id}: {e}")
    
    return None

def generate_code_description_v2(
    user_question: str, 
    required_tool: str, 
    code: str, 
    tool_name: str, 
    tool_general_description: str
) -> str:
    """
    Generate a concise description of the tool's functionality.
    
    Args:
        user_question (str): The original user question
        required_tool (str): The required tool identified by task analyzer
        code (str): The generated code
        tool_name (str): Name of the tool
        tool_general_description (str): General description of what the tool should do
        
    Returns:
        str: A concise tool description
    """
    prompt = f"""
    Generate a CONCISE and GENERIC description (max 80 characters) for this tool.
    The description should explain what the tool does in general terms, NOT specific to any example.
    
    Tool Purpose: {tool_general_description}
    Tool Type: {required_tool}
    Tool Name: {tool_name}
    
    Guidelines:
    - Be generic and reusable
    - Focus on the tool's primary function
    - Use active voice (e.g., "Fetches stock prices", "Retrieves weather data")
    - Do NOT mention specific examples or use cases
    - Keep it under 80 characters
    
    Examples of good descriptions:
    - "Fetches real-time stock market data and financial information"
    - "Retrieves current weather conditions and forecasts for any location"
    - "Searches and downloads YouTube videos based on keywords"
    
    Return ONLY the description text, nothing else.
    """
    
    description = get_model_response(prompt).strip()
    
    # Ensure it's not too long
    if len(description) > 100:
        description = description[:97] + "..."
    
    return description
