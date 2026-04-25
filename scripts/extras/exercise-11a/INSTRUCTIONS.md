# Exercise 0x11a - Security Assessment Information Gathering
## Objective
Build an agent that autonomously gathers structured information about an application for security assessment planning, focusing on Behavior, Tech Stack, and Brainstorming of potential risks.

## Instructions
### 1. Run Demo Script
Open _exercise-11a/langgraph_react_demo.py_ to observe the baseline information gathering workflow.

The script clones the BHIMA application (hospital management system) and uses ReAct agents with file/directory viewing tools to explore the codebase and collect structured information.

```sh
python exercise-11a/langgraph_react_demo.py
```

The agent will:
- Clone the BHIMA repository into `./repo/`
- Explore the directory structure
- Read documentation, configuration files, and code
- Collect information in three key areas

### 2. Review the Information Gathering Template
The agent follows a structured information gathering approach based on the security assessment template with three sections:

```python
instructions = """
Your goal is to collect information in three key areas:

## 1. Behavior
- What does it do? (business purpose)
- Who does it do this for? (internal / external customer base)
- What kind of information will it hold?
- What are the different types of roles?
- What aspects concern client/customer/staff the most?

## 2. Tech Stack
- Framework & Language
- 3rd party components
- Datastores

## 3. Brainstorming / Risks
- Potential failure modes
- Technology-specific risks (e.g., "ORM might have SQLi risks")
- General security concerns to explore later
"""
```

### 3. Improve Information Collection
Modify the prompt to enhance the depth and accuracy of information gathering. Consider:
- What additional questions would help understand the application better?
- How can the agent identify all technology components more thoroughly?
- What brainstorming questions lead to better risk identification?

Focus on **information gathering**, not vulnerability scanning. The goal is reconnaissance and context building.

### 4. Enhance Output Format
Improve the JSON output structure to make it more useful for security assessment planning.

Current output format:
```python
"""
### **Output Format**
Your final response must be in JSON format with these fields:
- `behavior`: (object) What the app does, users, data types, roles, concerns
- `tech_stack`: (object) Frameworks, 3rd party components, datastores identified
- `brainstorming`: (array) List of potential risk areas and concerns to explore
"""
```

Consider adding:
- More detailed subsections within each area
- Priority or severity indicators for brainstormed risks
- References to specific files or locations in the codebase
- Categorization of tech stack components by layer (frontend, backend, database, etc.)

### 5. Add Custom Tools (Optional)
Build a custom tool to enhance information gathering capabilities. Review _custom_tool_template.py_ for examples.

Example custom tools:
- Web search for technology documentation or security best practices
- Package dependency analyzer to identify all third-party components
- Configuration file parser to extract tech stack information
- Documentation summarizer

To add a custom tool:
```python
# Import your tool
from custom_tool_template import SimpleWebSearchTool

# Add to tools list
tools = [
    ViewFileTool(),
    ViewFileLinesTool(),
    DirectoryListingTool(),
    FileListingTool(),
    DirectoryStructureTool(),
    SimpleWebSearchTool(),  # Your custom tool
]
```

### 6. Test with Different Applications (Optional)
Modify the repository URL to analyze different applications and compare information gathering results.

```python
# Change the target repository
repo_url = "https://github.com/your-org/your-app.git"
```

Consider trying:
- Different technology stacks (Rails, Node.js, Go, etc.)
- Different application types (API, web app, microservices)
- Different complexity levels (small vs large codebases)

## Key Concepts
- **Information Gathering vs Vulnerability Scanning**: This exercise focuses on reconnaissance and context building, not finding specific vulnerabilities
- **Structured Assessment**: Following the Behavior/Tech Stack/Brainstorming template ensures comprehensive coverage
- **Brainstorming**: The third section should list potential concerns to explore (e.g., "authentication might need review"), not confirmed vulnerabilities
- **Real-World Application**: BHIMA is a hospital management system with medical records and financial data, requiring careful security consideration

## Files
- `langgraph_react_demo.py` - Main script with ReAct agent
- `view_file_tools.py` - File viewing tools
- `view_directory_tools.py` - Directory listing tools
- `custom_tool_template.py` - Template for custom tools (includes web search example)
