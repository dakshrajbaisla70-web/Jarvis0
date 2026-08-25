"""
Launcher API Routes

Handles website and application launching through REST API.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.commands.launcher import launcher
from backend.commands.intent_detector import intent_detector
from backend.commands.app_discovery import app_discovery
from backend.commands.url_resolver import url_resolver
from backend.core.logger import logger

router = APIRouter(prefix="/commands", tags=["commands"])


class OpenRequest(BaseModel):
    """Request to open website or app"""
    target: str
    type: Optional[str] = None  # 'website' or 'application'


class SearchRequest(BaseModel):
    """Request to search the web"""
    engine: Optional[str] = 'google'
    query: str


class ProcessCommandRequest(BaseModel):
    """Request to process natural language command"""
    input: str


@router.post("/open")
async def open_target(request: OpenRequest):
    """Open a website or application
    
    POST /commands/open
    {
        "target": "youtube",
        "type": "website"
    }
    """
    try:
        if request.type == 'website':
            result = launcher.resolve_and_launch_website(request.target)
        elif request.type == 'application':
            result = launcher.search_and_launch_application(request.target)
        else:
            result = launcher.smart_open(request.target)
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=404, detail=result['message'])
    
    except Exception as e:
        logger.error(f"Open command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/search")
async def search_web(request: SearchRequest):
    """Search the web
    
    POST /commands/search
    {
        "engine": "google",
        "query": "Python async await"
    }
    """
    try:
        result = launcher.search_web(request.engine, request.query)
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=400, detail=result['message'])
    
    except Exception as e:
        logger.error(f"Search command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/process")
async def process_command(request: ProcessCommandRequest):
    """Process natural language command
    
    POST /commands/process
    {
        "input": "open YouTube"
    }
    """
    try:
        intent, data = intent_detector.detect(request.input)
        
        if intent == 'OPEN_WEBSITE':
            result = launcher.resolve_and_launch_website(data.get('target', ''))
        elif intent == 'OPEN_APPLICATION':
            result = launcher.search_and_launch_application(data.get('target', ''))
        elif intent == 'WEB_SEARCH':
            result = launcher.search_web(
                data.get('engine', 'google'),
                data.get('query', '')
            )
        else:
            result = {
                'success': False,
                'type': 'unknown',
                'message': f'Could not process command: {request.input}'
            }
        
        result['intent'] = intent
        result['detected_data'] = data
        return result
    
    except Exception as e:
        logger.error(f"Process command failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/apps/list")
async def list_apps(limit: int = 20):
    """List available applications"""
    try:
        apps = app_discovery.list_apps(limit)
        return {
            'success': True,
            'count': len(apps),
            'apps': apps
        }
    except Exception as e:
        logger.error(f"List apps failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/websites/list")
async def list_websites():
    """List known websites"""
    try:
        websites = list(url_resolver.websites.items())
        return {
            'success': True,
            'count': len(websites),
            'websites': websites
        }
    except Exception as e:
        logger.error(f"List websites failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apps/search")
async def search_app(query: str):
    """Search for an application
    
    POST /commands/apps/search?query=vscode
    """
    try:
        success, app_id, message = app_discovery.search_app(query)
        return {
            'success': success,
            'query': query,
            'app_id': app_id,
            'message': message
        }
    except Exception as e:
        logger.error(f"App search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/websites/add")
async def add_custom_website(name: str, url: str):
    """Add a custom website
    
    POST /commands/websites/add?name=mysite&url=https://example.com
    """
    try:
        success, message = url_resolver.add_custom_website(name, url)
        return {
            'success': success,
            'message': message
        }
    except Exception as e:
        logger.error(f"Add website failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
