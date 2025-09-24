"""
Wikipedia tool for retrieving information from Wikipedia.
"""
import httpx
from typing import Dict, Any, List, AsyncIterator

from .base import BaseTool, ToolResult



class WikipediaTool(BaseTool):
    """Tool for searching and retrieving information from Wikipedia."""
    
    def __init__(self):
        super().__init__(
            name="wikipedia",
            description="Search Wikipedia and retrieve article summaries",
            version="1.0.0",
            tags=["search", "encyclopedia", "information", "knowledge"],
            parameters={
                "query": {
                    "type": "string",
                    "description": "The search query for Wikipedia",
                    "required": True
                },
                "sentences": {
                    "type": "integer",
                    "description": "Number of sentences to return (default: 3)",
                    "required": False,
                    "default": 3
                }
            },
            examples=[
                {
                    "input": "Python programming language",
                    "output": "Python is a high-level, interpreted programming language..."
                },
                {
                    "input": "Machine learning",
                    "output": "Machine learning is a subset of artificial intelligence..."
                }
            ]
        )
    
    async def execute(self, input_data: str, **kwargs) -> ToolResult:
        """Execute a Wikipedia search."""
        try:
            if not self.validate_input(input_data):
                return ToolResult.error_result("Invalid Wikipedia query")
            
            query = input_data.strip()
            sentences = kwargs.get('sentences', 3)
            
            self.logger.info(f"Searching Wikipedia for: {query}")
            
            # Search for articles
            search_results = await self._search_wikipedia(query)
            
            if not search_results:
                return ToolResult.error_result(f"No Wikipedia articles found for: {query}")
            
            # Get summary of the first result
            article_title = search_results[0]
            summary = await self._get_wikipedia_summary(article_title, sentences)
            
            return ToolResult.success_result(
                result={
                    "title": article_title,
                    "summary": summary,
                    "search_results": search_results[:5],  # Top 5 results
                    "url": f"https://en.wikipedia.org/wiki/{article_title.replace(' ', '_')}"
                },
                metadata={
                    "query": query,
                    "sentences": sentences,
                    "results_count": len(search_results)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Wikipedia search error: {e}")
            return ToolResult.error_result(f"Wikipedia search failed: {str(e)}")
    
    async def execute_streaming(self, input_data: str, **kwargs) -> AsyncIterator[Dict[str, Any]]:
        """Execute Wikipedia search with streaming support."""
        try:
            if not self.validate_input(input_data):
                yield {
                    "type": "error",
                    "data": {"error": "Invalid Wikipedia query"}
                }
                return
            
            query = input_data.strip()
            sentences = kwargs.get('sentences', 3)
            
            yield {
                "type": "status",
                "data": {"message": f"Searching Wikipedia for: {query}", "progress": 25}
            }
            
            # Search for articles
            search_results = await self._search_wikipedia(query)
            
            if not search_results:
                yield {
                    "type": "error",
                    "data": {"error": f"No Wikipedia articles found for: {query}"}
                }
                return
            
            yield {
                "type": "status",
                "data": {"message": f"Found {len(search_results)} results", "progress": 50}
            }
            
            # Get summary of the first result
            article_title = search_results[0]
            
            yield {
                "type": "status",
                "data": {"message": f"Retrieving summary for: {article_title}", "progress": 75}
            }
            
            summary = await self._get_wikipedia_summary(article_title, sentences)
            
            yield {
                "type": "status",
                "data": {"message": "Wikipedia search completed", "progress": 100}
            }
            
            # Final result
            yield {
                "type": "result",
                "data": {
                    "success": True,
                    "result": {
                        "title": article_title,
                        "summary": summary,
                        "search_results": search_results[:5],
                        "url": f"https://en.wikipedia.org/wiki/{article_title.replace(' ', '_')}"
                    },
                    "metadata": {
                        "query": query,
                        "sentences": sentences,
                        "results_count": len(search_results)
                    }
                }
            }
            
        except Exception as e:
            yield {
                "type": "error",
                "data": {"error": f"Wikipedia search failed: {str(e)}"}
            }
    
    async def _search_wikipedia(self, query: str, limit: int = 10) -> List[str]:
        """Search Wikipedia for articles matching the query."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "format": "json",
                        "list": "search",
                        "srsearch": query,
                        "srlimit": limit
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Wikipedia API request failed with status {response.status_code}")
                
                data = response.json()
                
                if 'query' not in data or 'search' not in data['query']:
                    return []
                
                return [result['title'] for result in data['query']['search']]
                
        except Exception as e:
            self.logger.error(f"Wikipedia search API error: {e}")
            return []
    
    async def _get_wikipedia_summary(self, title: str, sentences: int = 3) -> str:
        """Get a summary of a Wikipedia article."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://en.wikipedia.org/w/api.php",
                    params={
                        "action": "query",
                        "format": "json",
                        "titles": title,
                        "prop": "extracts",
                        "exintro": True,
                        "explaintext": True,
                        "exsentences": sentences
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    raise Exception(f"Wikipedia API request failed with status {response.status_code}")
                
                data = response.json()
                
                if 'query' not in data or 'pages' not in data['query']:
                    return f"Could not retrieve summary for: {title}"
                
                pages = data['query']['pages']
                page_id = list(pages.keys())[0]
                
                if page_id == '-1':
                    return f"No Wikipedia article found for: {title}"
                
                page = pages[page_id]
                
                if 'extract' not in page:
                    return f"No summary available for: {title}"
                
                return page['extract']
                
        except Exception as e:
            self.logger.error(f"Wikipedia summary API error: {e}")
            return f"Error retrieving summary for: {title}"
    
    def validate_input(self, input_data: str) -> bool:
        """Validate Wikipedia query input."""
        if not super().validate_input(input_data):
            return False
        
        query = input_data.strip()
        
        # Check for reasonable query length
        if len(query) < 2 or len(query) > 200:
            return False
        
        return True 