# Exercise 0x15 - AIxCode Review - Authorization Functions

## Objective
Instead of identifying authorization decorators or functions manually, utilize AI to both gather and summarize this information based on limited available resources.

## Instructions
### 1. Basic Example
For this exercise, we will be running the included script to review vectorized code from the Vulnerable Task Manager (VTM) application.

Start by opening the _exercise-12/list\authz\_decorators.py_ script and looking at the retrieval mechanism and prompt.

Run the script

```sh
python exercise-15/list_authz_decorators.py
```

Based on the current prompt, note the response.

```
Based on my review of the provided code snippets, I didn't find explicit usage of Django authorization decorators like @login_required or @permission_required in the visible code. However, I noticed some interesting authentication configurations:
```

### 2. Update Script/Prompt
Utilize your prompt engineering experienc to tune both the prompt and any other parameters in the file to identify actual authorization decorators.