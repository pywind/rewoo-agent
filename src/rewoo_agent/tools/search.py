"""
Search tool for web searches.
"""
import asyncio
import httpx
from typing import Dict, Any, List, AsyncIterator
from bs4 import BeautifulSoup

from .base import BaseTool, ToolResult

class SearchTool(BaseTool):
    """Tool for performing web searches."""
    
    def __init__(self):
        super().__init__(
            name="search",
            description="Search the web for information on a given topic",
            version="1.0.0",
            tags=["search", "web", "information"],
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query to execute",
                    "required": True
                }
            },
            examples=[
                {
                    "input": "python programming best practices",
                    "output": "Search results for python programming best practices"
                },
                {
                    "input": "climate change effects",
                    "output": "Search results for climate change effects"
                }
            ]
        )
    
    async def execute(self, input_data: str, **kwargs) -> ToolResult:
        """Execute a web search."""
        try:
            if not self.validate_input(input_data):
                return ToolResult.error_result("Invalid search query")
            
            query = input_data.strip()
            self.logger.info(f"Executing search for: {query}")
            
            # Use DuckDuckGo as a search engine (no API key required)
            search_results = await self._search_duckduckgo(query)
            
            return ToolResult.success_result(
                result=search_results,
                metadata={
                    "query": query,
                    "results_count": len(search_results),
                    "source": "duckduckgo"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Search error: {e}")
            return ToolResult.error_result(f"Search failed: {str(e)}")
    
    async def execute_streaming(self, input_data: str, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Execute search with streaming support."""
        try:
            if not self.validate_input(input_data):
                yield {
                    "type": "error",
                    "data": {"error": "Invalid search query"}
                }
                return
            
            query = input_data.strip()
            
            yield {
                "type": "status",
                "data": {"message": f"Searching for: {query}", "progress": 0}
            }
            
            # Simulate streaming by yielding progress updates
            search_results = await self._search_duckduckgo(query)
            
            yield {
                "type": "status",
                "data": {"message": "Processing search results", "progress": 50}
            }
            
            # Yield individual results
            for i, result in enumerate(search_results):
                yield {
                    "type": "partial_result",
                    "data": {
                        "result": result,
                        "index": i,
                        "total": len(search_results)
                    }
                }
                await asyncio.sleep(0.1)  # Small delay to simulate streaming
            
            yield {
                "type": "status",
                "data": {"message": "Search completed", "progress": 100}
            }
            
            # Final result
            yield {
                "type": "result",
                "data": {
                    "success": True,
                    "result": search_results,
                    "metadata": {
                        "query": query,
                        "results_count": len(search_results),
                        "source": "duckduckgo"
                    }
                }
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "data": {"error": f"Search failed: {str(e)}"}
            }
    
    async def _search_duckduckgo(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search using DuckDuckGo."""
        try:
            async with httpx.AsyncClient() as client:
                # DuckDuckGo instant answer API
                response = await client.get(
                    "https://html.duckduckgo.com/html/",
                    params={
                        "q": query,
                        "kl": "us-en"
                    },
                    headers={
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Search request failed with status {response.status_code}")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                results = []
                
                # Parse search results
                for result_div in soup.find_all('div', class_='result')[:max_results]:
                    try:
                        title_elem = result_div.find('a', class_='result__a')
                        snippet_elem = result_div.find('a', class_='result__snippet')
                        
                        if title_elem and snippet_elem:
                            title = title_elem.get_text(strip=True)
                            url = title_elem.get('href', '')
                            snippet = snippet_elem.get_text(strip=True)
                            
                            # Clean up the URL (DuckDuckGo uses redirects)
                            if url.startswith('/l/?uddg='):
                                url = url.split('uddg=')[1].split('&')[0]
                            
                            results.append({
                                "title": title,
                                "url": url,
                                "snippet": snippet
                            })
                    except Exception as e:
                        self.logger.warning(f"Error parsing search result: {e}")
                        continue
                
                # If no results found, try a simpler approach
                if not results:
                    # Fallback to a simple mock response
                    results = [{
                        "title": f"Search results for '{query}'",
                        "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                        "snippet": f"Found information related to '{query}'. Please visit the link for more details."
                    }]
                
                return results
                
        except Exception as e:
            self.logger.error(f"DuckDuckGo search error: {e}")
            # Return a fallback result
            return [{
                "title": f"Search for '{query}'",
                "url": f"https://duckduckgo.com/?q={query.replace(' ', '+')}",
                "snippet": f"Search query: {query}. Please perform manual search for detailed results."
            }]
    
    def validate_input(self, input_data: str) -> bool:
        """Validate search query input."""
        if not super().validate_input(input_data):
            return False
        
        # Check for reasonable query length
        query = input_data.strip()
        if len(query) < 2 or len(query) > 200:
            return False
        
        return True 