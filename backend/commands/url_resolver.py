"""
URL and Website Resolution

Handles opening websites, searching, and URL validation.
"""

import json
import re
import urllib.parse
from pathlib import Path
from typing import Dict, Optional, Tuple
from backend.core.logger import logger


class URLResolver:
    """Resolves and validates URLs for safe browsing"""
    
    def __init__(self):
        self.websites = self._load_websites()
        self.safe_protocols = ['http://', 'https://']
        self.unsafe_protocols = ['javascript:', 'file://', 'data:', 'vbscript:']
    
    def _load_websites(self) -> Dict[str, str]:
        """Load website registry from config"""
        try:
            config_path = Path('config/websites.json')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load websites.json: {e}")
        return {}
    
    def normalize_input(self, text: str) -> str:
        """Normalize user input for matching"""
        return text.lower().strip()
    
    def is_valid_domain(self, text: str) -> bool:
        """Check if text looks like a domain name"""
        domain_pattern = r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$'
        return bool(re.match(domain_pattern, text))
    
    def is_valid_url(self, url: str) -> bool:
        """Validate URL format and protocol"""
        try:
            # Check for dangerous protocols
            url_lower = url.lower()
            for unsafe in self.unsafe_protocols:
                if url_lower.startswith(unsafe):
                    return False
            
            # Check for valid protocol
            if not any(url_lower.startswith(safe) for safe in self.safe_protocols):
                return False
            
            # Basic URL validation
            result = urllib.parse.urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def resolve_website(self, user_input: str) -> Tuple[bool, Optional[str], str]:
        """Resolve website name or URL to HTTPS domain
        
        Returns:
            (success: bool, resolved_url: Optional[str], message: str)
        """
        normalized = self.normalize_input(user_input)
        
        # Check if it's already a valid URL
        if self.is_valid_url(user_input):
            return True, user_input, f"Opening URL: {user_input}"
        
        # Check if it's in the website registry
        if normalized in self.websites:
            url = self.websites[normalized]
            return True, url, f"Opening {normalized.capitalize()}"
        
        # Check if it looks like a domain (example.com)
        if self.is_valid_domain(normalized):
            url = f"https://{normalized}"
            return True, url, f"Opening {normalized}"
        
        # Check for partial matches in registry
        for key, value in self.websites.items():
            if normalized in key or key in normalized:
                return True, value, f"Opening {key.capitalize()}"
        
        # Could not resolve
        return False, None, f"Could not identify '{user_input}' as a known website. Please provide a domain name (e.g., example.com) or choose from: {', '.join(list(self.websites.keys())[:10])}..."
    
    def create_search_url(self, search_engine: str, query: str) -> Tuple[bool, Optional[str], str]:
        """Create a search URL
        
        Args:
            search_engine: 'google', 'youtube', 'reddit', etc.
            query: Search query string
        
        Returns:
            (success: bool, search_url: Optional[str], message: str)
        """
        search_engines = {
            'google': 'https://www.google.com/search?q=',
            'youtube': 'https://www.youtube.com/results?search_query=',
            'reddit': 'https://www.reddit.com/search?q=',
            'github': 'https://github.com/search?q=',
            'wikipedia': 'https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch=',
            'stackoverflow': 'https://stackoverflow.com/search?q='
        }
        
        engine_normalized = self.normalize_input(search_engine)
        
        if engine_normalized not in search_engines:
            return False, None, f"Search engine '{search_engine}' not supported. Supported: {', '.join(search_engines.keys())}"
        
        if not query or not query.strip():
            return False, None, "Search query cannot be empty"
        
        base_url = search_engines[engine_normalized]
        encoded_query = urllib.parse.quote(query.strip())
        search_url = base_url + encoded_query
        
        return True, search_url, f"Searching {search_engine} for '{query}'"
    
    def add_custom_website(self, name: str, url: str) -> Tuple[bool, str]:
        """Add a custom website to the registry
        
        Returns:
            (success: bool, message: str)
        """
        if not self.is_valid_url(url):
            return False, f"Invalid URL: {url}. Must start with http:// or https://"
        
        name_normalized = self.normalize_input(name)
        self.websites[name_normalized] = url
        
        try:
            config_path = Path('config/websites.json')
            config_path.parent.mkdir(exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.websites, f, indent=2)
            return True, f"Saved custom website: {name} -> {url}"
        except Exception as e:
            logger.error(f"Could not save custom website: {e}")
            return False, f"Could not save website (error: {e})"


# Global instance
url_resolver = URLResolver()
