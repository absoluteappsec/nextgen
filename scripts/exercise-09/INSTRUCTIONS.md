# Exercise 0x09 - Agentic DAST - XSS
## Objective
Utilize an AI Agent to confirm existence of XSS in a running site.

## Instructions
### 1. Run Basic Script
Open _exercise-09/agentic\_dast\_xss.py_ to observe the baseline workflow and output.

The main function specifies the target of this exercise:

```py
    url = "https://vtm.rdpt.dev/taskManager/login/"
    method = "POST"
    data = {"username": "admin", "password": "admin"}
    post_input = {
        "input": {
            "tool_input": {
                 "url": "https://vtm.rdpt.dev/taskManager/login/",
                 "method": "POST",
                 "data": {"username": "admin", "password": "admin"}
            }
        }
    }
    result = agent_executor.invoke(post_input)
    print(result)
```

As before, this script focuses on the VTM (Vulnerable Task Manager) application, but only looks at the login page. Let's see what it can find.

```sh
python exercise-09/agentic_dast_xss.py
```

### 2. Review Interactions
With debug enabled, we can see the agent behaviour that requests the page and evaluates the response.

```json
"Final Answer": {
    "URL": "https://vtm.rdpt.dev/taskManager/login/",
    "Parameters": "username=admin, password=admin",
    "XSS": "Yes",
    "Justification": "Unvalidated hash parameter used in document.write() allows arbitrary script injection"
}
```

Review the rest of the output to see how it came to the vulnerable conclusion.

### 3. Install Playwright
_exercise-09/agentic\_dast\_xss\_playwright.py_ swaps the HTTP tool for a real, visible browser so you can watch XSS payloads actually execute. If Playwright isn't installed yet in your virtual environment, install the package and its browser binary:

```sh
pip install playwright
playwright install chromium
```

### 4. Run the Playwright Script and Observe Browser Interactions
Open _exercise-09/agentic\_dast\_xss\_playwright.py_ to see how the browser-based tool works. Instead of just inspecting response text, it loads the page (or submits the POST form) in a headed Chromium browser, watches for `alert`/`confirm`/`prompt` dialogs, and takes a screenshot.

```sh
python exercise-09/agentic_dast_xss_playwright.py
```

A Chromium window will pop up and load the target page. If the injected payload fires, you'll visually see the popup appear in the browser before the tool dismisses it. Review the printed JSON result for:

```json
{
    "popup_triggered": true,
    "popups": [{"type": "alert", "message": "..."}],
    "screenshot": "exercise-09/steps/xss_....png",
    "body_snippet": "..."
}
```

Check the saved screenshot in _exercise-09/steps/_ to see the page state at the moment it was captured, and compare `popup_triggered` against the HTTP-only script's text-based analysis from steps 1/2.

### 5. Update Prompts
Improve the analysis and target different portions of the request and response utilizing the example prompts in the _exercise-09/xss-prompts_ directory.

*Note*: This page has more than one version of an XSS vulnerability. Challenge the scripts to identify other flaws outside the DOM-Based XSS shown during the initial interactions.

### 6 Authenticated Interactions
The _/taskManager/search_ page requires an authenticated session to reach, so a plain GET/POST from the browser tool will just be redirected to the login page. Update _exercise-09/agentic\_dast\_xss\_playwright.py_ so it authenticates first, then demonstrates the XSS on the search page:

1. Before navigating to the target URL, have the browser tool (or a setup step in `run_agent`/`__main__`) log in by submitting the login form at `https://vtm.rdpt.dev/taskManager/login/` with the credentials `chris:test123`, reusing the same page/browser context so the resulting session cookie is carried forward.
2. With that authenticated context still open, navigate to `https://vtm.rdpt.dev/taskManager/search/` with an XSS payload in the search parameter (e.g. `<script>alert('authenticated-xss')</script>`) and confirm the popup fires the same way it did for the unauthenticated login page.
3. Update the system prompt and example input/output so the agent knows it must authenticate before testing the search page, and adjust the `Justification` output to note that this flaw requires an authenticated session to exploit.
