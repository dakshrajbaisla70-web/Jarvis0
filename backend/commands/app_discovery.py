"""
Windows Application Discovery

Scans system for installed applications and creates an index.
"""

import json
import os
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from difflib import get_close_matches
from backend.core.logger import logger
import platform


class AppDiscovery:
    """Discovers and manages installed Windows applications"""
    
    def __init__(self):
        self.apps_registry = self._load_registry()
        self.discovered_apps = {}
        self.discover_apps()
    
    def _load_registry(self) -> Dict:
        """Load app registry from config"""
        try:
            config_path = Path('config/apps.json')
            if config_path.exists():
                with open(config_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load apps.json: {e}")
        return {}
    
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return platform.system() == 'Windows'
    
    def discover_apps(self) -> None:
        """Discover installed applications"""
        if not self.is_windows():
            logger.info("App discovery only supported on Windows")
            return
        
        # Scan from registry entries
        self._scan_registry()
        
        # Scan common program directories
        self._scan_program_files()
        
        # Add configured apps
        self._add_configured_apps()
        
        logger.info(f"Discovered {len(self.discovered_apps)} applications")
    
    def _scan_registry(self) -> None:
        """Scan Windows registry for installed apps"""
        try:
            reg_paths = [
                r'HKEY_LOCAL_MACHINE\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall',
                r'HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall'
            ]
            
            for reg_path in reg_paths:
                try:
                    output = subprocess.check_output(
                        ['reg', 'query', reg_path, '/s'],
                        stderr=subprocess.DEVNULL,
                        universal_newlines=True
                    )
                    
                    for line in output.split('\n'):
                        if 'DisplayName' in line:
                            match = re.search(r'DisplayName\\s+REG_SZ\\s+(.+)', line)
                            if match:
                                app_name = match.group(1).strip()
                                if app_name and len(app_name) < 100:
                                    self.discovered_apps[app_name.lower()] = {
                                        'name': app_name,
                                        'source': 'registry',
                                        'path': None
                                    }
                except:
                    pass
        except Exception as e:
            logger.warning(f"Registry scan failed: {e}")
    
    def _scan_program_files(self) -> None:
        """Scan Program Files directories"""
        if not self.is_windows():
            return
        
        scan_dirs = [
            Path(os.environ.get('PROGRAMFILES', 'C:\\\\Program Files')),
            Path(os.environ.get('PROGRAMFILES(X86)', 'C:\\\\Program Files (x86)')),
        ]
        
        for scan_dir in scan_dirs:
            if not scan_dir.exists():
                continue
            
            try:
                for item in scan_dir.iterdir():
                    if item.is_dir() and len(item.name) < 100:
                        app_id = item.name.lower().replace(' ', '_')
                        if app_id not in self.discovered_apps:
                            self.discovered_apps[app_id] = {
                                'name': item.name,
                                'source': 'filesystem',
                                'path': str(item)
                            }
            except PermissionError:
                pass
            except Exception as e:
                logger.warning(f"Could not scan {scan_dir}: {e}")
    
    def _add_configured_apps(self) -> None:
        """Add apps from configuration"""
        for app_id, app_info in self.apps_registry.items():
            app_key = app_id.lower()
            if app_key not in self.discovered_apps:
                self.discovered_apps[app_key] = app_info
    
    def find_app_executable(self, app_id: str) -> Optional[str]:
        """Find executable path for an app
        
        Returns:
            Path to executable if found, None otherwise
        """
        if app_id not in self.apps_registry:
            return None
        
        app_info = self.apps_registry[app_id]
        paths = app_info.get('paths', [])
        
        for path_template in paths:
            # Expand environment variables
            path_str = os.path.expandvars(path_template)
            path_str = path_str.replace('{user}', os.environ.get('USERNAME', ''))
            
            # Handle wildcards
            if '*' in path_str:
                pattern = path_str.split('*')[0]
                try:
                    parent = Path(pattern).parent
                    if parent.exists():
                        for item in parent.glob('*' + path_str.split('*')[1]):
                            if item.exists() and item.is_file():
                                return str(item)
                except:
                    pass
            else:
                path_obj = Path(path_str)
                if path_obj.exists() and path_obj.is_file():
                    return path_str
        
        return None
    
    def search_app(self, query: str) -> Tuple[bool, Optional[str], str]:
        """Search for an app by name or alias
        
        Returns:
            (success: bool, app_id: Optional[str], message: str)
        """
        query_lower = query.lower().strip()
        
        # Exact match in registry
        for app_id, app_info in self.apps_registry.items():
            if query_lower == app_id.lower():
                return True, app_id, f"Found: {app_info.get('name', app_id)}"
            
            # Check aliases
            aliases = app_info.get('aliases', [])
            if query_lower in [a.lower() for a in aliases]:
                return True, app_id, f"Found: {app_info.get('name', app_id)}"
        
        # Fuzzy match
        app_ids = list(self.apps_registry.keys())
        matches = get_close_matches(query_lower, app_ids, n=3, cutoff=0.6)
        
        if matches:
            if len(matches) == 1:
                return True, matches[0], f"Found: {self.apps_registry[matches[0]].get('name')}"
            else:
                options = '\n'.join([f"• {self.apps_registry[m].get('name', m)}" for m in matches])
                return False, None, f"Multiple matches found:\n{options}\nWhich one?"
        
        # Check in discovered apps
        discovered_matches = get_close_matches(query_lower, list(self.discovered_apps.keys()), n=1, cutoff=0.7)
        if discovered_matches:
            return True, discovered_matches[0], f"Found: {self.discovered_apps[discovered_matches[0]].get('name')}"
        
        return False, None, f"Application '{query}' not found on this system."
    
    def get_app_info(self, app_id: str) -> Optional[Dict]:
        """Get information about an app
        
        Returns:
            App info dict or None if not found
        """
        if app_id in self.apps_registry:
            return self.apps_registry[app_id]
        if app_id in self.discovered_apps:
            return self.discovered_apps[app_id]
        return None
    
    def list_apps(self, limit: int = 20) -> List[Dict]:
        """List available applications
        
        Args:
            limit: Max number of apps to return
        
        Returns:
            List of app info dicts
        """
        apps = []
        for app_id, app_info in list(self.apps_registry.items())[:limit]:
            apps.append({
                'id': app_id,
                'name': app_info.get('name', app_id),
                'aliases': app_info.get('aliases', [])
            })
        return apps


# Global instance
app_discovery = AppDiscovery()
