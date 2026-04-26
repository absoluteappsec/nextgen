"""
URL fetching tool for DeepAgent demonstration.
Intentionally vulnerable to SSRF for educational purposes.
"""

import subprocess
from typing import Optional, Type
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class FetchURLInput(BaseModel):
    url: str = Field(description="The URL to fetch")


class FetchURLTool(BaseTool):
    name: str = "fetch_url"
    description: str = "Fetches the content of a URL using curl and returns the response body."
    args_schema: Type[FetchURLInput] = FetchURLInput

    def _run(
        self, url: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        try:
            result = subprocess.run(
                ["curl", "-s", "-L", "--max-time", "10", url],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if result.returncode != 0:
                return f"[Error]: curl failed (exit {result.returncode}): {result.stderr[:500]}"

            body = result.stdout
            if len(body) > 50_000:
                body = body[:50_000] + "\n\n[Truncated — response exceeded 50KB]"

            return f"URL: {url}\n\nResponse:\n{body}"

        except subprocess.TimeoutExpired:
            return f"[Error]: Request timed out after 15 seconds for URL: {url}"
        except Exception as e:
            return f"[Error]: Failed to fetch URL '{url}': {e}"
