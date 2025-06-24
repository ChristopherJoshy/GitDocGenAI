import re
from typing import Optional

def validate_github_url(url: str) -> bool:
    """
    Validate GitHub repository URL format
    
    Args:
        url: GitHub repository URL to validate
        
    Returns:
        True if URL is valid GitHub repository URL, False otherwise
    """
    if not url:
        return False
    
    # GitHub URL patterns
    patterns = [
        # Standard HTTPS URLs
        r'^https://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+/?$',
        r'^https://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+\.git/?$',
        
        # SSH URLs  
        r'^git@github\.com:[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+\.git$',
        
        # HTTP URLs (less common)
        r'^http://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+/?$',
        r'^http://github\.com/[a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+\.git/?$'
    ]
    
    # Check against all patterns
    for pattern in patterns:
        if re.match(pattern, url.strip()):
            return True
    
    return False

def validate_api_key(api_key: str) -> bool:
    """
    Validate Gemini API key format
    
    Args:
        api_key: Gemini API key to validate
        
    Returns:
        True if API key format appears valid, False otherwise
    """
    if not api_key:
        return False
    
    # Remove whitespace
    api_key = api_key.strip()
    
    # Basic format checks for Gemini API keys
    # Gemini API keys typically start with specific prefixes and have certain length requirements
    if len(api_key) < 20:  # Too short
        return False
    
    if len(api_key) > 200:  # Too long
        return False
    
    # Check for common API key patterns
    # Gemini keys often start with "AI" followed by alphanumeric characters
    if api_key.startswith('AI') and len(api_key) >= 39:
        return True
    
    # Allow other reasonable API key formats
    # Check for alphanumeric with possible dashes/underscores
    if re.match(r'^[a-zA-Z0-9._-]+$', api_key):
        return True
    
    return False

def extract_repo_info(github_url: str) -> Optional[dict]:
    """
    Extract repository owner and name from GitHub URL
    
    Args:
        github_url: GitHub repository URL
        
    Returns:
        Dictionary with 'owner' and 'repo' keys, or None if invalid
    """
    if not validate_github_url(github_url):
        return None
    
    # Clean the URL
    url = github_url.strip().rstrip('/')
    
    # Remove .git suffix if present
    if url.endswith('.git'):
        url = url[:-4]
    
    # Extract owner and repo from various URL formats
    patterns = [
        r'github\.com[:/]([^/]+)/([^/]+)',
        r'github\.com/([^/]+)/([^/]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            owner = match.group(1)
            repo = match.group(2)
            
            return {
                'owner': owner,
                'repo': repo,
                'full_name': f"{owner}/{repo}"
            }
    
    return None

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file system operations
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for file system use
    """
    # Remove or replace problematic characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip(' .')
    
    # Ensure it's not empty
    if not sanitized:
        sanitized = 'unnamed_file'
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        max_name_len = 250 - len(ext) - 1 if ext else 254
        sanitized = name[:max_name_len] + ('.' + ext if ext else '')
    
    return sanitized
