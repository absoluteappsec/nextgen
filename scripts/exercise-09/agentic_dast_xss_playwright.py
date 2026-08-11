from deepagents import create_deep_agent
from langchain_aws import ChatBedrockConverse
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from typing import Optional, Type
from langchain_core.callbacks.manager import CallbackManagerForToolRun
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from pathlib import Path
import html
import json
import time
import urllib.parse

load_dotenv()

SCREENSHOT_DIR = Path(__file__).parent / "steps"
SCREENSHOT_DIR.mkdir(exist_ok=True)


class BrowserInput(BaseModel):
    req: str = Field(description="data to send with the request, example: {'url': 'http://example.com/path', 'method': 'GET', 'data': {}}")


class BrowserTool(BaseTool):
    name: str = "browser_tool"
    description: str = (
        "Useful for when you need to load a url in a real browser to check for XSS. "
        "Renders the response and executes any JavaScript in it, so a triggered "
        "alert()/confirm()/prompt() popup confirms the payload actually fired. "
        "Can be used for GET and POST requests."
    )
    args_schema: Type[BrowserInput] = BrowserInput

    def _run(
        self, req: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        data = json.loads(req)
        url = data["url"]
        method = data.get("method", "GET").upper()
        params = data.get("data") or {}
        print(f"Loading {method} {url} in browser with data: {params if params else 'N/A'}")

        dialogs = []

        def handle_dialog(dialog):
            dialogs.append({"type": dialog.type, "message": dialog.message})
            print(f"XSS popup triggered! [{dialog.type}] {dialog.message}")
            # Pause briefly so the popup is visible in the browser window before it is dismissed.
            time.sleep(2)
            dialog.accept()

        screenshot_path = None
        body = ""
        status = None

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False, slow_mo=250)
                page = browser.new_page()
                page.on("dialog", handle_dialog)

                try:
                    if method == "POST":
                        # Navigate the browser to a real HTML form that POSTs to the target
                        # so the server response is rendered (and any XSS payload executes)
                        # exactly as it would for a victim submitting the form.
                        inputs = "".join(
                            f'<input type="hidden" name="{html.escape(str(k))}" value="{html.escape(str(v))}">'
                            for k, v in params.items()
                        )
                        form_html = (
                            f'<html><body><form id="xss-form" method="POST" action="{html.escape(url)}">'
                            f"{inputs}</form>"
                            "<script>document.getElementById('xss-form').submit();</script>"
                            "</body></html>"
                        )
                        page.set_content(form_html)
                        page.wait_for_load_state("networkidle", timeout=15000)
                    else:
                        query = urllib.parse.urlencode(params)
                        full_url = f"{url}?{query}" if query else url
                        response = page.goto(full_url, wait_until="networkidle", timeout=15000)
                        status = response.status if response else None

                    page.wait_for_timeout(1000)
                    body = page.content()
                except Exception as nav_error:
                    body = f"Navigation error: {nav_error}"

                screenshot_path = str(SCREENSHOT_DIR / f"xss_{int(time.time() * 1000)}.png")
                page.screenshot(path=screenshot_path, full_page=True)
                browser.close()
        except Exception as e:
            return f"Browser request failed: {str(e)}"

        result = {
            "url": url,
            "method": method,
            "status_code": status,
            "popup_triggered": bool(dialogs),
            "popups": dialogs,
            "screenshot": screenshot_path,
            "body_snippet": body[:3000],
        }
        return json.dumps(result)

    async def _arun(
        self, req: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("browser_tool does not support async")


# Define tools and LLM
tools = [BrowserTool()]
llm = ChatBedrockConverse(
    #model_id="us.anthropic.claude-haiku-4-5-20251001-v1:0",
    model_id="qwen.qwen3-coder-30b-a3b-v1:0",
    temperature=0.6,
)

# System prompt - clean, no ReAct boilerplate
system_prompt = """You are an agent designed to check whether a page is vulnerable to cross-site scripting by loading it in a real browser and observing whether an alert/confirm/prompt popup actually fires, using a multi-step reasoning process.

### Analysis Process
1. **Initial Request**: Load the provided URL in the browser using the specified method (GET or POST).
2. **XSS Analysis**: Inspect the page and interactions for possible XSS locations, send crafted payloads to confirm whether or not its vulnerable.
3. **Response Analysis**: Inspect the tool result for:
   - popup_triggered / popups: whether a JavaScript dialog actually fired (the strongest evidence of XSS)
   - body_snippet: (str) the rendered page body, to spot reflected/unescaped payloads even if no popup fired
   - screenshot: path to a screenshot of the page at the time it was rendered
4. **Final Response**: Return the relevant information from the browser request.

You have access to a browser tool that loads a URL in a real, visible browser and executes its JavaScript. It can handle both GET and POST requests, and will report any popup dialog that fires as a result of an injected payload.

### Output Format
Your final response must include:
- URL: (str) The URL of the request
- Parameters: (str) The parameters sent with the request
- XSS: (str) Any identified XSS vulnerabilities (Yes or No)
- Justification: (str) A brief justification ONLY if XSS is confirmed, noting whether it was confirmed via a triggered popup or via reflected payload in the response body
"""

# Create DeepAgent
agent = create_deep_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt,
)


def run_agent(url: str) -> dict:
    """
    Analyze the given URL using the agent and return the result.
    """
    response = agent.invoke({
        "messages": [{"role": "user", "content": url}]
    })
    return response


if __name__ == "__main__":
    # Example input for POST request
    url = "https://vtm.rdpt.dev/taskManager/login/"
    method = "POST"
    data = {"username": "admin", "password": "admin"}
    post_input = f"Test this endpoint for XSS: URL={url}, Method={method}, Data={data}"

    result = agent.invoke({
        "messages": [{"role": "user", "content": post_input}]
    })
    print(result["messages"][-1].content)
