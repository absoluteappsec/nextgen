# Exercise 0x06 - Deterministic Code Review
## Objective
Use few-shot prompting to improve the accuracy when searching for specific vulnerability types (e.g. SQL Injection, XSS) 

## Instructions
### 1. Select Repository
Open _exercise-06/sca\_deterministic\_few\_shot.py_ and find the code repository specification.

The initial script focuses on the VTM (Vulnerable Task Manager) application. You can either target this application since it has known issues or pick another open source project. 

```py
repo_url = 'https://github.com/redpointsec/vtm.git'
local_path = 'exercise-06/repo'
```

### 2. Run the Script
The initial example looks for SQL Injection. Run the script and note the output.

```sh
python exercise-06/sca_deterministic_few_shot.py
```

### 2. Choose another Vulnerability Type
Select a vulnerability type or category and modify the few-shot examples, questions, and prompts accordingly.

Note that the prompt provides context along with the examples.

```py
system_prompt_template = """
You are a helpful secure code review assistant who is given acess to a
code base stored in vector format. You will be asked questions about that code.
Please provide helpful and accurate responses to the best of your ability.

</context>
{context}
</context>

<background>
 Django's ORM methods automatically handle SQL escaping
 in order to prevent SQL Injection attacks. Unsafe SQL
 queries can only be run with the following functions:
 `.raw()`, `.execute()`, `.extra()`.
</background>
"""
```

### 3. Compare Approaches
Try the script a few different times, with and without few-shot prompts, different vulnerability types, etc. Keep adding examples until you see a difference in results. Note that results degrade with more examples.
