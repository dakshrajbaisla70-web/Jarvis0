"""
Command Intent Detection

Detects user intent from natural language input.
"""

import re
from typing import Tuple, Dict, Any
from backend.core.logger import logger


class IntentDetector:
    """Detects user intent from input"""
    
    # Intent patterns
    PATTERNS = {
        'OPEN_WEBSITE': [
            r'open\\s+([\\w.\\-]+)',
            r'([\\w.\\-]+)\\s+khol(?:o|a)?',
            r'([\\w.\\-]+)\\s+ko\\s+khol',
            r'browse\\s+([\\w.\\-]+)',
            r'visit\\s+([\\w.\\-]+)',
            r'go\\s+to\\s+([\\w.\\-]+)',
            r'launch\\s+([\\w.\\-]+)\\s+in\\s+browser'
        ],
        'OPEN_APPLICATION': [
            r'open\\s+([\\w\\s]+)(?:\\s+application)?',
            r'launch\\s+([\\w\\s]+)',
            r'start\\s+([\\w\\s]+)',
            r'([\\w\\s]+)\\s+(?:chalao|kholo|launch)',
            r'run\\s+([\\w\\s]+)'
        ],
        'WEB_SEARCH': [
            r'search\\s+([\\w]+)\\s+(?:for|pe)\\s+(.+)',
            r'([\\w]+)\\s+pe\\s+search\\s+karo\\s+(.+)',
            r'google\\s+(?:pe|mein)\\s+search\\s+karo\\s+(.+)',
            r'search\\s+(.+)',
            r'find\\s+(.+)',
            r'look\\s+(?:for|up)\\s+(.+)'
        ],
        'SYSTEM_COMMAND': [
            r'(?:what|what\\'s|whats)\\s+(?:the\\s+)?time',
            r'(?:what|what\\'s|whats)\\s+(?:the\\s+)?date',
            r'tell\\s+me\\s+(?:the\\s+)?(?:time|date)',
            r'system\\s+status',
            r'check\\s+system',
            r'run\\s+diagnostics'
        ],
        'MEMORY_COMMAND': [
            r'remember\\s+(.+)',
            r'store\\s+(.+)',
            r'save\\s+(?:this|that)(?:\\s+to\\s+memory)?',
            r'what\\s+(?:do\\s+)?you\\s+remember',
            r'show\\s+(?:my\\s+)?memories',
            r'recall'
        ],
        'HELP': [
            r'help',
            r'(?:what|what\\'s)\\s+(?:your\\s+)?(?:capabilities|features|commands)',
            r'how\\s+(?:can\\s+)?(?:you|i)\\s+(?:help|assist)',
            r'what\\s+can\\s+(?:you|i)\\s+do'
        ]
    }
    
    def detect(self, user_input: str) -> Tuple[str, Dict[str, Any]]:
        """Detect user intent from input
        
        Args:
            user_input: Raw user input text
        
        Returns:
            (intent_type: str, extracted_data: Dict)
        """
        user_input = user_input.strip().lower()
        
        for intent, patterns in self.PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    groups = match.groups()
                    return intent, self._extract_data(intent, groups, user_input)
        
        # Default to chat
        return 'CHAT', {'message': user_input}
    
    def _extract_data(self, intent: str, groups: tuple, full_input: str) -> Dict[str, Any]:
        """Extract relevant data based on intent"""
        data = {}
        
        if intent == 'OPEN_WEBSITE' and groups:
            data['target'] = groups[0].strip()
        
        elif intent == 'OPEN_APPLICATION' and groups:
            data['target'] = groups[0].strip()
        
        elif intent == 'WEB_SEARCH':
            if len(groups) >= 2:
                data['engine'] = groups[0].strip() if groups[0] else 'google'
                data['query'] = groups[1].strip()
            elif len(groups) >= 1:
                data['engine'] = 'google'
                data['query'] = groups[0].strip()
        
        elif intent == 'MEMORY_COMMAND' and groups:
            data['content'] = groups[0].strip()
        
        data['full_input'] = full_input
        return data


# Global instance
intent_detector = IntentDetector()
