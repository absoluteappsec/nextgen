"""
Custom Tool Template for Exercise 11a

This is a placeholder/template for students to create their own custom tool.
Replace the functionality with your own implementation.

Example use cases:
- Web search for technology documentation
- Framework/library information lookup
- Common vulnerability pattern search
- Tech stack component information
- etc.
"""

from typing import Optional, Type
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class MyCustomToolInput(BaseModel):
    """Input schema for your custom tool"""

    # TODO: Define your input parameters here
    input_param: str = Field(description="Description of what this parameter does")


class MyCustomTool(BaseTool):
    """
    TODO: Describe what your custom tool does

    Example: "Searches the web for information about technology stacks and frameworks"
    """

    name: str = "my_custom_tool"  # TODO: Give your tool a unique name
    description: str = "TODO: Describe what this tool does and when to use it"
    args_schema: Type[MyCustomToolInput] = MyCustomToolInput

    def _run(
        self,
        input_param: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """
        Execute your custom tool logic here

        Args:
            input_param: The input parameter from the schema
            run_manager: Optional callback manager

        Returns:
            str: The result of your tool execution
        """
        # TODO: Implement your tool logic here

        try:
            # Example implementation - replace with your own logic
            result = f"Custom tool executed with input: {input_param}"

            # Your actual implementation goes here
            # For example:
            # - Search the web for framework information
            # - Look up library documentation
            # - Query vulnerability databases
            # - Fetch security best practices
            # - etc.

            return result

        except Exception as e:
            return f"[Error]: Custom tool failed: {e}"


# Example: Simple Web Search Tool (placeholder - requires API key)
class WebSearchInput(BaseModel):
    """Input for web search"""

    query: str = Field(description="The search query to look up information")


class SimpleWebSearchTool(BaseTool):
    """
    Example custom tool that performs web searches to gather information
    about technologies, frameworks, or security concerns.

    NOTE: This is a placeholder. To use this tool, you would need:
    - A search API (Google Custom Search, Bing, DuckDuckGo, etc.)
    - An API key configured in your environment
    """

    name: str = "web_search"
    description: str = (
        "Searches the web for information about technologies, frameworks, or security best practices. Useful for understanding unfamiliar tech stack components."
    )
    args_schema: Type[WebSearchInput] = WebSearchInput

    def _run(
        self,
        query: str,
        run_manager: Optional[CallbackManagerForToolRun] = None,
    ) -> str:
        """Search the web for information"""

        try:
            # PLACEHOLDER: This is where you would implement actual web search
            # For example, using Google Custom Search API:
            #
            # import os
            # import requests
            # api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
            # search_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
            # url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={search_engine_id}&q={query}"
            # response = requests.get(url)
            # results = response.json()
            # return format_search_results(results)

            # For now, return a placeholder message
            return f"""[Placeholder Web Search Tool]

To enable web search functionality, you would need to:
1. Choose a search API (Google Custom Search, Bing, DuckDuckGo, etc.)
2. Obtain an API key
3. Implement the search logic in this tool

Your search query was: "{query}"

This tool could help gather information about:
- Unfamiliar frameworks or libraries found in the codebase
- Security best practices for specific technologies
- Known issues or vulnerabilities in third-party components
- Documentation about configuration patterns
"""

        except Exception as e:
            return f"[Error]: Web search failed: {e}"
