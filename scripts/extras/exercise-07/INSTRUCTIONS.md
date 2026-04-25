# Exercise 0x07 - Basic Agentic AI
## Objective
Build a Security Analysis Agent

## Instructions
### 1. Run Initial Sccript
Execute _exercise-07/basic\_agent.py_ to see the baseline basic agent behavior and output.

```sh
python exercise-07/basic_agent.py
```

The initial script focuses on the VTM (Vulnerable Task Manager) application via the vectorized database.


### 2. Add Context Retrieval
The initial prompt uses reflexion to determine whether the provided code-snippet is vulnerable to insecure direct object reference (IDOR). 

```python
instructions = """
You are an agent designed to analyze Python code for potential Insecure Direct Object Reference (IDOR) vulnerabilities.

### Analysis Process
1. Initial Review:
   - Identify where the code accesses or modifies database records
   - Locate user-supplied input that influences record access
   - Find authorization checks in the code
```

Modify the script to retrieve additional background information about the application being analyzed. 

### 3. Enhance Prompts
Provide the retrieved context to the analysis and modify prompts to discover additional issues, such as MFLAC.

```sh
python exercise-07/agentic_basic.py
```

### 4. Tune with Few-Shot
Use the few-shot prompt examples to improve accuracy and reduce false positives.
