"""
Universal Application & Website Launcher

Handles launching applications and opening websites.
"""

import subprocess
import os
import webbrowser
from typing import Dict, Optional, Tuple
from backend.core.logger import logger
from backend.commands.url_resolver import url_resolver
from backend.commands.app_discovery import app_discovery
import platform


class Launcher:
    """Launches applications and websites"""
    
    def launch_website(self, url: str) -> Dict:
        """Launch a website in the default browser
        
        Args:
            url: Full URL to open
        
        Returns:
            Result dict with success, type, target, message
        """
        try:
            if not url_resolver.is_valid_url(url):
                return {
                    'success': False,
                    'type': 'website',
                    'target': url,
                    'message': 'Invalid URL format'
                }
            
            webbrowser.open(url)
            logger.info(f"Launched website: {url}")
            
            return {
                'success': True,
                'type': 'website',
                'target': url,
                'resolved_to': url,
                'message': f'Opening {url}'
            }
        except Exception as e:
            logger.error(f"Failed to launch website {url}: {e}")
            return {
                'success': False,
                'type': 'website',
                'target': url,
                'message': f'Failed to open website: {e}'
            }
    
    def resolve_and_launch_website(self, user_input: str) -> Dict:
        """Resolve website name/domain and launch it
        
        Args:
            user_input: Website name, domain, or URL
        
        Returns:
            Result dict
        """
        success, url, message = url_resolver.resolve_website(user_input)
        
        if not success:
            return {
                'success': False,
                'type': 'website',
                'target': user_input,
                'message': message
            }
        
        return self.launch_website(url)
    
    def launch_application(self, app_id: str) -> Dict:
        """Launch an application by ID
        
        Args:
            app_id: Application ID from registry
        
        Returns:
            Result dict
        """
        try:
            app_info = app_discovery.get_app_info(app_id)
            if not app_info:
                return {
                    'success': False,
                    'type': 'application',
                    'target': app_id,
                    'message': f'Application {app_id} not found'
                }
            
            # Try to find executable
            executable = app_discovery.find_app_executable(app_id)
            
            if executable:
                if platform.system() == 'Windows':
                    subprocess.Popen(executable)
                else:
                    subprocess.Popen([executable])
                
                logger.info(f"Launched application: {app_id} ({executable})")
                return {
                    'success': True,
                    'type': 'application',
                    'target': app_id,
                    'app_name': app_info.get('name', app_id),
                    'executable': executable,
                    'message': f"Opening {app_info.get('name', app_id)}"
                }
            else:
                # App is registered but executable not found
                return {
                    'success': False,
                    'type': 'application',
                    'target': app_id,
                    'app_name': app_info.get('name', app_id),
                    'message': f"{app_info.get('name', app_id)} is installed but executable could not be located"
                }
        except Exception as e:
            logger.error(f"Failed to launch application {app_id}: {e}")
            return {
                'success': False,
                'type': 'application',
                'target': app_id,
                'message': f'Failed to launch application: {e}'
            }
    
    def search_and_launch_application(self, user_input: str) -> Dict:
        """Search for an application and launch it
        
        Args:
            user_input: Application name or alias
        
        Returns:
            Result dict
        """
        success, app_id, message = app_discovery.search_app(user_input)
        
        if not success:
            return {
                'success': False,
                'type': 'application',
                'target': user_input,
                'message': message
            }
        
        return self.launch_application(app_id)
    
    def search_web(self, search_engine: str, query: str) -> Dict:
        """Search the web using a search engine
        
        Args:
            search_engine: 'google', 'youtube', etc.
            query: Search query
        
        Returns:
            Result dict
        """
        success, search_url, message = url_resolver.create_search_url(search_engine, query)
        
        if not success:
            return {
                'success': False,
                'type': 'search',
                'engine': search_engine,
                'query': query,
                'message': message
            }
        
        result = self.launch_website(search_url)
        result['type'] = 'search'
        result['engine'] = search_engine
        result['query'] = query
        return result
    
    def smart_open(self, user_input: str) -> Dict:
        """Intelligently determine what the user wants to open
        
        Returns website or app result dict
        """
        user_input = user_input.strip()
        
        # Check if it looks like a URL
        if url_resolver.is_valid_url(user_input) or url_resolver.is_valid_domain(user_input.split()[0]):
            return self.resolve_and_launch_website(user_input)
        
        # Try website resolution first (more common)
        success, _, _ = url_resolver.resolve_website(user_input)
        if success:
            return self.resolve_and_launch_website(user_input)
        
        # Try application search
        success, _, _ = app_discovery.search_app(user_input)
        if success:
            return self.search_and_launch_application(user_input)
        
        # Could not determine
        return {
            'success': False,
            'type': 'unknown',
            'target': user_input,
            'message': f"Could not identify '{user_input}' as a known website or application. Try being more specific."
        }


# Global instance
launcher = Launcher()
