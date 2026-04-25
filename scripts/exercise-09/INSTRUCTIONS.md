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

### 3. Update Prompts
Improve the analysis and target different portions of the request and response utilizing the example prompts in the _exercise-09/xss-prompts_ directory.

*Note*: This page has more than one version of an XSS vulnerability. Challenge the script to identify other flaws outside the DOM-Based XSS shown above.
